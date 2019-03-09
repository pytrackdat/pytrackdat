#!/usr/bin/env python3

# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2019 the PyTrackDat authors.
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
import datetime
import getpass
import gzip
import io
import json
import os
import shutil
import subprocess
import sys

from typing import Dict, Optional, Tuple, Union

from common import *

# TODO: TIMEZONES
# TODO: Multiple date formats
# TODO: More ways for custom validation
# TODO: More customization options

TEMP_DIRECTORY = "tmp"

ADMIN_FILE_HEADER = """# Generated using PyTrackDat v{}
from django.contrib import admin
from advanced_filters.admin import AdminAdvancedFiltersMixin

from core.models import *
from .export_csv import ExportCSVMixin
from .import_csv import ImportCSVMixin
from .export_labels import ExportLabelsMixin

""".format(VERSION)

MODELS_FILE_HEADER = """# Generated using PyTrackDat v{}
import json
from django.db import models

""".format(VERSION)

URL_OLD = """urlpatterns = [
    path('admin/', admin.site.urls),
]"""
URL_NEW = """from django.urls import include

urlpatterns = [
    path('', admin.site.urls),
    path('advanced_filters/', include('advanced_filters.urls')),
]"""

DEBUG_OLD = "DEBUG = True"
DEBUG_NEW = "DEBUG = not (os.getenv('DJANGO_ENV') == 'production')"

ALLOWED_HOSTS_OLD = "ALLOWED_HOSTS = []"
ALLOWED_HOSTS_NEW = "ALLOWED_HOSTS = ['127.0.0.1', '{}'] if (os.getenv('DJANGO_ENV') == 'production') else []"

INSTALLED_APPS_OLD = """INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]"""

INSTALLED_APPS_NEW = """INSTALLED_APPS = [
    'core.apps.CoreConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'advanced_filters',
]"""

STATIC_OLD = "STATIC_URL = '/static/'"
STATIC_NEW = """STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')"""

DISABLE_MAX_FIELDS = "\nDATA_UPLOAD_MAX_NUMBER_FIELDS = None\n"

BASIC_NUMBER_TYPES = {
    "integer": "IntegerField",
    "float": "FloatField",
}


def print_usage() -> None:
    print("Usage: ./generate.py design.csv output_site_name")


def auto_key_formatter(f: Dict) -> str:
    return "models.AutoField(primary_key=True, help_text='{}')".format(f["description"].replace("'", "\\'"))


def manual_key_formatter(f: Dict) -> str:
    # TODO: Shouldn't be always text?
    return "models.TextField(primary_key=True, max_length=127, " \
           "help_text='{}')".format((f["description"].replace("'", "\\'")))


def foreign_key_formatter(f: Dict) -> str:
    return "models.ForeignKey('{}', help_text='{}', on_delete=models.CASCADE)".format(
        to_relation_name(f["additional_fields"][0]),
        f["description"].replace("'", "\\'")
    )


def basic_number_formatter(f: Dict) -> str:
    t = BASIC_NUMBER_TYPES[f["data_type"]]
    return "models.{}(help_text='{}', null={}{})".format(
        t,
        f["description"].replace("'", "\\'"),
        str(f["nullable"]),
        "" if f["default"] is None else ", default={}".format(f["default"])
    )


def decimal_formatter(f: Dict) -> str:
    return "models.DecimalField(help_text='{}', max_digits={}, decimal_places={}, null={}{})".format(
        f["description"].replace("'", "\\'"),
        f["additional_fields"][0],
        f["additional_fields"][1],
        str(f["nullable"]),
        "" if f["default"] is None else ", default=Decimal({})".format(f["default"])
    )


def boolean_formatter(f: Dict) -> str:
    return "models.BooleanField(help_text='{}', null={}{})".format(
        f["description"].replace("'", "\\'"),
        str(f["nullable"]),
        "" if f["default"] is None else ", default={}".format(f["default"])
    )


def get_choices_from_text_field(f: Dict) -> Optional[Tuple[str]]:
    if len(f["additional_fields"]) == 2:
        # TODO: Choice human names
        choice_names = [str(c).strip() for c in f["additional_fields"][1].split(";") if str(c).strip() != ""]
        if len(choice_names) == 0:
            return None
        return tuple(choice_names)
    return None


