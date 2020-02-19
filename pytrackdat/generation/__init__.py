# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2020 the PyTrackDat authors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact information:
#     David Lougheed (david.lougheed@gmail.com)

import csv
import getpass
import gzip
import importlib
import io
import os
import pprint
import re
import shutil
import subprocess
import sys

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import IO, List, Optional, Union

from ..common import *
from .constants import *

from . import constants
from . import errors
from . import formatters
from . import utils


__all__ = [
    "constants",
    "errors",
    "formatters",
    "utils",
    "get_default_from_csv_with_type",
    "design_to_relations",
    "create_admin",
    "create_models",
    "create_api",
    "print_usage",
    "sanitize_and_check_site_name",
    "is_common_password",
    "main"
]


def parse_dt_integer(dv: str):
    return int(re.sub(RE_NUMBER_GROUP_SEPARATOR, "", dv.strip()))


def parse_dt_float(dv: str):
    return float(re.sub(RE_NUMBER_GROUP_SEPARATOR, "", dv.lower().strip()))


def parse_dt_decimal(dv: str):
    return Decimal(re.sub(RE_NUMBER_GROUP_SEPARATOR, "", dv.lower().strip()))


def parse_dt_date(dv: str, field_name: str):
    # TODO: adjust format based on heuristics
    # TODO: Allow extra column setting with date format from python docs?

    dt_interpretations = tuple(datetime.strptime(dv.strip(), df) for dr, df in DATE_FORMATS)
    if len(dt_interpretations) == 0:
        # TODO: Warning
        print("Warning: Value '{}' the date-typed field '{}' does not match any PyTrackDat-compatible "
              "formats.".format(dv.strip(), field_name))
        return None

    if re.match(RE_DATE_DMY_D, dv.strip()) or re.match(RE_DATE_DMY_S, dv.strip()):
        print("Warning: Assuming d{sep}m{sep}Y date format for ambiguously-formatted date field '{field}'.".format(
            sep="-" if "-" in dv.strip() else "/", field=field_name))

    return dt_interpretations[0]


def parse_dt_time(dv: str):
    # TODO: adjust format based on MORE heuristics
    # TODO: Allow extra column setting with time format from python docs?
    return datetime.strptime(dv.strip(), "%H:%M" if len(dv.strip().split(":")) == 2 else "%H:%M:%S")


def parse_dt_boolean(dv: str, _field_name: str, nullable: bool, null_values: tuple) -> Optional[bool]:
    if nullable and ((len(null_values) != 0 and dv.strip() in null_values) or (dv.strip() == "")):
        return None

    return dv.strip().lower() in BOOLEAN_TRUE_VALUES


# TODO: GIS default parsers
DATA_TYPE_STRING_PARSERS = {
    DT_INTEGER: parse_dt_integer,
    DT_FLOAT: parse_dt_float,
    DT_DECIMAL: parse_dt_decimal,
    DT_DATE: parse_dt_date,
    DT_TIME: parse_dt_time,
    DT_BOOLEAN: parse_dt_boolean,
}


def get_default_from_csv_with_type(field_name: str, dv: str, dt: str, nullable: bool = False, null_values: tuple = ()) \
        -> Union[None, int, float, Decimal, datetime, str, bool]:
    if dv.strip() == "" and dt != DT_BOOLEAN:
        return None

    if dt in DATA_TYPE_STRING_PARSERS:
        return DATA_TYPE_STRING_PARSERS[dt](dv, field_name, nullable, null_values)

    # Otherwise, keep string version
    return dv


