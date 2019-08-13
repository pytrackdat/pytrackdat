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
import re

import core.models

from django import forms
from django.apps import apps
from django.shortcuts import redirect, render
from django.urls import path

from datetime import datetime
from decimal import *
from io import TextIOWrapper

from .common import *

from snapshot_manager.models import Snapshot

# TODO: ACCEPT https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry FOR GIS
# TODO: NEED TO CHECK NULL VALUES?

POINT_REGEX = r"\(\s*-?\d+(\.\d+)?\s+-?\d+(\.\d+)?\s*\)"
LINE_STRING_REGEX = r"\(\s*(-?\d+(\.\d+)\s+-?\d+(\.\d+),\s+)*-?\d+(\.\d+)\s*\)"
POLYGON_REGEX = r"\(\s*({ls},\s*)*{ls}\s*\)".format(ls=LINE_STRING_REGEX)


class ImportCSVForm(forms.Form):
    csv_file = forms.FileField()


class ImportCSVMixin:
    def import_csv(self, request):
        if request.method == "POST":
            form = ImportCSVForm(request.POST, request.FILES)

            if form.is_valid():
                encoding = form.cleaned_data["csv_file"].charset \
                    if form.cleaned_data["csv_file"].charset else "utf-8-sig"
                csv_file = TextIOWrapper(request.FILES["csv_file"], encoding=encoding)

                reader = csv.DictReader(csv_file)

                model_name = self.model.__name__
                ptd_info = self.model.ptd_info()
                headers = [h.strip() for h in reader.fieldnames if h != ""]

                header_fields_1 = {h: tuple([f for f in ptd_info if h == f["csv_name"]]) for h in headers
                                   if len([f for f in ptd_info if h == f["csv_name"]]) > 0}
                header_fields_2 = {h.lower(): tuple([f for f in ptd_info if h.lower() == f["name"]]) for h in headers
                                   if len([f for f in ptd_info if h == f["name"]]) > 0}

                # Option of using database field names as headers, but keep it consistent.
                header_fields = header_fields_1 if len(header_fields_1) >= len(header_fields_2) else header_fields_2

                models = {m.__name__: m for m in apps.get_app_config("core").get_models()}

                snapshot = Snapshot(snapshot_type='auto', reason='Pre-import snapshot')
                snapshot.save()

                for row in reader:
                    object_data = {}
                    for h in header_fields:
                        str_v = row[h].strip()
                        for f in header_fields[h]:
                            if f["data_type"] == "auto key":
                                # Key is automatically generated by the database, skip it.
                                pass

                            elif f["data_type"] == "manual key":
                                object_data[f["name"]] = str_v
                                break

                            elif f["data_type"] == "integer":
                                if re.match(r"^([+-]?[1-9]\d*|0)$", str_v):
                                    object_data[f["name"]] = int(str_v)
                                    break
                                elif f["nullable"]:
                                    # TODO: This assumes null if not integer-like, might be wrong
                                    object_data[f["name"]] = None
                                else:
                                    raise ValueError("Incorrect value for integer field {}: {}".format(f["name"],
                                                                                                       str_v))

                            elif f["data_type"] in ("float", "decimal"):
                                if re.match(r"^[-+]?[0-9]*\.?[0-9]+(e[-+]?[0-9]+)?$", str_v.lower()):
                                    if f["data_type"] == "float":
                                        object_data[f["name"]] = float(str_v.lower())
                                    else:
                                        object_data[f["name"]] = Decimal(str_v.lower())

                                    break

                                elif f["nullable"]:
                                    # TODO: This assumes null if not integer-like, might be wrong
                                    object_data[f["name"]] = None

                                else:
                                    raise ValueError("Incorrect value for float field {}: {}".format(f["name"],
                                                                                                     str_v.lower()))

                            elif f["data_type"] == "boolean":
                                if str_v.lower() in ("y", "yes", "t", "true"):
                                    object_data[f["name"]] = True
                                    break
                                elif str_v.lower() in ("n", "no", "f", "false"):
                                    object_data[f["name"]] = False
                                    break
                                elif f["nullable"]:
                                    object_data[f["name"]] = None

                            elif f["data_type"] == "text":
                                max_length = -1
                                choices = []

                                # TODO: More coersion for choices

                                additional_fields = [f.strip() for f in f["additional_fields"] if f.strip() != ""]

                                if len(additional_fields) in (1, 2):
                                    max_length = int(additional_fields[0])
                                    if len(additional_fields) == 2:
                                        choices = [c.strip() for c in additional_fields[1].split(";")]

                                if 0 < max_length < len(str_v):
                                    raise ValueError("Value for text field {} exceeded maximum length: "
                                                     "{}".format(f["name"], max_length))

                                if len(choices) > 0 and str_v not in choices:
                                    if f["nullable"]:
                                        # TODO: This assumes null if not integer-like, might be wrong
                                        object_data[f["name"]] = None
                                    else:
                                        raise ValueError("Value for text field {} in model {} is not one of the "
                                                         "available choices {}: {}".format(f["name"], model_name,
                                                                                           tuple(choices), str_v))

                                object_data[f["name"]] = str_v
                                break

                            elif f["data_type"] == "date":
                                # TODO: More date formats
                                # TODO: Further validation
                                # TODO: encode format somewhere?
                                if re.match(RE_DATE_YMD_D, str_v):
                                    object_data[f["name"]] = datetime.strptime(str_v, "%Y-%m-%d")
                                    break
                                elif re.match(RE_DATE_YMD_S, str_v):
                                    object_data[f["name"]] = datetime.strptime(str_v, "%Y/%m/%d")
                                    break
                                elif re.match(RE_DATE_DMY_D, str_v):
                                    object_data[f["name"]] = datetime.strptime(str_v, "%d-%m-%Y")
                                    break
                                elif re.match(RE_DATE_DMY_S, str_v):
                                    object_data[f["name"]] = datetime.strptime(str_v, "%d/%m/%Y")
                                    break
                                elif f["nullable"]:
                                    object_data[f["name"]] = None
                                else:
                                    raise ValueError("Incorrect value for date field {} in model {}: "
                                                     "{}".format(f["name"], model_name, str_v))

                            elif f["data_type"] == "time":
                                # TODO: More time formats (12-hour especially)
                                # TODO: Further validation
                                if re.match(r"^\d{2}:\d{2}$", str_v):
                                    object_data[f["name"]] = datetime.strptime(str_v, "%H:%M")
                                elif re.match(r"^\d{2}:\d{2}:\d{2}$", str_v):
                                    object_data[f["name"]] = datetime.strptime(str_v, "%H:%M:%S")

                            elif f["data_type"] == "foreign key":
                                # TODO: TYPES PROPERLY
                                rel_name = to_relation_name(f["additional_fields"][0])
                                rel_id_data_type = models[rel_name].get_id_type()

                                if rel_id_data_type == "":
                                    raise ValueError("Target model for foreign key field {} in model {} has no "
                                                     "primary key.".format(f["name"], model_name))

                                foreign_key_value = str_v
                                if rel_id_data_type == "integer":
                                    foreign_key_value = int(foreign_key_value)

                                if rel_name not in models:
                                    raise ValueError("Unavailable model reference for foreign key field "
                                                     "{} in model {}: {}".format(f["name"], model_name, rel_name))
                                object_data[f["name"]] = models[rel_name].objects.get(pk=foreign_key_value)
                                # TODO!

                            elif f["data_type"] == "point":
                                # WKT Point
                                if re.match(r"^POINT\s*{}$".format(POINT_REGEX), str_v.upper()):
                                    object_data[f["name"]] = str_v.upper()
                                elif re.match(r"^\(?-?\d+(\.\d+)?,?\s+-?\d+(\.\d+)?\)?$", str_v):
                                    # Coerce (5 7), (5, 7), etc. to WKT format
                                    object_data[f["name"]] = "POINT ({})".format(
                                        str_v.replace(",", "").replace("(", "").replace(")", ""))
                                else:
                                    # TODO: NEED TO HANDLE NULLABLE (DONT THINK IT IS NULLABLE) OR BLANK...
                                    raise ValueError("Incorrect value for point field {}: {}".format(f["name"],
                                                                                                     str_v.upper()))

                            elif f["data_type"] == "line string":
                                # WKT Line String
                                if re.match(r"^LINESTRING\s*{}$".format(LINE_STRING_REGEX),
                                            str_v.upper()):
                                    object_data[f["name"]] = str_v.upper()
                                else:
                                    # TODO: NEED TO HANDLE NULLABLE (DONT THINK IT IS NULLABLE) OR BLANK...
                                    raise ValueError("Incorrect value for line string field {}: {}".format(
                                        f["name"], str_v.upper()))

                            elif f["data_type"] == "polygon":
                                # WKT Polygon
                                if re.match(r"^POLYGON\s*{}".format(POLYGON_REGEX),
                                            str_v.upper()):
                                    object_data[f["name"]] = str_v.upper()
                                else:
                                    # TODO: NEED TO HANDLE NULLABLE (DONT THINK IT IS NULLABLE) OR BLANK...
                                    raise ValueError("Incorrect value for polygon field {}: {}".format(
                                        f["name"], str_v.upper()))

                            elif f["data_type"] == "multi point":
                                # WKT Multi Point
                                if re.match(r"MULTIPOINT\s*\(({pt},\s*)*{pt}\s*\)".format(pt=POINT_REGEX),
                                            str_v.upper()):
                                    object_data[f["name"]] = str_v.upper()
                                else:
                                    # TODO: NEED TO HANDLE NULLABLE (DONT THINK IT IS NULLABLE) OR BLANK...
                                    raise ValueError("Incorrect value for multi point field {}: {}".format(
                                        f["name"], str_v.upper()))

                            elif f["data_type"] == "multi line string":
                                if re.match(r"MULTILINESTRING\s*\(({ls},\s*)*{ls}\s*\)".format(ls=LINE_STRING_REGEX),
                                            str_v.upper()):
                                    object_data[f["name"]] = str_v.upper()
                                else:
                                    # TODO: NEED TO HANDLE NULLABLE (DONT THINK IT IS NULLABLE) OR BLANK...
                                    raise ValueError("Incorrect value for multi line string field {}: {}".format(
                                        f["name"], str_v.upper()))

                            elif f["data_type"] == "multi polygon":
                                if re.match(r"MULTIPOLYGON\s*\(({p},\s*)*{p}\s*\)".format(p=POLYGON_REGEX),
                                            str_v.upper()):
                                    object_data[f["name"]] = str_v.upper()
                                else:
                                    # TODO: NEED TO HANDLE NULLABLE (DONT THINK IT IS NULLABLE) OR BLANK...
                                    raise ValueError("Incorrect value for multi polygon field {}: {}".format(
                                        f["name"], str_v.upper()))

                    new_object = self.model(**object_data)
                    new_object.save()

            else:
                # TODO: Handle Errors
                print(form.errors)

            return redirect("..")

        return render(
            request,
            "admin/core/csv_form.html",
            dict(self.admin_site.each_context(request), title="Import CSV", form=ImportCSVForm())
        )

    def get_urls(self):
        urls = super().get_urls()
        mixin_urls = [path("import-csv/", self.import_csv)]

        return mixin_urls + urls