def text_formatter(f: Dict) -> str:
    choices = ()
    max_length = None

    if len(f["additional_fields"]) >= 1:
        try:
            max_length = int(f["additional_fields"][0])
        except ValueError:
            pass

    if len(f["additional_fields"]) == 2:
        # TODO: Choice human names
        choice_names = get_choices_from_text_field(f)
        if choice_names is not None:
            choices = tuple(zip(choice_names, choice_names))

    return "models.{}(help_text='{}'{}{}{})".format(
        "TextField" if max_length is None else "CharField",
        f["description"].replace("'", "\\'"),
        "" if f["default"] is None else ", default='{}'".format(f["default"]),
        "" if len(choices) == 0 else ", choices={}".format(str(choices)),
        "" if max_length is None else ", max_length={}".format(max_length)
    )


def date_formatter(f: Dict) -> str:
    # TODO: standardize date formatting... I think this might already be standardized?
    return "models.DateField(help_text='{}', null={}{})".format(
        f["description"].replace("'", "\\'"),
        str(f["nullable"]),
        "" if f["default"] is None else ", default=datetime.strptime('{}', '%Y-%m-%d')".format(
            f["default"].strftime("%Y-%m-%d")
        )
    )


DJANGO_TYPE_FORMATTERS = {
    "auto key": auto_key_formatter,
    "manual key": manual_key_formatter,
    "foreign key": foreign_key_formatter,
    "integer": basic_number_formatter,
    "decimal": decimal_formatter,
    "float": basic_number_formatter,
    "boolean": boolean_formatter,
    "text": text_formatter,
    "date": date_formatter,
    "unknown": text_formatter  # Default to text fields... TODO: Should give a warning
}


def get_default_from_csv_with_type(dv: str, dt: str, nullable=False, null_values=()) \
        -> Union[None, int, datetime.datetime, str, bool]:
    if dv.strip() == "" and dt != "boolean":
        return None

    if dt == "integer":
        return int(dv)

    if dt == "date":
        # TODO: adjust format based on heuristics
        # TODO: Allow extra column setting with date format from python docs?
        if re.match(RE_DATE_YMD_D, dv):
            return datetime.strptime(dv, "%Y-%m-%d")
        elif re.match(RE_DATE_DMY_D, dv):
            # TODO: ambiguous d-m-Y or m-d-Y
            return datetime.strptime(dv, "%d-%m-%Y", str_v)
        else:
            # TODO: Warning
            return None

    if dt == "time":
        # TODO: adjust format based on MORE heuristics
        # TODO: Allow extra column setting with time format from python docs?
        if len(dv.split(":")) == 2:
            return datetime.strptime(dv, "%H:%M")
        else:
            return datetime.strptime(dv, "%H:%M:%S")

    if dt == "boolean":
        if nullable and ((len(null_values) != 0 and dv.strip() in null_values) or (dv.strip() == "")):
            return None

        return dv.lower() in ("y", "yes", "t", "true")

    return dv


def exit_with_error(message):
    print()
    print(message)
    print()
    # TODO: HANDLE CLEANUP
    exit(1)


