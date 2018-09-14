import csv

from django import forms
from django.shortcuts import redirect, render
from django.urls import path

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
                headers = [h for h in reader.fieldnames if h != ""]
                print(self.model.ptd_info())
                # TODO
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
