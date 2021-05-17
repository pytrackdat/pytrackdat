from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from pytrackdat.ptd_site.core.api import api_router
from pytrackdat.ptd_site.snapshot_manager.views import urls as snapshot_urls

urlpatterns = [
    *snapshot_urls,
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(api_router.urls)),
    path("advanced_filters/", include("advanced_filters.urls")),
    path("", admin.site.urls),
]