def create_admin_and_models(design_file, site_name):
    """
    Validates the design file and creates the contents of the admin and models
    files for the Django data application.
    """

    af = io.StringIO()
    mf = io.StringIO()

    with open(design_file, "r") as df:
        af.write(ADMIN_FILE_HEADER)
        mf.write(MODELS_FILE_HEADER)

        af.write("admin.site.site_header = 'PyTrackDat: {}'\n\n".format(site_name))

        design_reader = csv.reader(df)

        relation_name = next(design_reader)

        end_loop = False

        while not end_loop:
            python_relation_name = to_relation_name(relation_name[0])

            relation_fields = []
            id_type = ""

            end_inner_loop = False

            while not end_inner_loop:
                try:
                    current_field = next(design_reader)
                    while current_field and "".join(current_field).strip() != "":
                        # TODO: Process

                        if current_field[2].lower() not in DATA_TYPES:
                            exit_with_error("Error: Unknown data type specified for field '{}': '{}'".format(
                                current_field[1],
                                current_field[2].lower()
                            ))

                        data_type = current_field[2].lower()
                        nullable = current_field[3].lower() in ("true", "t", "yes", "y", "1")
                        null_values = tuple([n.strip() for n in current_field[4].split(";")])

                        if data_type in ("auto key", "manual key") and id_type != "":
                            exit_with_error(
                                "Error: More than one primary key (auto/manual key) was specified for relation '{}'. "
                                "Please only specify one primary key.".format(python_relation_name)
                            )

                        if data_type == "auto key":
                            id_type = "integer"
                        elif data_type == "manual key":
                            id_type = "text"

                        current_field_data = {
                            "name": field_to_py_code(current_field[1].lower()),
                            "csv_name": current_field[0],
                            "data_type": data_type,
                            "nullable": nullable,
                            "null_values": null_values,
                            "default": get_default_from_csv_with_type(current_field[5].strip(), data_type, nullable,
                                                                      null_values),
                            "description": current_field[6].strip(),
                            "additional_fields": current_field[7:]
                        }

                        if data_type == "text":
                            choices = get_choices_from_text_field(current_field_data)
                            if choices is not None and current_field[5].strip() != "" and \
                                    current_field[5].strip() not in choices:
                                exit_with_error(
                                    "Error: Default value for field '{}' in relation '{}' does not match any available "
                                    "choices for the field. Available choices: {}".format(
                                        current_field[1],
                                        python_relation_name,
                                        ", ".join(choices)
                                    ))

                            if choices is not None and len(choices) > 1:
                                current_field_data["choices"] = choices

                        relation_fields.append(current_field_data)

                        current_field = next(design_reader)

                except StopIteration:
                    if len(relation_fields) == 0:
                        end_loop = True
                        break

                    # Otherwise, write data into the model and admin files

                mf.write("\n\nclass {}(models.Model):\n".format(python_relation_name))
                mf.write("    @classmethod\n")
                mf.write("    def ptd_info(cls):\n")
                mf.write("        return json.loads(\"\"\"{}\"\"\")\n\n".format(json.dumps(relation_fields)))

                mf.write("    @classmethod\n")
                mf.write("    def get_label_name(cls):\n")
                mf.write("        return    '{}'\n\n".format(python_relation_name[len(PDT_RELATION_PREFIX):]))

                mf.write("    @classmethod\n")
                mf.write("    def get_id_type(cls):\n")
                mf.write("        return '{}'\n\n".format(id_type))

                mf.write("    class Meta:\n")
                mf.write("        verbose_name = '{}'\n\n".format(python_relation_name[len(PDT_RELATION_PREFIX):]))

                af.write("\n\n@admin.register({})\n".format(python_relation_name))
                af.write("class {}Admin(ExportCSVMixin, ImportCSVMixin, ExportLabelsMixin, AdminAdvancedFiltersMixin, "
                         "admin.ModelAdmin):\n".format(python_relation_name))
                af.write("    change_list_template = 'admin/core/change_list.html'\n")
                af.write("    actions = ['export_csv', 'export_labels']\n")

                list_display_fields = [r["name"] for r in relation_fields
                                       if r["data_type"] not in ("text", "auto key", "manual key") or "choices" in r]
                key = [r["name"] for r in relation_fields if r["data_type"] in ("auto key", "manual key")]
                list_display_fields = key + list_display_fields

                list_filter_fields = [r["name"] for r in relation_fields
                                      if r["data_type"] in ("boolean",) or "choices" in r]

                advanced_filter_fields = [r["name"] for r in relation_fields]

                if len(list_display_fields) > 1:
                    af.write("    list_display = ('{}',)\n".format("', '".join(list_display_fields)))

                if len(list_filter_fields) > 0:
                    af.write("    list_filter = ('{}',)\n".format("', '".join(list_filter_fields)))

                if len(advanced_filter_fields) > 0:
                    af.write("    advanced_filter_fields = ('{}',)\n".format("', '".join(advanced_filter_fields)))

                for f in relation_fields:
                    mf.write("    {} = {}\n".format(f["name"], DJANGO_TYPE_FORMATTERS[f["data_type"]](f)))

                mf.flush()
                af.flush()

                relation_name = ""

                try:
                    while not relation_name or "".join(relation_name).strip() == "":
                        rel = next(design_reader)
                        if len(rel) > 0:
                            relation_name = rel
                            end_inner_loop = True

                except StopIteration:
                    end_loop = True
                    break

    af.seek(0)
    mf.seek(0)

    return af, mf


