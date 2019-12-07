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

from pytrackdat.generation import design_to_relation_fields
from pytrackdat.generation.errors import GenerationError


class TestDesignFileParsing(unittest.TestCase):
    def test_two_primary_keys(self):
        with self.assertRaises(GenerationError):
            with open("./tests/design_files/two_primary_keys_1.csv") as tf:
                design_to_relation_fields(tf, False)
        with self.assertRaises(GenerationError):
            with open("./tests/design_files/two_primary_keys_2.csv") as tf:
                design_to_relation_fields(tf, False)
        with self.assertRaises(GenerationError):
            with open("./tests/design_files/two_primary_keys_3.csv") as tf:
                design_to_relation_fields(tf, False)

    def test_invalid_data_types(self):
        with self.assertRaises(GenerationError):
            with open("./tests/design_files/invalid_data_type.csv") as tf:
                design_to_relation_fields(tf, False)

            with open("./tests/design_files/point_field.csv") as tf:
                # GIS mode is off, so an error should be raised.
                design_to_relation_fields(tf, False)
