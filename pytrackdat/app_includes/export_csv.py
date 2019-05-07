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

from django.http import StreamingHttpResponse


class Echo:
    def write(self, value):
        return value


def csv_generator(writer, column_names, queryset):
    # TODO: replace null values with their encoded equivalents from the design file
    yield writer.writerow(column_names)
    for item in queryset:
        yield writer.writerow([getattr(item, c) for c in column_names])


# noinspection PyProtectedMember
class ExportCSVMixin:
    def export_csv(self, _request, queryset):
        # TODO: replace null values with their encoded equivalents from the design file

        column_names = [c.name for c in self.model._meta.fields]

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)

        response = StreamingHttpResponse(csv_generator(writer, column_names, queryset),
                                         content_type="text/csv; charset=utf-8")

        response["Content-Disposition"] = "attachment; filename={}.csv".format(self.model.__name__.lower())

        return response

    export_csv.short_description = "Export selected as CSV"
