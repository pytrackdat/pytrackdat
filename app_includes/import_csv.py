import csv

from django import forms
from django.shortcuts import redirect, render
from django.urls import path


class ImportCSVForm(forms.Form):
    csv_file = forms.FileField()


class ImportCSVMixin:
    def import_csv(self, request):
        if request.method == "POST":
            form = ImportCSVForm(request.POST)
            if form.is_valid():
                csv_file = form.cleaned_data["csv_file"]
                reader = csv.reader(csv_file)
                # TODO

            return redirect("..")

        return render(
            request,
            "admin/core/csv_form.html",
            dict(self.admin_site.each_context(request), form=ImportCSVForm())
        )

    def get_urls(self):
        urls = super().get_urls()
        mixin_urls = [path("import-csv/", self.import_csv)]

        return urls + mixin_urls
