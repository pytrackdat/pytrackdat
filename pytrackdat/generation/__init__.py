# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2021 the PyTrackDat authors.
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

from pathlib import Path
from typing import List

from ..common import *
from .constants import *

from pytrackdat.design_file import design_to_relations

from . import constants
from . import errors
from . import formatters
from . import utils


__all__ = [
    "constants",
    "errors",
    "formatters",
    "utils",
    "create_models",
    "create_api",
    "print_usage",
    "sanitize_and_check_site_name",
    "is_common_password",
    "main",
    "API_FILTERABLE_FIELD_TYPES"
]


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


API_FILTERABLE_FIELD_TYPES = {
    DT_AUTO_KEY: ["exact", "in"],
    DT_MANUAL_KEY: ["exact", "in"],

    DT_INTEGER: ["exact", "lt", "lte", "gt", "gte", "in"],
    DT_FLOAT: ["exact", "lt", "lte", "gt", "gte"],
    DT_DECIMAL: ["exact", "lt", "lte", "gt", "gte", "in"],

    DT_BOOLEAN: ["exact"],

    DT_TEXT: ["exact", "iexact", "contains", "icontains", "in"],

    DT_DATE: ["exact", "lt", "lte", "gt", "gte", "in"],
    DT_TIME: ["exact", "lt", "lte", "gt", "gte", "in"],

    DT_FOREIGN_KEY: ["exact", "in"],
}


def create_api(relations: List[Relation], site_name: str, gis_mode: bool) -> io.StringIO:
    """
    Creates the contents of the API specification file.
    """

    api_file = io.StringIO()

    api_file.write(API_FILE_HEADER.format(version=VERSION, site_name=site_name, gis_mode=gis_mode,
                                          relations=pprint.pformat(tuple(dict(r) for r in relations), indent=12,
                                                                   width=120, compact=True)))

    for relation in relations:
        api_file.write(MODEL_SERIALIZER_TEMPLATE.format(
            relation_name=relation.name,
            fields="('{}',)".format("', '".join(f.name for f in relation.fields))
        ))

        api_file.write(MODEL_VIEWSET_TEMPLATE.format(
            relation_name=relation.name,
            filterset_fields=pprint.pformat(
                {f.name: API_FILTERABLE_FIELD_TYPES[f.data_type]
                 for f in relation.fields if f.data_type in API_FILTERABLE_FIELD_TYPES},
                indent=12, width=120, compact=True),
            categorical_fields="('{}',)".format(
                "', '".join(f.name for f in relation.fields if f.choices is not None)),
            categorical_choices=pprint.pformat(
                {f.name: f.choices + (("",) if f.nullable else ())
                 for f in relation.fields if f.choices is not None},
                indent=12, width=120, compact=True),
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
    return f"{name}.{'bat' if os.name == 'nt' else 'bash'}"


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
    is_production_build = False

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

    # a_buf = create_admin(relations, django_site_name, gis_mode)
    m_buf = create_models(relations, gis_mode)
    api_buf = create_api(relations, django_site_name, gis_mode)

    print("Done.\n")

    try:
        prod_build = input("Is this a production build? (y/n): ")

        if prod_build.lower() in BOOLEAN_TRUE_VALUES:
            site_url = input(PRODUCTION_SITE_URL_PROMPT)
            while "http:" in site_url or "https:" in site_url or "/www." in site_url:
                site_url = input(PRODUCTION_SITE_URL_PROMPT)

        elif prod_build.lower() not in BOOLEAN_FALSE_VALUES:
            print("Invalid answer '{}', assuming 'n'...".format(prod_build))

        is_production_build = prod_build.lower() in BOOLEAN_TRUE_VALUES

    except KeyboardInterrupt:
        print("\nExiting...\n")
        exit(0)

    print()

    core_app_path = os.path.join(TEMP_DIRECTORY, django_site_name, "core")
    django_site_path = os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name)

    with m_buf, api_buf:
        # Clean up any old remnants
        clean_up(package_dir, django_site_name)

        # Run site creation script
        subprocess.run((
            os.path.join(package_dir, "os_scripts", get_script_file_name("create_django_site")),
            package_dir, django_site_name, TEMP_DIRECTORY, "Dockerfile{}.template".format(".gis" if gis_mode else "")
        ), check=True)

        # # Write admin file contents to disk
        # copy_buf_to_path(a_buf, os.path.join(core_app_path, "admin.py"))

        # Write model file contents to disk
        copy_buf_to_path(m_buf, os.path.join(core_app_path, "models.py"))

        # Write API specification file contents to disk
        copy_buf_to_path(api_buf, os.path.join(core_app_path, "api.py"))

    with open(os.path.join(django_site_path, "settings.py"), "r+") as sf:
        old_contents = sf.read()

        sf.seek(0)

        # TODO: GIS mode stuff and site url stuff should be done in runtime

        new_contents = (
                old_contents.replace(INSTALLED_APPS_OLD, INSTALLED_APPS_NEW.format(gis_mode=gis_mode))
                .replace(MIDDLEWARE_OLD, MIDDLEWARE_NEW)
                .replace(DEBUG_OLD, DEBUG_NEW)
                .replace(ALLOWED_HOSTS_OLD, ALLOWED_HOSTS_NEW.format(site_url=site_url))
                .replace(STATIC_OLD, STATIC_NEW)
                + DISABLE_MAX_FIELDS
                + REST_FRAMEWORK_SETTINGS
                + CORS_SETTINGS.format(site_url=site_url)
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
            os.path.join(package_dir, "os_scripts", get_script_file_name("run_site_setup")),
            package_dir,  # $1
            django_site_name,  # $2
            TEMP_DIRECTORY,  # $3
            admin_username,  # $4
            admin_email,  # $5
            admin_password,  # $6
            site_url,  # $7
            str(is_production_build),  # $8
            str(gis_mode),  # $9
        ), check=True)

    except subprocess.CalledProcessError:
        # Need to catch subprocess errors to prevent password from being shown onscreen.
        clean_up(package_dir, django_site_name)
        exit_with_error("Error: An error occurred while running the site setup script.\nTerminating...")

    shutil.make_archive(django_site_name, "zip", root_dir=os.path.join(os.getcwd(), "tmp"), base_dir=django_site_name)


if __name__ == "__main__":
    main()
