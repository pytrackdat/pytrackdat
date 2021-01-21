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
import shutil
from datetime import datetime

from django.conf import settings
from django.db import models, transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Snapshot(models.Model):
    pdt_created_at = models.DateTimeField(auto_now_add=True, null=False)
    pdt_modified_at = models.DateTimeField(auto_now=True, null=False)
    snapshot_type = models.TextField(help_text="Created by whom?", max_length=6, default='manual',
                                     choices=(("auto", "Automatic"), ("manual", "Manual")), null=False, blank=False)
    name = models.TextField(help_text="Name of snapshot file", max_length=127, null=False, blank=False)
    reason = models.TextField(help_text="Reason for snapshot creation", max_length=127, null=False, blank=True,
                              default="Manually created")
    size = models.IntegerField(help_text="Size of database (in bytes)", null=False)

    def __str__(self):
        return "{} snapshot ({}; size: {} bytes)".format(self.snapshot_type, str(self.name), str(self.size))

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                # TODO: THIS ONLY WORKS WITH SQLITE
                # Newly-created snapshot

                name = "snapshot-{}.sqlite3".format(str(datetime.utcnow()).replace(" ", "_").replace(":", "-"))

                shutil.copyfile(settings.DATABASES["default"]["NAME"],
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
