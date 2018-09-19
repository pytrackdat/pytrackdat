# import rpy2.robjects.packages as rpackages
# from rpy2.robjects.vectors import StrVector

import csv

from django.http import HttpResponse


class ExportLabelsMixin:
    def export_labels(self, _request, queryset):
        id_vector = [o.pk for o in queryset]

        # base = rpackages.importr("base")
        #
        # utils = rpackages.importr("utils")
        # utils.chooseCRANmirror(ind=1)
        # utils.install_packages(StrVector(("devtools",)))
        #
        # devtools = rpackages.importr("devtools")
        # devtools.install_github("yihanwu/baRcodeR", build_vignettes=False)
        #
        # barcoder = rpackages.importr("baRcodeR")
        # barcoder.create_PDF(Labels=StrVector(id_vector), name=base.file.path(base.tempdir(), "example"))
        #
        # print(base.tempdir())

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = "attachment; filename=labels_{}.csv".format(self.model.__name__.lower())

        writer = csv.writer(response)
        for o_id in id_vector:
            writer.writerow([o_id])

        return response

    export_labels.short_description = "Export baRcodeR CSV ID list for selected"
