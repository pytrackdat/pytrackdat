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
import io
import pprint

from typing import Dict, IO, Optional, Tuple, Union

from .common import *

ADMIN_FILE_HEADER = """# Generated using PyTrackDat v{}
from django.contrib import admin
from advanced_filters.admin import AdminAdvancedFiltersMixin

from core.models import *
from .export_csv import ExportCSVMixin
from .import_csv import ImportCSVMixin
from .export_labels import ExportLabelsMixin

""".format(VERSION)

SNAPSHOT_ADMIN_FILE_HEADER = """# Generated using PyTrackDat v{}
from django.contrib import admin
from advanced_filters.admin import AdminAdvancedFiltersMixin

from snapshot_manager.models import *

""".format(VERSION)

MODELS_FILE_HEADER = """# Generated using PyTrackDat v{}
from django.db import models

""".format(VERSION)

MODEL_TEMPLATE = """class {name}(models.Model):
    @classmethod
    def ptd_info(cls):
        return {fields}

    @classmethod
    def get_label_name(cls):
        return '{label_name}'

    @classmethod
    def get_id_type(cls):
        return '{id_type}'

    class Meta:
        verbose_name = '{verbose_name}'

    pdt_created_at = models.DateTimeField(auto_now_add=True, null=False)
    pdt_modified_at = models.DateTimeField(auto_now=True, null=False)"""

SNAPSHOT_MODEL = """import os
import shutil
from datetime import datetime

import {}.settings as settings

from django.db import transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Snapshot(models.Model):
    pdt_created_at = models.DateTimeField(auto_now_add=True, null=False)
    pdt_modified_at = models.DateTimeField(auto_now=True, null=False)
    snapshot_type = models.TextField(help_text='Created by whom?', max_length=6, default='manual',
                                     choices=(('auto', 'Automatic'), ('manual', 'Manual')), null=False, blank=False)
    name = models.TextField(help_text='Name of snapshot file', max_length=127, null=False, blank=False)
    size = models.IntegerField(help_text='Size of database (in bytes)', null=False)

    def __str__(self):
        return self.snapshot_type + " snapshot (" + str(self.name) + "; size: " + str(self.size) + " bytes)"

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                # TODO: THIS ONLY WORKS WITH SQLITE
                # Newly-created snapshot

                name = "snapshot-" + str(datetime.utcnow()).replace(" ", "_").replace(":", "-") + ".sqlite3"

                shutil.copyfile(settings.DATABASES['default']['NAME'],
                                os.path.join(settings.BASE_DIR, "snapshots", name))

                self.name = name
                self.size = os.path.getsize(os.path.join(settings.BASE_DIR, "snapshots", name))

        super(Snapshot, self).save(*args, **kwargs)


@receiver(pre_delete, sender=Snapshot)
def delete_snapshot_file(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.BASE_DIR, "snapshots", instance.name))
    except OSError:
        print("Error deleting snapshot")
        # TODO: prevent deletion in some way?
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
    'snapshot_manager.apps.SnapshotManagerConfig',

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


def create_admin_and_models(df: IO, site_name: str) -> Tuple[io.StringIO, io.StringIO]:
    """
    Validates the design file and creates the contents of the admin and models
    files for the Django data application.
    """

    af = io.StringIO()
    mf = io.StringIO()

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

            # Write model information

            mf.write("\n\n")
            mf.write(MODEL_TEMPLATE.format(
                name=python_relation_name,
                fields=pprint.pformat(relation_fields, indent=12, width=120, compact=True),
                label_name=python_relation_name[len(PDT_RELATION_PREFIX):],
                id_type=id_type,
                verbose_name=python_relation_name[len(PDT_RELATION_PREFIX):]
            ))
            mf.write("\n\n")

            # Write admin information

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
