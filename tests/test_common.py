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

import io
import unittest

from contextlib import redirect_stdout

from pytrackdat.common import *


class TestCommonMethods(unittest.TestCase):
    def test_data_type_validity(self):
        for dt in DATA_TYPES:
            self.assertTrue(valid_data_type(dt, False))

        for dt in GIS_DATA_TYPES:
            self.assertFalse(valid_data_type(dt, False))

        for dt in DATA_TYPES + GIS_DATA_TYPES:
            self.assertTrue(valid_data_type(dt, True))

    def test_multiple_underscores(self):
        cases = [("a__b", "a_b"), ("___c", "_c"), ("d_____", "d_")]
        for b, a in cases:
            self.assertEqual(collapse_multiple_underscores(b), a)

    def test_python_id_sanitization(self):
        cases = [("A b", "A_b"), ("a*D(#b", "aDb"), ("c-----4", "c_4")]
        for b, a in cases:
            self.assertEqual(sanitize_python_identifier(b), a)

    def test_fieldify(self):
        cases = [("A-84t___B", "a_84t_b"), ("await", "await_field")]
        for b, a in cases:
            self.assertEqual(field_to_py_code(b), a)

    def test_data_type_standardization(self):
        cases = [("Auto   _  keY", "auto key"), ("ForEign______     \tkey", "foreign key")]
        for b, a in cases:
            self.assertEqual(standardize_data_type(b), a)

    def test_string_to_relation_name(self):
        cases = [("hello____ world", PDT_RELATION_PREFIX + "HelloWorld"),
                 ("Countries", PDT_RELATION_PREFIX + "Country"),
                 ("Specimens", PDT_RELATION_PREFIX + "Specimen")]
        for b, a in cases:
            self.assertEqual(to_relation_name(b), a)

    def test_license_printing(self):
        lf = io.StringIO()
        with redirect_stdout(lf):
            print_license()
            self.assertGreater(len(lf.getvalue()), 0)
