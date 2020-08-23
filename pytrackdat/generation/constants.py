# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2020 the PyTrackDat authors.
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

from ..common import DT_INTEGER, DT_FLOAT, VERSION


__all__ = [
    "PRODUCTION_SITE_URL_PROMPT",

    "ADMIN_FILE_HEADER_TEMPLATE",
    "MODEL_ADMIN_TEMPLATE",

    "MODELS_FILE_HEADER",
    "MODEL_TEMPLATE",

    "API_FILE_HEADER",
    "MODEL_SERIALIZER_TEMPLATE",
    "MODEL_VIEWSET_TEMPLATE",
    "MODEL_ROUTER_REGISTRATION_TEMPLATE",

    "URL_OLD",
    "URL_NEW",
    "DEBUG_OLD",
    "DEBUG_NEW",
    "ALLOWED_HOSTS_OLD",
    "ALLOWED_HOSTS_NEW",
    "INSTALLED_APPS_OLD",
    "INSTALLED_APPS_NEW",
    "INSTALLED_APPS_NEW_GIS",
    "STATIC_OLD",
    "STATIC_NEW",
    "REST_FRAMEWORK_SETTINGS",
    "SPATIALITE_SETTINGS",
    "DATABASE_ENGINE_NORMAL",
    "DATABASE_ENGINE_GIS",
    "DISABLE_MAX_FIELDS",

    "BASIC_NUMBER_TYPES",
]


# Prompts

PRODUCTION_SITE_URL_PROMPT = "Please enter the production site URL, without 'www.' or 'http://': "


# Model-Relevant Templates


ADMIN_FILE_HEADER_TEMPLATE = """# Generated using PyTrackDat v{}
from django.contrib import admin
from advanced_filters.admin import AdminAdvancedFiltersMixin
from reversion.admin import VersionAdmin

from core.models import *
from .export_csv import ExportCSVMixin
from .import_csv import ImportCSVMixin
from .export_labels import ExportLabelsMixin
from .charts import ChartsMixin

if {{gis_mode}}:
    from django.contrib.gis import forms as gis_forms, admin as gis_admin
    from django.contrib.gis.db import models as gis_models

admin.site.site_header = "PyTrackDat: {{site_name}}"

""".format(VERSION)

MODEL_ADMIN_TEMPLATE = """
@admin.register({relation_name})
class {relation_name}Admin(
    ExportCSVMixin,
    ImportCSVMixin,
    ExportLabelsMixin,
    ChartsMixin,
    AdminAdvancedFiltersMixin,
    VersionAdmin, {admin_class}
):
    map_template = "admin/core/gis/openlayers.html"
    change_list_template = 'admin/core/change_list.html'
    actions = ('export_csv', 'export_labels')
{list_display}{list_filter}{advanced_filter_fields}
"""


MODELS_FILE_HEADER = """# Generated using PyTrackDat v{version}
from {models_path} import models

"""

MODEL_TEMPLATE = """
class {name}(models.Model):
    @classmethod
    def ptd_info(cls):
        return {fields}

    @classmethod
    def get_label_name(cls):
        return '{short_name}'

    @classmethod
    def get_id_type(cls):
        return '{id_type}'

    def __str__(self):
        return '{short_name}: {{}}'.format(self.pk)

    class Meta:
        # Use short name as verbose name to not show the PyTrackDat prefix
        verbose_name = '{short_name}'

    pdt_created_at = models.DateTimeField(auto_now_add=True, null=False)
    pdt_modified_at = models.DateTimeField(auto_now=True, null=False)

{model_fields}
"""


# API Specification Code

API_FILE_HEADER = """# Generated using PyTrackDat v{version}

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from core.models import *
from pytrackdat_snapshot_manager.models import Snapshot

api_router = DefaultRouter()


# TODO: Move to snapshot app?
class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshot
        fields = "__all__"


# TODO: Move to snapshot app?
class SnapshotViewSet(viewsets.ModelViewSet):
    queryset = Snapshot.objects.all()
    serializer_class = SnapshotSerializer


api_router.register(r'snapshots', SnapshotViewSet)


class MetaViewSet(viewsets.ViewSet):
    def list(self, _request):
        return Response({{
            "site_name": "{site_name}",
            "gis_mode": {gis_mode},
            "relations": {relations}
        }})


api_router.register(r'meta', MetaViewSet, basename='meta')


"""

MODEL_SERIALIZER_TEMPLATE = """
class {relation_name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {relation_name}
        fields = {fields}
"""

MODEL_VIEWSET_TEMPLATE = """
class {relation_name}ViewSet(viewsets.ModelViewSet):
    queryset = {relation_name}.objects.all()
    serializer_class = {relation_name}Serializer
    filterset_fields = {filterset_fields}
    @action(detail=False)
    def categorical_counts(self, _request):
        categorical_fields = {categorical_fields}
        categorical_choices = {categorical_choices}
        counts = {{f: {{c: 0 for c in categorical_choices[f]}} for f in categorical_fields}}
        for row in {relation_name}.objects.values():
            for f in categorical_fields:
                counts[f][row[f]] += 1
        return Response(counts)
"""

MODEL_ROUTER_REGISTRATION_TEMPLATE = """
api_router.register(r'data/{relation_name_lower}', {relation_name}ViewSet)
"""

# Settings Code

URL_OLD = """urlpatterns = [
    path('admin/', admin.site.urls),
]"""
URL_NEW = """from django.urls import include

from core.api import api_router
from pytrackdat_snapshot_manager.views import urls

urlpatterns = [
    path('', admin.site.urls),
    path('api/', include(api_router.urls)),
    path('advanced_filters/', include('advanced_filters.urls')),
] + urls"""

DEBUG_OLD = "DEBUG = True"
DEBUG_NEW = "DEBUG = not (os.getenv('DJANGO_ENV') == 'production')"

ALLOWED_HOSTS_OLD = "ALLOWED_HOSTS = []"
ALLOWED_HOSTS_NEW = "ALLOWED_HOSTS = ['127.0.0.1', '{}'] if (os.getenv('DJANGO_ENV') == 'production') else []"

INSTALLED_APPS_OLD = """INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]"""

INSTALLED_APPS_NEW = """INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'core.apps.CoreConfig',
    'pytrackdat_snapshot_manager',

    'advanced_filters',
    'rest_framework',
    'reversion',
]"""

INSTALLED_APPS_NEW_GIS = INSTALLED_APPS_NEW.replace(
    "'django.contrib.staticfiles',",
    """'django.contrib.staticfiles',

    'django.contrib.gis',

    'rest_framework_gis',"""
)

STATIC_OLD = "STATIC_URL = '/static/'"
STATIC_NEW = """STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')"""

REST_FRAMEWORK_SETTINGS = """
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,  # Default
}
"""

SPATIALITE_SETTINGS = """
SPATIALITE_LIBRARY_PATH='{}' if (os.getenv('DJANGO_ENV') != 'production') else None
"""

DATABASE_ENGINE_NORMAL = "django.db.backends.sqlite3"
DATABASE_ENGINE_GIS = "django.contrib.gis.db.backends.spatialite"

DISABLE_MAX_FIELDS = "\nDATA_UPLOAD_MAX_NUMBER_FIELDS = None\n"


# Other Constants

BASIC_NUMBER_TYPES = {
    DT_INTEGER: "IntegerField",
    DT_FLOAT: "FloatField",
}
