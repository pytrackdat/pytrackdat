#!/usr/bin/env python3

import csv
import getpass
import json
import os
import shutil
import subprocess
import sys

from common import *

# TODO: TIMEZONES
# TODO: Multiple date formats
# TODO: More ways for custom validation
# TODO: More customization options

TEMP_DIRECTORY = "tmp"

ADMIN_FILE_HEADER = """
from django.contrib import admin
from core.models import *
from .export_csv import ExportCSVMixin
from .import_csv import ImportCSVMixin
from .export_labels import ExportLabelsMixin

"""

MODELS_FILE_HEADER = """
import json
from django.db import models

"""

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
ALLOWED_HOSTS_NEW = "ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] if (os.getenv('DJANGO_ENV') == 'production') else []"

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

BASIC_NUMBER_TYPES = {
    "integer": "IntegerField",
    "float": "FloatField",
}


def print_usage():
    print("Usage: ./generate.py design.csv output_site_name")


def auto_key_formatter(f):
    return "models.AutoField(primary_key=True, help_text='{}')".format(f["description"].replace("'", "\\'"))


def manual_key_formatter(f):
    # TODO: Shouldn't be always text?
    return "models.TextField(primary_key=True, max_length=127, " \
           "help_text='{}')".format((f["description"].replace("'", "\\'")))


def foreign_key_formatter(f):
    return "models.ForeignKey('{}', help_text='{}', on_delete=models.CASCADE)".format(
        to_relation_name(f["additional_fields"][0]),
        f["description"].replace("'", "\\'")
    )


def basic_number_formatter(f):
    t = BASIC_NUMBER_TYPES[f["data_type"]]
    return "models.{}(help_text='{}', null={}{})".format(
        t,
        f["description"].replace("'", "\\'"),
        str(f["nullable"]),
        "" if f["default"] is None else ", default={}".format(f["default"])
    )


def decimal_formatter(f):
    return "models.DecimalField(help_text='{}', max_digits={}, decimal_places={}, null={}{})".format(
        f["description"].replace("'", "\\'"),
        f["additional_fields"][0],
        f["additional_fields"][1],
        str(f["nullable"]),
        "" if f["default"] is None else ", default=Decimal({})".format(f["default"])
    )


def boolean_formatter(f):
    return "models.BooleanField(help_text='{}', null={}{})".format(
        f["description"].replace("'", "\\'"),
        str(f["nullable"]),
        "" if f["default"] is None else ", default={}".format(f["default"])
    )


def text_formatter(f):
    choices = ()
    max_length = None

    if len(f["additional_fields"]) >= 1:
        try:
            max_length = int(f["additional_fields"][0])
        except ValueError:
            pass

    if len(f["additional_fields"]) == 2:
        # TODO: Choice human names
        choice_names = [c.strip() for c in f["additional_fields"][1].split(";")]
        choices = tuple(zip(choice_names, choice_names))

    return "models.{}(help_text='{}'{}{}{})".format(
        "TextField" if max_length is None else "CharField",
        f["description"].replace("'", "\\'"),
        "" if f["default"] is None else ", default={}".format(f["default"]),
        "" if len(choices) == 0 else ", choices={}".format(str(choices)),
        "" if max_length is None else ", max_length={}".format(max_length)
    )


def date_formatter(f):
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


def get_default_from_csv_with_type(dv, dt, nullable=False, null_values=()):
    if dv.strip() == "" and dt != "boolean":
        return None

    if dt == "integer":
        return int(dv)

    if dt == "date":
        # TODO: adjust format based on heuristics
        # TODO: Allow extra column setting with date format from python docs?
        if re.match(RE_DATE_YMD_D, str_v):
            return datetime.strptime(dv, "%Y-%m-%d")
        elif re.match(RE_DATE_DMY_D, str_v):
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