def design_to_relations(df: IO, gis_mode: bool) -> List[Relation]:
    """
    Validates the design file and converts it into relations and their fields.
    """

    relations = []

    design_reader = csv.reader(df)
    relation_name_and_headers = next(design_reader)

    end_loop = False

    while not end_loop:
        design_relation_name = relation_name_and_headers[0]

        relation_fields = []
        id_type = ""

        end_inner_loop = False

        while not end_inner_loop:
            try:
                current_field = next(design_reader)
                while current_field and "".join(current_field).strip() != "":
                    # TODO: Process

                    field_name = field_to_py_code(current_field[1])
                    data_type = standardize_data_type(current_field[2])

                    if not valid_data_type(data_type, gis_mode):
                        raise errors.GenerationError("Error: Unknown data type specified for field '{}': '{}'.".format(
                            field_name,
                            data_type
                        ))

                    nullable = current_field[3].strip().lower() in BOOLEAN_TRUE_VALUES
                    # TODO: Covert to correct type?
                    null_values = tuple([n.strip() for n in current_field[4].split(";")])

                    if data_type in KEY_TYPES and id_type != "":
                        raise errors.GenerationError(
                            "Error: More than one primary key (auto/manual key) was specified for relation '{}'. "
                            "Please only specify one primary key.".format(design_relation_name)
                        )

                    if data_type == DT_AUTO_KEY:
                        id_type = "integer"  # TODO: DT_ ?
                    elif data_type == DT_MANUAL_KEY:
                        id_type = "text"  # TODO: DT_ ?

                    csv_names = tuple(f.replace(r"\;", ";") for f in re.split(r";;\s*", current_field[0]))
                    if len(csv_names) > 1 and data_type != "":  # TODO: Specify permissible data types here
                        # TODO: Codify this better
                        raise errors.GenerationError(
                            "Error: Cannot take more than one column as input for field '{field}' with data type "
                            "{data_type}.".format(field=current_field[0], data_type=data_type))

                    # TODO: Have blank mean a default inference instead of False
                    show_in_table = current_field[7].strip().lower() in BOOLEAN_TRUE_VALUES
                    if data_type in KEY_TYPES and not show_in_table:
                        print("Warning: Primary key '{}' must be shown in table; overriding false-like value...".format(
                            field_name))
                        show_in_table = True

                    default_str = current_field[5].strip()
                    default = get_default_from_csv_with_type(field_name, default_str, data_type, nullable, null_values)

                    # TODO: This handling of additional_fields could eventually cause trouble, because it can shift
                    #  positions of additional fields if a blank additional field occurs before a valued one.
                    current_field_obj = RelationField(
                        csv_names=csv_names,
                        name=field_name,
                        data_type=data_type,
                        nullable=nullable,
                        null_values=null_values,
                        default=default,
                        description=current_field[6].strip(),
                        show_in_table=show_in_table,
                        additional_fields=tuple(f for f in current_field[8:] if f.strip() != "")
                    )

                    if (len(current_field_obj.additional_fields) >
                            len(DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS[data_type])):
                        if data_type in KEY_TYPES and len(current_field_obj.additional_fields) == 2 and \
                                DESIGN_SEPARATOR in current_field_obj.additional_fields[1]:
                            # Looks like user tried to specify choices for a key-type
                            # TODO: This is heuristic-based, and should be re-examined if additional_fields changes
                            #  for the key types.
                            exit_with_error(
                                "Error: Choices aren't valid for a primary key (auto or manual.) If this was\n"
                                "       specifyable, there could only be as many rows as choices, and the choices\n"
                                "       would not be modifyable after the database is constructed."
                            )

                        else:
                            print(
                                "Warning: More additional settings specified for field '{field}' than can be used.\n"
                                "         Available settings: '{settings}' \n".format(
                                    field=field_name,
                                    settings="', '".join(DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS[data_type])
                                )
                            )

                    if data_type == DT_TEXT:
                        choices = formatters.get_choices_from_text_field(current_field_obj)
                        if choices is not None and default_str != "" and default_str not in choices:
                            raise errors.GenerationError(
                                "Error: Default value for field '{field}' in relation '{relation}' does not match \n"
                                "       any available choices for the field. \n"
                                "       Available choices: {choices}".format(
                                    field=current_field[1],
                                    relation=design_relation_name,
                                    choices=", ".join(choices)
                                ))

                        current_field_obj.choices = choices if choices is not None and len(choices) > 1 else None

                    relation_fields.append(current_field_obj)

                    current_field = next(design_reader)

            except StopIteration:
                if len(relation_fields) == 0:
                    end_loop = True
                    break

            # Otherwise, save the relation information.
            relations.append(Relation(design_name=design_relation_name, fields=relation_fields, id_type=id_type))

            # Find the next relation.

            relation_name_and_headers = ()

            try:
                while "".join(relation_name_and_headers).strip() == "":
                    rel = next(design_reader)
                    if len(rel) > 0:
                        relation_name_and_headers = rel
                        end_inner_loop = True

            except StopIteration:
                end_loop = True
                break

    return relations


