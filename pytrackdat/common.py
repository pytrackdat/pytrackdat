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

import re


__all__ = ["VERSION",
           "COPYRIGHT_DATES",
           "PYTHON_KEYWORDS",
           "DATA_TYPES",
           "GIS_DATA_TYPES",
           "DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS",
           "RE_INTEGER",
           "RE_INTEGER_HUMAN",
           "RE_DECIMAL",
           "RE_DECIMAL_HUMAN",
           "RE_NUMBER_GROUP_SEPARATOR",
           "RE_DATE_YMD_D",
           "RE_DATE_YMD_S",
           "RE_DATE_DMY_D",
           "RE_DATE_DMY_S",
           "RE_MULTIPLE_UNDERSCORES",
           "RE_NON_IDENTIFIER_CHARACTERS",
           "RE_SEPARATOR_CHARACTERS",
           "RE_MULTIPLE_WHITESPACE_CHARACTERS",
           "BOOLEAN_TRUE_VALUES",
           "BOOLEAN_FALSE_VALUES",
           "BOOLEAN_TF_PAIRS",
           "DATE_FORMATS",
           "PDT_RELATION_PREFIX",
           "valid_data_type",
           "collapse_multiple_underscores",
           "sanitize_python_identifier",
           "field_to_py_code",
           "standardize_data_type",
           "to_relation_name",
           "print_license",
           "exit_with_error"]


VERSION = "0.2.1"
COPYRIGHT_DATES = "2018-2019"

PYTHON_KEYWORDS = ["False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
                   "def", "del", "else", "elif", "except", "finally", "for", "from", "global", "if", "import", "in",
                   "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]

DATA_TYPES = ["auto key", "manual key", "integer", "float", "decimal", "boolean", "text", "date", "time", "foreign key"]
GIS_DATA_TYPES = ["point", "line string", "polygon", "multi point", "multi line string", "multi polygon"]


DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS = {
    "auto key": [],
    "manual key": [],
    "integer": [],
    "float": [],
    "decimal": ["max_length", "precision"],
    "boolean": [],
    "text": ["max_length", "options"],
    "date": [],
    "time": [],
    "foreign key": ["target"],

    "point": [],  # TODO: COORDINATE TYPE
    "line string": [],  # TODO: COORDINATE TYPE
    "polygon": [],  # TODO: COORDINATE TYPE
    "multi point": [],  # TODO: COORDINATE TYPE
    "multi line string": [],  # TODO: COORDINATE TYPE
    "multi polygon": []  # TODO: COORDINATE TYPE
}


RE_INTEGER = re.compile(r"^([-+]?[1-9]\d*|0)$")
RE_INTEGER_HUMAN = re.compile(r"^([-+]?([1-9]\d{0,2})[\s,](\d{3}[\s,])*\d{3})$")  # TODO: THIS IS LOCALE-SPECIFIC
RE_DECIMAL = re.compile(r"^[-+]?\d*\.?\d+(e[-+]?\d+)?$")
# TODO: THIS IS LOCALE-SPECIFIC, AND CAN WE HAVE GROUPS AFTER?
RE_DECIMAL_HUMAN = re.compile(r"^[-+]?(\d{1,3}[\s,](\d{3}[\s,])*\d{3}(\.\d+)?|\d{1,3}(\.\d+)?|\.\d+)(e[-+]?\d+)?$")
# TODO: THIS IS LOCALE-SPECIFIC
RE_NUMBER_GROUP_SEPARATOR = re.compile(r"[,\s]")

RE_DATE_YMD_D = re.compile(r"^[1-2]\d{3}-\d{1,2}-\d{1,2}$")
RE_DATE_YMD_S = re.compile(r"^[1-2]\d{3}/\d{1,2}/\d{1,2}$")
RE_DATE_DMY_D = re.compile(r"^\d{1,2}-\d{1,2}-[1-2]\d{3}$")
RE_DATE_DMY_S = re.compile(r"^\d{1,2}/\d{1,2}/[1-2]\d{3}$")

RE_MULTIPLE_UNDERSCORES = re.compile(r"[_]{2,}")
RE_NON_IDENTIFIER_CHARACTERS = re.compile(r"[^\w]+")
RE_SEPARATOR_CHARACTERS = re.compile(r"[\s.\-]+")
RE_MULTIPLE_WHITESPACE_CHARACTERS = re.compile(r"\s{2,}")


# Order matters here - they line up and are zipped into matching pairs.
BOOLEAN_TRUE_VALUES = ("y", "yes", "t", "true", "1")
BOOLEAN_FALSE_VALUES = ("n", "no", "f", "false", "0")
BOOLEAN_TF_PAIRS = tuple(zip(BOOLEAN_TRUE_VALUES, BOOLEAN_FALSE_VALUES))


DATE_FORMATS = (
    (RE_DATE_YMD_D, "%Y-%m-%d"),
    (RE_DATE_YMD_S, "%Y/%m/%d"),
    (RE_DATE_DMY_D, "%d-%m-%Y"),
    (RE_DATE_DMY_S, "%d/%m/%Y")
)


PDT_RELATION_PREFIX = "PyTrackDat"


def valid_data_type(data_type: str, gis_mode: bool) -> bool:
    """
    Validates a data type. Assumes the data type has already been sanitized.
    """
    return (not gis_mode and data_type in DATA_TYPES) or (gis_mode and data_type in DATA_TYPES + GIS_DATA_TYPES)


def collapse_multiple_underscores(s: str):
    return re.sub(RE_MULTIPLE_UNDERSCORES, "_", s)


def sanitize_python_identifier(s: str) -> str:
    return re.sub(RE_NON_IDENTIFIER_CHARACTERS, "", re.sub(RE_SEPARATOR_CHARACTERS, "_", s.strip()))


def field_to_py_code(field: str) -> str:
    field = sanitize_python_identifier(field.lower())
    field = field + "_field" if field in PYTHON_KEYWORDS else field
    field = collapse_multiple_underscores(field)
    return field


def standardize_data_type(dt: str) -> str:
    return re.sub(RE_MULTIPLE_WHITESPACE_CHARACTERS, " ", dt.lower().replace("_", " "))


def to_relation_name(name: str) -> str:
    name_sanitized = collapse_multiple_underscores(sanitize_python_identifier(name))
    python_relation_name = PDT_RELATION_PREFIX + "".join([n.capitalize() for n in name_sanitized.split("_")])

    # Take care of plurals so they do not look dumb.

    if python_relation_name[-3:] == "ies":
        old_name = python_relation_name
        python_relation_name = python_relation_name[:-3] + "y"
        print("Warning: Auto-detected incorrect plural relation name.\n"
              "         Changing {} to {}.\n"
              "         To avoid this, specify singular names.".format(old_name, python_relation_name))
    elif python_relation_name[-1] == "s":
        old_name = python_relation_name
        python_relation_name = python_relation_name[:-1]
        print("Warning: Auto-detected incorrect plural relation name.\n         Altering from "
              "{} to {}.\n         To avoid this, specify singular names.".format(old_name, python_relation_name))

    return python_relation_name


def print_license() -> None:
    print("""PyTrackDat v{}  Copyright (C) {} the PyTrackDat authors.
This program comes with ABSOLUTELY NO WARRANTY; see LICENSE for details.
""".format(VERSION, COPYRIGHT_DATES))


def exit_with_error(message: str):
    print()
    print(message)
    print()
    # TODO: HANDLE CLEANUP
    exit(1)
