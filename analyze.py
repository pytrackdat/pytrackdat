#!/usr/bin/env python3

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

# To lowercase
# Replace whitespace with underline
# Analyze domain and find out:
#    integer with one other value -> nullable integer
#    integer with no other value -> integer
#    decimal with constant digits -> decimal (max: length plus 2)
#    y/n, t/f, true/false -> boolean
#    y/n/u, y/n/blank, etc. -> nullable boolean
#    mm/dd/yyyy, dd/mm/yyyy, yyyy-mm-dd -> date (if ONE other value that doesn't match, nullable) TODO
#    HH:MM pm, HH:MMpm, HH:MM, etc -> time (if ONE other value that doesn't match, nullable) TODO
#    text where the choices are way less than the number of rows -> max length text choice field
#    highly deviant text (excluding blanks) -> text field

# LIMITATION: memory must be enough to ingest the CSV file to analyze

from pytrackdat.analysis import main

if __name__ == "__main__":
    main()