def create_admin(relations: List[Relation], site_name: str, gis_mode: bool) -> io.StringIO:
    """
    Creates the contents of the admin.py file for the Django data application.
    """

    af = io.StringIO()

    af.write(ADMIN_FILE_HEADER_TEMPLATE.format(site_name))

    for relation in relations:
        # Write admin information

        list_display_fields = tuple(f.name for f in relation.fields if f.show_in_table)
        list_filter_fields = tuple(f.name for f in relation.fields
                                   if f.data_type == DT_BOOLEAN or f.choices is not None)

        advanced_filter_fields = tuple(r.name for r in relation.fields)

        af.write(MODEL_ADMIN_TEMPLATE.format(
            relation_name=relation.name,
            admin_class="gis_admin.GeoModelAdmin" if gis_mode else "",
            list_display=("    list_display = ('{}',)\n".format("', '".join(list_display_fields))
                          if len(list_display_fields) > 1 else ""),
            list_filter=("    list_filter = ('{}',)\n".format("', '".join(list_filter_fields))
                         if len(list_filter_fields) > 0 else ""),
            advanced_filter_fields=("    advanced_filter_fields = ('{}',)\n".format("', '".join(advanced_filter_fields))
                                    if len(advanced_filter_fields) > 0 else "")
        ))

        af.flush()

    af.seek(0)

    return af


def create_models(relations: List[Relation], gis_mode: bool) -> io.StringIO:
    """
    Creates the contents of the model.py file for the Django data application.
    """

    mf = io.StringIO()

    mf.write(MODELS_FILE_HEADER.format(version=VERSION,
                                       models_path="django.contrib.gis.db" if gis_mode else "django.db"))

    for relation in relations:
        mf.write(MODEL_TEMPLATE.format(
            name=relation.name,
            # TODO: Pretty-print serialize field objects?
            fields=pprint.pformat([dict(f) for f in relation.fields], indent=12, width=120, compact=True),
            id_type=relation.id_type,
            short_name=relation.name[len(PDT_RELATION_PREFIX):],
            model_fields="\n".join("    {} = {}".format(f.name, formatters.DJANGO_TYPE_FORMATTERS[f.data_type](f))
                                   for f in relation.fields)
        ))
        mf.flush()

    mf.seek(0)

    return mf


def create_api(relations: List[Relation], site_name: str, gis_mode: bool) -> io.StringIO:
    """
    Creates the contents of the API specification file.
    """

    api_file = io.StringIO()

    api_file.write(API_FILE_HEADER.format(version=VERSION, site_name=site_name, gis_mode=gis_mode,
                                          relations=pprint.pformat(relations, indent=12, width=120, compact=True)))

    for relation in relations:
        api_file.write(MODEL_SERIALIZER_TEMPLATE.format(
            relation_name=relation.name,
            fields="('{}',)".format("', '".join(f.name for f in relation.fields))
        ))

        api_file.write(MODEL_VIEWSET_TEMPLATE.format(
            relation_name=relation.name,
            categorical_fields="('{}',)".format(
                "', '".join(f.name for f in relation.fields if f.choices is not None)),
            categorical_choices=pprint.pformat(
                {f.name: f.choices + (("",) if f.nullable else ())
                 for f in relation.fields if f.choices is not None},
                indent=12, width=120, compact=True)
        ))

        api_file.write(MODEL_ROUTER_REGISTRATION_TEMPLATE.format(
            relation_name_lower=relation.name_lower,
            relation_name=relation.name,
        ))

        api_file.flush()

    api_file.seek(0)
    return api_file


TEMP_DIRECTORY = os.path.join(os.getcwd(), "tmp")


def print_usage():
    print("Usage: ptd-generate design.csv output_site_name")


