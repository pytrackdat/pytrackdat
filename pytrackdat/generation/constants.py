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

from ..common import *


__all__ = [
    "ADMIN_FILE_HEADER_TEMPLATE",
    "MODEL_ADMIN_TEMPLATE",

    "MODELS_FILE_HEADER",
    "MODEL_TEMPLATE",

    "SNAPSHOT_ADMIN_FILE",
    "SNAPSHOT_MODEL",

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

admin.site.site_header = "PyTrackDat: {{}}"

""".format(VERSION)

MODEL_ADMIN_TEMPLATE = """
@admin.register({relation_name})
class {relation_name}Admin(
    ExportCSVMixin,
    ImportCSVMixin,
    ExportLabelsMixin,
    ChartsMixin,
    AdminAdvancedFiltersMixin,
    VersionAdmin
):
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
        return '{label_name}'

    @classmethod
    def get_id_type(cls):
        return '{id_type}'

    class Meta:
        verbose_name = '{verbose_name}'

    pdt_created_at = models.DateTimeField(auto_now_add=True, null=False)
    pdt_modified_at = models.DateTimeField(auto_now=True, null=False)

    {model_fields}
"""


# Snapshot Specification Code

SNAPSHOT_ADMIN_FILE = """# Generated using PyTrackDat v{}
from django.contrib import admin
from django.utils.html import format_html
from advanced_filters.admin import AdminAdvancedFiltersMixin

from snapshot_manager.models import *


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    exclude = ('snapshot_type', 'size', 'name', 'reason')
    list_display = ('__str__', 'download_link', 'reason')

    def download_link(self, obj):
        return format_html('<a href="{{url}}">Download Database Snapshot</a>',
                           url='/snapshots/' + str(obj.pk) + '/download/')

    download_link.short_description = 'Download Link'

""".format(VERSION)

SNAPSHOT_MODEL = """import os
import shutil
from datetime import datetime

import {site_name}.settings as settings

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.http import HttpResponse, Http404


class Snapshot(models.Model):
    pdt_created_at = models.DateTimeField(auto_now_add=True, null=False)
    pdt_modified_at = models.DateTimeField(auto_now=True, null=False)
    snapshot_type = models.TextField(help_text='Created by whom?', max_length=6, default='manual',
                                     choices=(('auto', 'Automatic'), ('manual', 'Manual')), null=False, blank=False)
    name = models.TextField(help_text='Name of snapshot file', max_length=127, null=False, blank=False)
    reason = models.TextField(help_text='Reason for snapshot creation', max_length=127, null=False, blank=True,
                              default='Manually created')
    size = models.IntegerField(help_text='Size of database (in bytes)', null=False)

    def __str__(self):
        return self.snapshot_type + " snapshot (" + str(self.name) + "; size: " + str(self.size) + " bytes)"

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                # TODO: THIS ONLY WORKS WITH SQLITE
                # Newly-created snapshot

                name = "snapshot-" + str(datetime.utcnow()).replace(" ", "_").replace(":", "-") + ".sqlite3"

                shutil.copyfile(settings.DATABASES['default']['NAME'],
                                os.path.join(settings.BASE_DIR, "snapshots", name))

                self.name = name
                self.size = os.path.getsize(os.path.join(settings.BASE_DIR, "snapshots", name))

        super(Snapshot, self).save(*args, **kwargs)


@receiver(pre_delete, sender=Snapshot)
def delete_snapshot_file(sender, instance, **kwargs):
    try:
        os.remove(os.path.join(settings.BASE_DIR, "snapshots", instance.name))
    except OSError:
        print("Error deleting snapshot")
        # TODO: prevent deletion in some way?


@login_required
def download_view(request, id):
    try:
        snapshot = Snapshot.objects.get(pk=id)
        path = os.path.join(settings.BASE_DIR, 'snapshots', snapshot.name)
        if os.path.exists(path):
            # TODO
            with open(path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/x-sqlite3')
                response['Content-Disposition'] = 'inline; filename=' + snapshot.name
                return response
        else:
            raise Http404('Snapshot file does not exist (database inconsistency!)')

    except Snapshot.DoesNotExist:
        raise Http404('Snapshot does not exist')

"""


# API Specification Code

API_FILE_HEADER = """# Generated using PyTrackDat v{version}

from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from core.models import *
from snapshot_manager.models import Snapshot

api_router = DefaultRouter()


class SnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snapshot
        fields = ['pdt_created_at', 'pdt_modified_at', 'snapshot_type', 'name', 'reason', 'size']


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
    @action(detail=False)
    def categorical_counts(self, _request):
        categorical_fields = {categorical_fields}
        categorical_choices = {categorical_choices}
        counts = {f: {c: 0 for c in categorical_choices[f]} for f in categorical_fields}
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
from snapshot_manager.models import download_view

urlpatterns = [
    path('', admin.site.urls),
    path('api/', include(api_router.urls)),
    path('snapshots/<int:id>/download/', download_view, name='snapshot-download'),
    path('advanced_filters/', include('advanced_filters.urls')),
]"""

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
    'core.apps.CoreConfig',
    'snapshot_manager.apps.SnapshotManagerConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'reversion',
    'advanced_filters',
    'rest_framework',
]"""

INSTALLED_APPS_NEW_GIS = INSTALLED_APPS_NEW.replace(
    "'django.contrib.staticfiles',",
    """'django.contrib.staticfiles',

    'django.contrib.gis',"""
)

STATIC_OLD = "STATIC_URL = '/static/'"
STATIC_NEW = """STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')"""

REST_FRAMEWORK_SETTINGS = """
REST_FRAMEWORK = {'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated']}
"""

SPATIALITE_SETTINGS = """
SPATIALITE_LIBRARY_PATH='{}' if (os.getenv('DJANGO_ENV') != 'production') else None
"""

DATABASE_ENGINE_NORMAL = "django.db.backends.sqlite3"
DATABASE_ENGINE_GIS = "django.contrib.gis.db.backends.spatialite"

DISABLE_MAX_FIELDS = "\nDATA_UPLOAD_MAX_NUMBER_FIELDS = None\n"


# Other Constants

BASIC_NUMBER_TYPES = {
    "integer": "IntegerField",
    "float": "FloatField",
}
