import csv

from django.http import StreamingHttpResponse


class Echo:
    def write(self, value):
        return value


def csv_generator(writer, column_names, queryset):
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
