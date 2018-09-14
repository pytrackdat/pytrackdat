import csv
import re

import core.models

from django import forms
from django.shortcuts import redirect, render
from django.urls import path

from datetime import datetime
from decimal import *
from io import TextIOWrapper


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

                ptd_info = self.model.ptd_info()
                headers = [h.strip() for h in reader.fieldnames if h != ""]
                header_fields = {h: tuple([f for f in ptd_info if f["csv_name"] == h]) for h in headers}

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

                            elif f["data_type"] == "foreign key":
                                # TODO!
                                pass

                            elif f["data_type"] == "integer":
                                if re.match(r"^([+-]?[1-9]\d*|0)$", str_v):
                                    object_data[f["name"]] = int(str_v)
                                    break
                                elif f["nullable"]:
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
                                        object_data[f["name"]] = None
                                    else:
                                        raise ValueError("Value for text field {} is not one of the available choices "
                                                         "{}: {}".format(f["name"], tuple(choices), str_v))

                                object_data[f["name"]] = str_v
                                break

                            elif f["data_type"] == "date":
                                # TODO: More date formats
                                # TODO: Further validation
                                if re.match(r"^[1-2]\d{3}-\d{1,2}-\d{1,2}$", str_v):
                                    object_data[f["name"]] = datetime.strptime(str_v, "%Y-%m-%d")
                                    break
                                elif f["nullable"]:
                                    object_data[f["name"]] = None
                                else:
                                    raise ValueError("Incorrect value for date field {}: {}".format(f["name"], str_v))

                    new_object = self.model(**object_data)
                    new_object.save()

            else:
                # TODO: Handle Errors
                print(form.errors)

            return redirect("..")

        return render(
            request,
            "admin/core/csv_form.html",
            dict(self.admin_site.each_context(request), form=ImportCSVForm())
        )

    def get_urls(self):
        urls = super().get_urls()
        mixin_urls = [path("import-csv/", self.import_csv)]

        return mixin_urls + urls
