# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2021 the PyTrackDat authors.
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

import sys

from advanced_filters.admin import AdminAdvancedFiltersMixin
from django.conf import settings
from django.contrib import admin
from django.db import models
from reversion.admin import VersionAdmin

from pytrackdat.common import DT_BOOLEAN, PDT_RELATION_PREFIX, Relation
from . import models as core_models
from .export_csv import ExportCSVMixin
from .import_csv import ImportCSVMixin
from .export_labels import ExportLabelsMixin
from .charts import ChartsMixin

if settings.PTD_GIS_MODE:
    from django.contrib.gis import admin as gis_admin

admin.site.site_header = f"PyTrackDat: {settings.PTD_SITE_NAME}"

for name in dir(core_models):
    Cls = getattr(core_models, name)
    if not name.startswith(PDT_RELATION_PREFIX) or type(Cls) != models.base.ModelBase:
        continue

    # noinspection PyUnresolvedReferences
    relation: Relation = Cls.ptd_relation  # TODO: Abstract mixin for this stuff

    list_display_fields = tuple(f.name for f in relation.fields if f.show_in_table)
    list_filter_fields = tuple(f.name for f in relation.fields
                               if f.data_type == DT_BOOLEAN or f.choices is not None)

    advanced_filter_fields = tuple(r.name for r in relation.fields)

    admin_name = f"{name}Admin"

    NewAdmin = type(admin_name, (
        ExportCSVMixin,
        ImportCSVMixin,
        ExportLabelsMixin,
        ChartsMixin,
        AdminAdvancedFiltersMixin,
        VersionAdmin,
        *((gis_admin.GeoModelAdmin,) if settings.PTD_GIS_MODE else ()),
    ), {
        "__module__": __name__,
        "map_template": "admin/core/gis/openlayers.html",
        "change_list_template": "admin/core/change_list.html",
        "actions": ('export_csv', 'export_labels'),
        **({"list_display": list_display_fields} if len(list_display_fields) > 1 else {}),
        **({"list_filter": list_filter_fields} if list_filter_fields else {}),
        **({"advanced_filter_fields": advanced_filter_fields} if advanced_filter_fields else {}),
    })

    setattr(sys.modules[__name__], admin_name, admin.register(Cls)(NewAdmin))
