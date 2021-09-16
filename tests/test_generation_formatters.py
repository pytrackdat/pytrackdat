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

import os

from django.core.wsgi import get_wsgi_application
from django.db import models
from django.test import TestCase as DjangoTestCase

import pytrackdat.common as pc
import pytrackdat.design_file.formatters as pf

os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
    "DJANGO_SETTINGS_MODULE", "pytrackdat.ptd_site.ptd_site.settings")

os.environ["PTD_DESIGN_FILE"] = "./tests/design_files/dummy.csv"

# Make test case class happy
application = get_wsgi_application()


AUTO_KEY_FIELD = pc.RelationField(
    csv_names=(),
    name="test_id",
    data_type="auto key",
    nullable=False,
    null_values=(),
    default="",
    description="test \\'auto\\' key",
    show_in_table=True,
    additional_fields=(),  # no additional fields
)


class TestGenerationFormatters(DjangoTestCase):
    def test_auto_key_formatter(self):
        i = pf.auto_key_formatter(AUTO_KEY_FIELD)
        assert isinstance(i, models.AutoField)
        assert i.primary_key
        assert i.help_text == AUTO_KEY_FIELD.description
