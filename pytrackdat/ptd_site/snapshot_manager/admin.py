# PyTrackDat Snapshot Manager is a Django app for versioning SQLite databases.
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

from django.contrib import admin
from django.utils.html import format_html

from pytrackdat.ptd_site.snapshot_manager.models import Snapshot


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    exclude = ('snapshot_type', 'size', 'name', 'reason')
    list_display = ('__str__', 'download_link', 'reason')

    def download_link(self, obj):
        return format_html('<a href="{url}">Download Database Snapshot</a>',
                           url='/snapshots/{}/download/'.format(obj.pk))

    download_link.short_description = 'Download Link'