def sanitize_and_check_site_name(site_name_raw: str) -> str:
    site_name_stripped = site_name_raw.strip()
    site_name = sanitize_python_identifier(site_name_stripped)

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]+$", site_name):
        raise errors.GenerationError("Error: Site name '{}' cannot be turned into a valid Python package name. \n"
                                     "       Please choose a different name.".format(site_name_stripped))

    if site_name != site_name_stripped:
        print("Warning: Site name '{}' is not a valid Python package name; \n"
              "         using '{}' instead.\n".format(site_name_stripped, site_name))

    try:
        importlib.import_module(site_name)
        raise errors.GenerationError("Error: Site name '{}' conflicts with a Python package name. \n"
                                     "       Please choose a different name.".format(site_name))
    except ImportError:
        pass

    return site_name


def is_common_password(password: str, package_dir: str) -> bool:
    # Try to use password list created by Royce Williams and adapted for the Django project:
    # https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7

    common_passwords = {"password", "123456", "12345678"}  # Fallbacks if file not present
    try:
        with gzip.open(os.path.join(package_dir, "common-passwords.txt.gz")) as f:
            common_passwords = {p.strip() for p in f.read().decode().splitlines()
                                if len(p.strip()) >= 8}  # Don't bother including too-short passwords
    except OSError:
        pass

    return password.lower().strip() in common_passwords


def copy_buf_to_path(buf, path):
    with open(path, "w") as fh:
        shutil.copyfileobj(buf, fh)


def clean_up(package_dir: str, django_site_name: str):
    subprocess.run((os.path.join(package_dir, "os_scripts", "clean_up.bat" if os.name == "nt" else "clean_up.bash"),
                    package_dir, django_site_name, TEMP_DIRECTORY))


def get_script_file_name(name: str):
    return "{}.{}".format(name, "bat" if os.name == "nt" else "bash")


# TODO: TIMEZONES
# TODO: Multiple date formats
# TODO: More ways for custom validation
# TODO: More customization options


