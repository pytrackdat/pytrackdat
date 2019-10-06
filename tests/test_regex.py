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

import pytrackdat.common as pc


VALID_INTEGERS = ("1", "0", "-1", "-1000", "-4302941", "+43902", "+10000", "+5", "5", "304923")
VALID_HUMAN_INTEGERS = ("321,423,423", "32,000", "-55,000", "-66,432", "+31,543", "+32,042,423,543")


class TestRegex(unittest.TestCase):
    def test_valid_integers(self):
        for i in VALID_INTEGERS:
            self.assertRegex(i, pc.RE_INTEGER)

    def test_valid_human_integers(self):
        for i in VALID_HUMAN_INTEGERS:
            self.assertRegex(i, pc.RE_INTEGER_HUMAN)
            self.assertRegex(i.replace(",", " "), pc.RE_INTEGER_HUMAN)