def main(args):
    design_file = args[0]  # File name for design file input
    django_site_name = args[1]

    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY)

    if os.name not in ("nt", "posix"):
        print("Unsupported platform.")
        exit(1)

    # Process and validate design file, get contents of admin and models files
    try:
        print("Validating design file '{}'...".format(design_file))
        a_buf, m_buf = create_admin_and_models(design_file, django_site_name)
        print("done.\n")

        site_url = "localhost"
        prod_build = input("Is this a production build? (y/n): ")
        if prod_build.lower() in ("y", "yes"):
            site_url = input("Please enter the production site URL, without 'www.' or 'http://': ")
            while "http:" in site_url or "https:" in site_url or "/www." in site_url:
                site_url = input("Please enter the production site URL, without 'www.' or 'http://': ")
        elif prod_build.lower() not in ("n", "no"):
            print("Invalid answer '{}', assuming 'n'...".format(prod_build))

        print()

        with a_buf, m_buf:
            # Run site creation script
            create_site_script = "os_scripts\\create_django_site.bat" if os.name == "nt" \
                else "./os_scripts/create_django_site.bash"
            create_site_options = [create_site_script, django_site_name, TEMP_DIRECTORY]
            subprocess.run(create_site_options, check=True)

            # Write admin and models file contents to disk
            with open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "models.py"), "w") as mf, \
                    open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "admin.py"), "w") as af:
                shutil.copyfileobj(a_buf, af)
                shutil.copyfileobj(m_buf, mf)

    except FileNotFoundError:
        exit_with_error("Design file not found.")

    with open(os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name, "settings.py"), "r+") as sf:
        old_contents = sf.read()
        sf.seek(0)
        sf.write(old_contents.replace(INSTALLED_APPS_OLD, INSTALLED_APPS_NEW)
                 .replace(DEBUG_OLD, DEBUG_NEW)
                 .replace(ALLOWED_HOSTS_OLD, ALLOWED_HOSTS_NEW.format(site_url))
                 .replace(STATIC_OLD, STATIC_NEW) + DISABLE_MAX_FIELDS)
        sf.truncate()

    with open(os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name, "urls.py"), "r+") as uf:
        old_contents = uf.read()
        uf.seek(0)
        uf.write(old_contents.replace(URL_OLD, URL_NEW))
        uf.truncate()

    # Try to use password list created by Royce Williams and adapted for the Django project:
    # https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7
    common_passwords = ["password", "123456", "12345678"]  # Fallbacks if file not present
    try:
        with gzip.open(os.path.join(os.path.dirname(__file__), "common-passwords.txt.gz")) as f:
            common_passwords = {p.strip() for p in f.read().decode().splitlines()
                                if len(p.strip()) >= 8}  # Don't bother including too-short passwords
    except OSError:
        pass

    print("\n================ ADMINISTRATIVE SETUP ================")
    admin_username = input("Admin Account Username: ")
    while admin_username.strip() == "":
        print("Please enter a username.")
        admin_username = input("Admin Account Username: ")
    admin_email = input("Admin Account Email (Optional): ")
    admin_password = "1"
    admin_password_2 = "2"
    while admin_password != admin_password_2:
        admin_password = getpass.getpass("Admin Account Password: ")

        # TODO: Properly check password validity
        if len(admin_password.strip()) < 8:
            print("Please enter a secure password (8 or more characters).")
            admin_password = "1"
            admin_password_2 = "2"
            continue

        if admin_password.lower().strip() in common_passwords:
            print("Please enter in a less commonly-used password (8 or more characters).")
            admin_password = "1"
            admin_password_2 = "2"
            continue

        admin_password_2 = getpass.getpass("Admin Account Password Again: ")

        if admin_password != admin_password_2:
            print("Passwords do not match. Please try again.")
    print("======================================================\n")

    try:
        site_setup_script = "os_scripts\\run_site_setup.bat" if os.name == "nt" \
            else "./os_scripts/run_site_setup.bash"
        site_setup_options = [site_setup_script, django_site_name, TEMP_DIRECTORY, admin_username, admin_email,
                              admin_password, site_url]
        subprocess.run(site_setup_options, check=True)

    except subprocess.CalledProcessError:
        # Need to catch subprocess errors to prevent password from being shown onscreen.
        exit_with_error("An error occurred while running the site setup script.\nTerminating...")

    shutil.make_archive(django_site_name, "zip", root_dir="tmp", base_dir=django_site_name)


if __name__ == "__main__":
    print_license()

    if len(sys.argv) != 3:
        print_usage()
        exit(1)

    main(sys.argv[1:])
