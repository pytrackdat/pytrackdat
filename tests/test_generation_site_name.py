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

from pytrackdat.generation import GenerationError, sanitize_and_check_site_name


class TestGenerationSiteName(unittest.TestCase):
    def test_site_name_invalid_chars(self):
        with self.assertRaises(GenerationError):
            # TODO: Check error message
            sanitize_and_check_site_name("aaa!!!")

    def test_site_name_conflict(self):
        with self.assertRaises(GenerationError):
            # TODO: Check error message
            sanitize_and_check_site_name("unittest")
