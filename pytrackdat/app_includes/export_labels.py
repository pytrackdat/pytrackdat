# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018 the PyTrackDat authors.
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
import os
import shutil
import subprocess

from django.http import FileResponse, HttpResponse

have_r = shutil.which("Rscript") is not None


class ExportLabelsMixin:
    def export_labels(self, _request, queryset):
        model_name = self.model.get_label_name()
        id_vector = ["{}\n{}".format(model_name, o.pk) for o in queryset]

        response = HttpResponse(status=500)

        for f in os.listdir("."):
            if f.startswith("labels-"):
                os.remove(os.path.join(".", f))

        if have_r:
            # TODO: Prefix for IDs
            result = subprocess.run(["Rscript", "./export_labels.R"] + id_vector, stdout=subprocess.PIPE, check=True)
            path = result.stdout.decode("utf-8").split("\n")[-1] + ".pdf"
            response = FileResponse(open(path, "rb"), as_attachment=True,
                                    filename="labels_{}.pdf".format(self.model.__name__.lower()))

        return response

    export_labels.short_description = "Export baRcodeR labels (PDF) for selected"
