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