def main():
    print_license()

    if len(sys.argv) != 3:
        print_usage()
        exit(1)

    # TODO: EXPERIMENTAL: GIS MODE
    gis_mode = os.environ.get("PTD_GIS", "false").lower() == "true"
    spatialite_library_path = os.environ.get("SPATIALITE_LIBRARY_PATH", "")
    if gis_mode:
        print("Notice: Enabling experimental GIS mode...\n")
        if spatialite_library_path == "":
            exit_with_error("Error: Please set SPATIALITE_LIBRARY_PATH.")

    args = sys.argv[1:]

    # TODO: Make path more robust
    package_dir = Path(os.path.dirname(__file__)).parent

    design_file = args[0]  # File name for design file input

    django_site_name = ""
    try:
        django_site_name = sanitize_and_check_site_name(args[1])
    except ValueError as e:
        exit_with_error(str(e))

    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY)

    if os.name not in ("nt", "posix"):
        exit_with_error("Unsupported platform.")

    site_url = "localhost"

    # Process and validate design file, get contents of admin and models files

    print("Validating design file '{}'...".format(design_file))

    relations = []

    try:
        with open(os.path.join(os.getcwd(), design_file), "r") as df:
            try:
                relations = design_to_relations(df, gis_mode)
            except errors.GenerationError as e:
                exit_with_error(str(e))

    except FileNotFoundError:
        exit_with_error("Error: Design file not found: '{}'.".format(design_file))

    except IOError:
        exit_with_error("Error: Design file could not be read: '{}'.".format(design_file))

    if len(relations) == 0:
        exit_with_error("Error: No relations detected.")

    a_buf = create_admin(relations, django_site_name, gis_mode)
    m_buf = create_models(relations, gis_mode)
    api_buf = create_api(relations, django_site_name, gis_mode)

    print("Done.\n")

    try:
        prod_build = input("Is this a production build? (y/n): ")
        if prod_build.lower() in BOOLEAN_TRUE_VALUES:
            site_url = input("Please enter the production site URL, without 'www.' or 'http://': ")
            while "http:" in site_url or "https:" in site_url or "/www." in site_url:
                site_url = input("Please enter the production site URL, without 'www.' or 'http://': ")
        elif prod_build.lower() not in BOOLEAN_FALSE_VALUES:
            print("Invalid answer '{}', assuming 'n'...".format(prod_build))

    except KeyboardInterrupt:
        print("\nExiting...\n")
        exit(0)

    print()

    core_app_path = os.path.join(TEMP_DIRECTORY, django_site_name, "core")
    django_site_path = os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name)

    with a_buf, m_buf, api_buf:
        # Clean up any old remnants
        clean_up(package_dir, django_site_name)

        # Run site creation script
        subprocess.run((
            os.path.join(package_dir, "os_scripts", get_script_file_name("create_django_site")),
            package_dir, django_site_name, TEMP_DIRECTORY, "Dockerfile{}.template".format(".gis" if gis_mode else "")
        ), check=True)

        # Write admin file contents to disk
        copy_buf_to_path(a_buf, os.path.join(core_app_path, "admin.py"))

        # Write model file contents to disk
        copy_buf_to_path(m_buf, os.path.join(core_app_path, "models.py"))

        # Write API specification file contents to disk
        copy_buf_to_path(api_buf, os.path.join(core_app_path, "api.py"))

    with open(os.path.join(django_site_path, "settings.py"), "r+") as sf:
        old_contents = sf.read()

        sf.seek(0)

        new_contents = (
                old_contents.replace(INSTALLED_APPS_OLD, INSTALLED_APPS_NEW_GIS if gis_mode else INSTALLED_APPS_NEW)
                .replace(DEBUG_OLD, DEBUG_NEW)
                .replace(ALLOWED_HOSTS_OLD, ALLOWED_HOSTS_NEW.format(site_url))
                .replace(STATIC_OLD, STATIC_NEW)
                + DISABLE_MAX_FIELDS
                + REST_FRAMEWORK_SETTINGS
        )

        if gis_mode:
            new_contents = new_contents.replace(DATABASE_ENGINE_NORMAL, DATABASE_ENGINE_GIS)
            new_contents += SPATIALITE_SETTINGS.format(spatialite_library_path)

        sf.write(new_contents)

        # TODO: May not need spatialite path in settings

        sf.truncate()

    with open(os.path.join(django_site_path, "urls.py"), "r+") as uf:
        old_contents = uf.read()
        uf.seek(0)
        uf.write(old_contents.replace(URL_OLD, URL_NEW))
        uf.truncate()

    print("\n================ ADMINISTRATIVE SETUP ================")

    admin_username = ""
    admin_email = ""
    admin_password = "1"
    admin_password_2 = "2"

    try:
        admin_username = input("Admin Account Username: ")
        while admin_username.strip() == "":
            print("Please enter a username.")
            admin_username = input("Admin Account Username: ")
        admin_email = input("Admin Account Email (Optional): ")

        while admin_password != admin_password_2:
            admin_password = getpass.getpass("Admin Account Password: ")

            # TODO: Properly check password validity
            if len(admin_password.strip()) < 8:
                print("Error: Please enter a more secure password (8 or more characters).")
                admin_password = "1"
                admin_password_2 = "2"
                continue

            if is_common_password(admin_password, package_dir=package_dir):
                print("Error: Please enter in a less commonly-used password (8 or more characters).")
                admin_password = "1"
                admin_password_2 = "2"
                continue

            admin_password_2 = getpass.getpass("Admin Account Password Again: ")

            if admin_password != admin_password_2:
                print("Error: Passwords do not match. Please try again.")

    except KeyboardInterrupt:
        print("\n\nCleaning up and exiting...")
        clean_up(package_dir, django_site_name)
        print("Done.\n")
        exit(0)

    print("======================================================\n")

    try:
        # TODO: Make path more robust
        subprocess.run((
            os.path.join(package_dir, "os_scripts", get_script_file_name("run_site_setup")), package_dir,
            django_site_name, TEMP_DIRECTORY, admin_username, admin_email, admin_password, site_url
        ), check=True)

    except subprocess.CalledProcessError:
        # Need to catch subprocess errors to prevent password from being shown onscreen.
        clean_up(package_dir, django_site_name)
        exit_with_error("Error: An error occurred while running the site setup script.\nTerminating...")

    shutil.make_archive(django_site_name, "zip", root_dir=os.path.join(os.getcwd(), "tmp"), base_dir=django_site_name)


if __name__ == "__main__":
    main()
