#!/usr/bin/env python3

import csv
import json
import os
import subprocess
import sys

from common import *

TEMP_DIRECTORY = "tmp"

URL_OLD = """urlpatterns = [
    path('admin/', admin.site.urls),
]"""
URL_NEW = """from django.urls import include

urlpatterns = [
    path('', admin.site.urls),
    path('advanced_filters/', include('advanced_filters.urls')),
]"""

DEBUG_OLD = "DEBUG = True"
DEBUG_NEW = "DEBUG = True"

ALLOWED_HOSTS_OLD = "ALLOWED_HOSTS = []"
ALLOWED_HOSTS_NEW = "ALLOWED_HOSTS = ['127.0.0.1', 'localhost']"

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


def auto_key_formatter(f):
    return "models.AutoField(primary_key=True, help_text='{}')".format(f["description"].replace("'", "\\'"))


def manual_key_formatter(f):
    # TODO: Shouldn't be always text?
    return "models.TextField(primary_key=True, max_length=127, " \
           "help_text='{}')".format((f["description"].replace("'", "\\'")))


def foreign_key_formatter(f):
    return "models.ForeignKey('{}', on_delete=models.CASCADE)".format(to_relation_name(f["additional_fields"]))


def integer_formatter(f):
    return "models.IntegerField(help_text='{}', null={}{})".format(
        f["description"].replace("'", "\\'"),
        str(f["nullable"]),
        "" if f["default"] is None else ", default={}".format(f["default"])
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
        choice_names = [c.strip() for c in f["additional_fields"][0].split(";")]
        choices = tuple(zip(choice_names, choice_names))

    return "models.{}(help_text='{}'{}{}{})".format(
        "TextField" if max_length is None else "CharField",
        f["description"].replace("'", "\\'"),
        "" if f["default"] is None else ", default={}".format(f["default"]),
        "" if len(choices) == 0 else ", choices={}".format(str(choices)),
        "" if max_length is None else ", max_length={}".format(max_length)
    )


def date_formatter(f):
    # TODO: standardize date formatting...
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
    "integer": integer_formatter,
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
        return datetime.strptime(dv, "%Y-%m-%d")

    if dt == "boolean":
        if nullable and ((len(null_values) != 0 and dv.strip() in null_values) or (dv.strip() == "")):
            return None

        return dv.lower() in ("y", "yes", "t", "true")

    return dv


def to_relation_name(name):
    python_relation_name = "".join([n.capitalize() for n in name.split("_")])

    if python_relation_name in PYTHON_KEYWORDS:
        python_relation_name += "Class"

    return python_relation_name


def main(args):
    if len(args) != 2:
        print("Usage: ./generate.py design.csv output_site_name")

    design_file = args[0]  # File name for design file input
    django_site_name = args[1]

    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY)

    subprocess.run(["./create_django_site.bash", django_site_name, TEMP_DIRECTORY], check=True)

    with open(design_file, "r") as df, \
            open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "models.py"), "w") as mf, \
            open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "admin.py"), "w") as af:
        mf.write("from django.db import models\n")

        af.write("from django.contrib import admin\n")
        af.write("from core.models import *\n")
        af.write("from .export_csv import ExportCSVMixin\n")
        af.write("from .import_csv import ImportCSVMixin\n")

        design_reader = csv.reader(df)

        relation_name = next(design_reader)

        end_loop = False

        while not end_loop:
            python_relation_name = to_relation_name(relation_name[0])

            relation_fields = []

            while True:
                try:
                    current_field = next(design_reader)
                    while current_field:
                        # TODO: Process

                        if current_field[2].lower() not in DATA_TYPES:
                            print("Error: Unknown data type specified for field '{}': '{}'".format(
                                current_field[1],
                                current_field[2].lower()
                            ))

                        data_type = current_field[2].lower()
                        nullable = current_field[3].lower() in ("true", "t", "yes", "y", "1")
                        null_values = tuple([n.strip() for n in current_field[4].split(";")])

                        current_field_data = {
                            "name": field_to_py_code(current_field[1].lower()),
                            "csv_name": current_field[0],
                            "data_type": data_type,
                            "nullable": nullable,
                            "null_values": null_values,
                            "alt": current_field[6] == "true",
                            "default": get_default_from_csv_with_type(current_field[5], data_type, nullable,
                                                                      null_values),
                            "description": current_field[7].strip(),
                            "additional_fields": current_field[8:]
                        }

                        relation_fields.append(current_field_data)

                        current_field = next(design_reader)

                    mf.write("\n\nclass {}(models.Model):\n".format(python_relation_name))
                    mf.write("    @classmethod\n")
                    mf.write("    def ptd_info(cls):")
                    mf.write("        return json.loads(\"\"\"{}\"\"\")\n\n".format(json.dumps(relation_fields)))

                    af.write("\n\n@admin.register({})\n".format(python_relation_name))
                    af.write("class {}Admin(ExportCSVMixin, ImportCSVMixin, admin.ModelAdmin):\n".format(
                        python_relation_name
                    ))
                    af.write("    actions = ['export_csv']\n")

                    for f in relation_fields:
                        mf.write("    {} = {}\n".format(f["name"], DJANGO_TYPE_FORMATTERS[f["data_type"]](f)))

                    while not current_field:
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
                 .replace(ALLOWED_HOSTS_OLD, ALLOWED_HOSTS_NEW))
        sf.truncate()

    with open(os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name, "urls.py"), "r+") as uf:
        old_contents = uf.read()
        uf.seek(0)
        uf.write(old_contents.replace(URL_OLD, URL_NEW))
        uf.truncate()

    subprocess.run(["./run_site_setup.bash", django_site_name, TEMP_DIRECTORY], check=True)


if __name__ == "__main__":
    main(sys.argv[1:])