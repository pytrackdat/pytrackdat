from django.contrib import admin
from django.urls import include, path

from pytrackdat.ptd_site.core.api import api_router
from pytrackdat.ptd_site.snapshot_manager.views import urls as snapshot_urls

urlpatterns = [
    path("", admin.site.urls),
    path("api/", include(api_router.urls)),
    path("advanced_filters/", include("advanced_filters.urls")),
    *snapshot_urls,
]
