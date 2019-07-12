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

import unittest

import pytrackdat.generation as pg

AUTO_KEY_FIELD = {
    # TODO: FILL IN OTHER MISC. INFO
    "description": "test \\'auto\\' key"
}


class TestGenerationFormatters(unittest.TestCase):
    def test_help_text_cleaner(self):
        self.assertEqual(pg.clean_field_help_text("\\"), "\\\\")
        self.assertEqual(pg.clean_field_help_text("'"), "\\'")
        self.assertEqual(pg.clean_field_help_text("\\'"), "\\\\\\'")

    def test_auto_key_formatter(self):
        print(pg.auto_key_formatter(AUTO_KEY_FIELD))
        self.assertEqual(
            pg.auto_key_formatter(AUTO_KEY_FIELD),
            "models.AutoField(primary_key=True, help_text='test \\\\\\'auto\\\\\\' key')"
        )
