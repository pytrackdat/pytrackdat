from django.shortcuts import render
from django.urls import path

class ChartsMixin:
    def charts(self, request):
        return render(request, "admin/core/charts.html", dict(self.admin_site.each_context(request), title="Charts"))

    def get_urls(self):
        urls = super().get_urls()
        mixin_urls = [path("charts/", self.charts)]

        return mixin_urls + urls
