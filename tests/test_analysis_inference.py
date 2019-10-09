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

import pytrackdat.analysis as pa


UNIQUE_INT_LIST = [str(i) for i in range(1, 21)]
NULL_INT_LIST = UNIQUE_INT_LIST + [""]
REPEATED_INT_LIST = ["999"] * 20

UNIQUE_CONSISTENT_DECIMAL_LIST = ["{}.{}".format(i, j) for i, j in zip(range(10, 51), range(51, 100))]
MIXED_INTS_AND_DECIMALS = ("1", "1.1", "1.20", "2", "2.1", "2.20", "2.300")


class TestAnalysisInference(unittest.TestCase):
    def test_manual_key_inference(self):
        inference = pa.infer_column_type(UNIQUE_INT_LIST, False)
        self.assertDictEqual(inference, {
            "detected_type": "manual key",
            "nullable": False,
            "null_values": (),
            "choices": (),
            "max_length": -1,
            "is_key": True,
            "include_alternate": False,
            "max_seen_decimals": -1
        })

    def test_unique_int_inference_with_existing_key(self):
        inference = pa.infer_column_type(UNIQUE_INT_LIST, True)
        self.assertDictEqual(inference, {
            "detected_type": "integer",
            "nullable": False,
            "null_values": (),
            "choices": (),
            "max_length": -1,
            "is_key": False,
            "include_alternate": False,
            "max_seen_decimals": -1
        })

    def test_nullable_int(self):
        inference = pa.infer_column_type(NULL_INT_LIST, True)
        self.assertDictEqual(inference, {
            "detected_type": "integer",
            "nullable": True,
            "null_values": (),  # TODO: DO WE WANT NULL VALUES HERE?
            "choices": (),
            "max_length": -1,
            "is_key": False,
            "include_alternate": False,
            "max_seen_decimals": -1
        })

    def test_repeated_int(self):
        inference = pa.infer_column_type(REPEATED_INT_LIST, False)
        self.assertDictEqual(inference, {
            "detected_type": "integer",
            "nullable": False,
            "null_values": (),
            "choices": (),
            "max_length": -1,
            "is_key": False,
            "include_alternate": False,
            "max_seen_decimals": -1
        })

    def test_consistent_decimal(self):
        inference = pa.infer_column_type(UNIQUE_CONSISTENT_DECIMAL_LIST, True)
        self.assertDictEqual(inference, {
            "detected_type": "decimal",
            "nullable": False,
            "null_values": (),
            "choices": (),
            "max_length": 11,  # 4 digits + decimal point + 2 digits after decimal + (constant 4) TODO: good formula?
            "is_key": False,
            "include_alternate": False,
            "max_seen_decimals": 2
        })

    def test_mix_of_ints_and_decimals(self):
        inference = pa.infer_column_type(MIXED_INTS_AND_DECIMALS, True)
        self.assertDictEqual(inference, {
            "detected_type": "decimal",
            "nullable": False,
            "null_values": (),
            "choices": (),
            "max_length": 12,  # 4 digits + decimal point + 3 digits after decimal + (constant 4) TODO: good formula?
            "is_key": False,
            "include_alternate": False,
            "max_seen_decimals": 3
        })
