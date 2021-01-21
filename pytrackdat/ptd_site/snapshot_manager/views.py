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

import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.urls import path

from .models import Snapshot


@login_required
def download_view(request, snapshot_id):
    try:
        snapshot = Snapshot.objects.get(pk=snapshot_id)
        snapshot_path = os.path.join(settings.BASE_DIR, "snapshots", snapshot.name)
        if os.path.exists(snapshot_path):
            # TODO
            with open(snapshot_path, "rb") as f:
                response = HttpResponse(f.read(), content_type="application/x-sqlite3")
                response["Content-Disposition"] = "inline; filename={}".format(snapshot.name)
                return response
        else:
            raise Http404("Snapshot file does not exist (database inconsistency!)")

    except Snapshot.DoesNotExist:
        raise Http404("Snapshot does not exist")


urls = [
    path("snapshots/<int:snapshot_id>/download/", download_view, name="snapshot-download"),
]