def main(args):
    design_file = args[0]  # File name for design file input
    django_site_name = args[1]

    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY)

    if os.name not in ("nt", "posix"):
        print("Unsupported platform.")
        exit(1)

    create_site_script = "create_django_site.bat" if os.name == "nt" else "./create_django_site.bash"
    create_site_options = [create_site_script, django_site_name, TEMP_DIRECTORY]
    subprocess.run(create_site_options, check=True)

    with open(design_file, "r") as df, \
            open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "models.py"), "w") as mf, \
            open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "admin.py"), "w") as af:
        af.write(ADMIN_FILE_HEADER)
        mf.write(MODELS_FILE_HEADER)

        design_reader = csv.reader(df)

        relation_name = next(design_reader)

        end_loop = False

        while not end_loop:
            python_relation_name = to_relation_name(relation_name[0])

            relation_fields = []
            id_type = ""

            while True:
                try:
                    current_field = next(design_reader)
                    while current_field and "".join(current_field).strip() != "":
                        # TODO: Process

                        if current_field[2].lower() not in DATA_TYPES:
                            print("Error: Unknown data type specified for field '{}': '{}'".format(
                                current_field[1],
                                current_field[2].lower()
                            ))
                            exit(1)

                        data_type = current_field[2].lower()
                        nullable = current_field[3].lower() in ("true", "t", "yes", "y", "1")
                        null_values = tuple([n.strip() for n in current_field[4].split(";")])

                        if data_type in ("auto_key", "manual_key") and id_type != "":
                            print("Error: Primary key was already specified for relation "
                                  "'{}'. Please only specify one primary key.".format(python_relation_name))
                            exit(1)

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
                            "default": get_default_from_csv_with_type(current_field[5], data_type, nullable,
                                                                      null_values),
                            "description": current_field[6].strip(),
                            "additional_fields": current_field[7:]
                        }

                        relation_fields.append(current_field_data)

                        current_field = next(design_reader)

                    mf.write("\n\nclass {}(models.Model):\n".format(python_relation_name))
                    mf.write("    @classmethod\n")
                    mf.write("    def ptd_info(cls):\n")
                    mf.write("        return json.loads(\"\"\"{}\"\"\")\n\n".format(json.dumps(relation_fields)))

                    mf.write("    @classmethod\n")
                    mf.write("    def get_id_type(cls):\n")
                    mf.write("        return '{}'\n\n".format(id_type))

                    af.write("\n\n@admin.register({})\n".format(python_relation_name))
                    af.write("class {}Admin(ExportCSVMixin, ImportCSVMixin, ExportLabelsMixin, "
                             "admin.ModelAdmin):\n".format(python_relation_name))
                    af.write("    actions = ['export_csv', 'export_labels']\n")

                    for f in relation_fields:
                        mf.write("    {} = {}\n".format(f["name"], DJANGO_TYPE_FORMATTERS[f["data_type"]](f)))

                    while not current_field or "".join(current_field).strip() == "":
                        current_field = next(design_reader)

                    relation_name = next(design_reader)

                except StopIteration:
                    end_loop = True
                    break

    with open(os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name, "settings.py"), "r+") as sf:
        old_contents = sf.read()
        sf.seek(0)
        sf.write(old_contents.replace(INSTALLED_APPS_OLD, INSTALLED_APPS_NEW)
                 .replace(DEBUG_OLD, DEBUG_NEW)
                 .replace(ALLOWED_HOSTS_OLD, ALLOWED_HOSTS_NEW)
                 .replace(STATIC_OLD, STATIC_NEW))
        sf.truncate()

    with open(os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name, "urls.py"), "r+") as uf:
        old_contents = uf.read()
        uf.seek(0)
        uf.write(old_contents.replace(URL_OLD, URL_NEW))
        uf.truncate()

    print("\n===== ADMINISTRATIVE USER SETUP =====")
    admin_username = input("Admin Account Username: ")
    admin_email = input("Admin Account Email (Optional): ")
    admin_password = "1"
    admin_password_2 = "2"
    while admin_password != admin_password_2:
        admin_password = getpass.getpass("Admin Account Password: ")
        admin_password_2 = getpass.getpass("Admin Account Password Again: ")
        if admin_password != admin_password_2:
            print("Passwords do not match. Please try again.")
    print("=====================================\n")

    try:
        site_setup_script = "run_site_setup.bat" if os.name == "nt" else "./run_site_setup.bash"
        site_setup_options = [site_setup_script, django_site_name, TEMP_DIRECTORY, admin_username, admin_email,
                              admin_password]
        subprocess.run(site_setup_options, check=True)

    except subprocess.CalledProcessError:
        # Need to catch subprocess errors to prevent password from being shown onscreen.
        print("An error occurred while running the site setup script.")
        print("Terminating...")
        exit(1)

    shutil.make_archive(django_site_name, "zip", base_dir=os.path.join("tmp", django_site_name))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_usage()
        exit(1)

    main(sys.argv[1:])
