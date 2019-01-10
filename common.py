import re

# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018 the PyTrackDat authors.
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

VERSION = "0.1.0"
COPYRIGHT_DATES = "2018"

PYTHON_KEYWORDS = ["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
                   "def", "del", "else", "elif", "except", "finally", "for", "from", "global", "if", "import", "in",
                   "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]

DATA_TYPES = ["auto key", "manual key", "integer", "float", "decimal", "boolean", "text", "date", "time", "foreign key"]


RE_DATE_YMD_D = re.compile("^[1-2]\d{3}-\d{1,2}-\d{1,2}$")
RE_DATE_YMD_S = re.compile("^[1-2]\d{3}/\d{1,2}/\d{1,2}$")
RE_DATE_DMY_D = re.compile("^\d{1,2}-\d{1,2}-[1-2]\d{3}$")
RE_DATE_DMY_S = re.compile("^\d{1,2}/\d{1,2}/[1-2]\d{3}$")

RE_MULTIPLE_UNDERSCORES = re.compile("[_]{2,}")

PDT_RELATION_PREFIX = "PyTrackDat"


def field_to_py_code(field):
    field = field + "_field" if field in PYTHON_KEYWORDS else field
    field = re.sub(RE_MULTIPLE_UNDERSCORES, "_", field)
    return field


def to_relation_name(name):
    python_relation_name = PDT_RELATION_PREFIX + "".join([n.capitalize() for n in name.split("_")])

    if python_relation_name in PYTHON_KEYWORDS:
        python_relation_name += "Class"

    return python_relation_name


def print_license():
    print("""PyTrackDat v{}  Copyright (C) {} the PyTrackDat authors.
This program comes with ABSOLUTELY NO WARRANTY; see LICENSE for details.
""".format(VERSION, COPYRIGHT_DATES))
