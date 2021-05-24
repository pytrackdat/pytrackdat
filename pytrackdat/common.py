# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2021 the PyTrackDat authors.
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

# TODO: py3.9: Use other Tuple typing
from typing import Dict, Optional, Sequence, Tuple


__all__ = [
    "VERSION",
    "COPYRIGHT_DATES",
    "PYTHON_KEYWORDS",

    "DT_AUTO_KEY",
    "DT_MANUAL_KEY",
    "DT_INTEGER",
    "DT_FLOAT",
    "DT_DECIMAL",
    "DT_BOOLEAN",
    "DT_TEXT",
    "DT_DATE",
    "DT_TIME",
    "DT_FOREIGN_KEY",

    "DT_GIS_POINT",
    "DT_GIS_LINE_STRING",
    "DT_GIS_POLYGON",
    "DT_GIS_MULTI_POINT",
    "DT_GIS_MULTI_LINE_STRING",
    "DT_GIS_MULTI_POLYGON",

    "KEY_TYPES",
    "DATA_TYPES",
    "GIS_DATA_TYPES",
    "DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS",
    "SEARCHABLE_FIELD_TYPES",
    "DESIGN_SEPARATOR",

    "RE_INTEGER",
    "RE_INTEGER_HUMAN",
    "RE_DECIMAL",
    "RE_DECIMAL_HUMAN",
    "RE_NUMBER_GROUP_SEPARATOR",
    "RE_DATE_YMD_D",
    "RE_DATE_YMD_S",
    "RE_DATE_DMY_D",
    "RE_DATE_DMY_S",
    "RE_TIME_HH_MM_24",
    "RE_TIME_HH_MM_SS_24",
    "RE_MULTIPLE_UNDERSCORES",
    "RE_NON_IDENTIFIER_CHARACTERS",
    "RE_SEPARATOR_CHARACTERS",
    "RE_MULTIPLE_WHITESPACE_CHARACTERS",

    "BOOLEAN_TRUE_VALUES",
    "BOOLEAN_FALSE_VALUES",
    "BOOLEAN_TF_PAIRS",

    "TIME_FORMATS",
    "DATE_FORMATS",

    "PDT_RELATION_PREFIX",

    "API_FILTERABLE_FIELD_TYPES",

    "valid_data_type",
    "collapse_multiple_underscores",
    "sanitize_python_identifier",
    "field_to_py_code",
    "standardize_data_type",
    "to_relation_name",
    "print_license",
    "exit_with_error",

    "RelationField",
    "Relation",
]


VERSION = "0.3.0"
COPYRIGHT_DATES = "2018-2021"

PYTHON_KEYWORDS = ("False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
                   "def", "del", "else", "elif", "except", "finally", "for", "from", "global", "if", "import", "in",
                   "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield")

DT_AUTO_KEY = "auto key"
DT_MANUAL_KEY = "manual key"
DT_INTEGER = "integer"
DT_FLOAT = "float"
DT_DECIMAL = "decimal"
DT_BOOLEAN = "boolean"
DT_TEXT = "text"
DT_DATE = "date"
DT_TIME = "time"
DT_FOREIGN_KEY = "foreign key"

DT_GIS_POINT = "point"
DT_GIS_LINE_STRING = "line string"
DT_GIS_POLYGON = "polygon"
DT_GIS_MULTI_POINT = "multi point"
DT_GIS_MULTI_LINE_STRING = "multi line string"
DT_GIS_MULTI_POLYGON = "multi polygon"

KEY_TYPES: Tuple[str, ...] = (DT_AUTO_KEY, DT_MANUAL_KEY)

DATA_TYPES: Tuple[str, ...] = (
    DT_AUTO_KEY,
    DT_MANUAL_KEY,
    DT_INTEGER,
    DT_FLOAT,
    DT_DECIMAL,
    DT_BOOLEAN,
    DT_TEXT,
    DT_DATE,
    DT_TIME,
    DT_FOREIGN_KEY,
)

GIS_DATA_TYPES: Tuple[str, ...] = (
    DT_GIS_POINT,
    DT_GIS_LINE_STRING,
    DT_GIS_POLYGON,
    DT_GIS_MULTI_POINT,
    DT_GIS_MULTI_LINE_STRING,
    DT_GIS_MULTI_POLYGON,
)


DATA_TYPE_ADDITIONAL_DESIGN_SETTINGS: Dict[str, Tuple[str, ...]] = {
    DT_AUTO_KEY: (),
    DT_MANUAL_KEY: (),
    DT_INTEGER: (),
    DT_FLOAT: (),
    DT_DECIMAL: ("max_length", "precision"),
    DT_BOOLEAN: (),
    DT_TEXT: ("max_length", "options"),
    DT_DATE: (),
    DT_TIME: (),
    DT_FOREIGN_KEY: ("target",),

    DT_GIS_POINT: (),  # TODO: COORDINATE TYPE
    DT_GIS_LINE_STRING: (),  # TODO: COORDINATE TYPE
    DT_GIS_POLYGON: (),  # TODO: COORDINATE TYPE
    DT_GIS_MULTI_POINT: (),  # TODO: COORDINATE TYPE
    DT_GIS_MULTI_LINE_STRING: (),  # TODO: COORDINATE TYPE
    DT_GIS_MULTI_POLYGON: (),  # TODO: COORDINATE TYPE
}

DESIGN_SEPARATOR = ";"


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

RE_TIME_HH_MM_24 = re.compile(r"^\d{2}:\d{2}$")
RE_TIME_HH_MM_SS_24 = re.compile(r"^\d{2}:\d{2}:\d{2}$")

RE_MULTIPLE_UNDERSCORES = re.compile(r"[_]{2,}")
RE_NON_IDENTIFIER_CHARACTERS = re.compile(r"[^\w]+")
RE_SEPARATOR_CHARACTERS = re.compile(r"[\s.\-]+")
RE_MULTIPLE_WHITESPACE_CHARACTERS = re.compile(r"\s{2,}")


# Order matters here - they line up and are zipped into matching pairs.
BOOLEAN_TRUE_VALUES = ("y", "yes", "t", "true", "1")
BOOLEAN_FALSE_VALUES = ("n", "no", "f", "false", "0")
BOOLEAN_TF_PAIRS = tuple(zip(BOOLEAN_TRUE_VALUES, BOOLEAN_FALSE_VALUES))


TIME_FORMATS = (
    (RE_TIME_HH_MM_24, "%H:%M"),
    (RE_TIME_HH_MM_SS_24, "%H:%M:%S")
)


DATE_FORMATS = (
    (RE_DATE_YMD_D, "%Y-%m-%d"),
    (RE_DATE_YMD_S, "%Y/%m/%d"),
    (RE_DATE_DMY_D, "%d-%m-%Y"),
    (RE_DATE_DMY_S, "%d/%m/%Y")
)


# Prefix applied to all relation class names to guarantee no clashes in the models file namespace
PDT_RELATION_PREFIX = "PyTrackDat"


# What django-filter operations can be applied to which field data types
API_FILTERABLE_FIELD_TYPES = {
    DT_AUTO_KEY: ["exact", "in"],
    DT_MANUAL_KEY: ["exact", "in"],

    DT_INTEGER: ["exact", "lt", "lte", "gt", "gte", "in"],
    DT_FLOAT: ["exact", "lt", "lte", "gt", "gte"],
    DT_DECIMAL: ["exact", "lt", "lte", "gt", "gte", "in"],

    DT_BOOLEAN: ["exact"],

    DT_TEXT: ["exact", "iexact", "contains", "icontains", "in"],

    DT_DATE: ["exact", "lt", "lte", "gt", "gte", "in"],
    DT_TIME: ["exact", "lt", "lte", "gt", "gte", "in"],

    DT_FOREIGN_KEY: ["exact", "in"],
}

SEARCHABLE_FIELD_TYPES = frozenset({
    DT_AUTO_KEY,
    DT_MANUAL_KEY,
    DT_TEXT,
})


def valid_data_type(data_type: str, gis_mode: bool) -> bool:
    """
    Validates a data type. Assumes the data type has already been sanitized.
    """
    return (not gis_mode and data_type in DATA_TYPES) or (gis_mode and data_type in DATA_TYPES + GIS_DATA_TYPES)


def collapse_multiple_underscores(s: str) -> str:
    return RE_MULTIPLE_UNDERSCORES.sub("_", s)


def sanitize_python_identifier(s: str) -> str:
    return RE_NON_IDENTIFIER_CHARACTERS.sub("", RE_SEPARATOR_CHARACTERS.sub("_", s.strip()))


def field_to_py_code(field: str) -> str:
    field = sanitize_python_identifier(field.lower())
    return collapse_multiple_underscores(field + "_field" if field in PYTHON_KEYWORDS else field)


def standardize_data_type(dt: str) -> str:
    return re.sub(RE_MULTIPLE_WHITESPACE_CHARACTERS, " ", dt.lower().replace("_", " "))


def to_relation_name(name: str) -> str:
    name_sanitized = collapse_multiple_underscores(sanitize_python_identifier(name))
    python_relation_name = PDT_RELATION_PREFIX + "".join(n.capitalize() for n in name_sanitized.split("_"))

    # Take care of plurals so they do not look dumb.
    # This is actually a much harder problem than what is done here
    #  - more of a hack to make things look nicer on average.
    # TODO: Internationalization

    if python_relation_name[-3:] == "ies":
        old_name = python_relation_name
        python_relation_name = python_relation_name[:-3] + "y"
        print(f"Warning: Auto-detected incorrect plural relation name.\n"
              f"         Changing {old_name} to {python_relation_name}.\n"
              f"         To avoid this, specify singular names.")
    elif python_relation_name[-1] == "s":
        old_name = python_relation_name
        python_relation_name = python_relation_name[:-1]
        print(f"Warning: Auto-detected incorrect plural relation name.\n         Altering from "
              f"{old_name} to {python_relation_name}.\n         To avoid this, specify singular names.")

    return python_relation_name


def print_license():
    print(f"""PyTrackDat v{VERSION}  Copyright (C) {COPYRIGHT_DATES} the PyTrackDat authors.
This program comes with ABSOLUTELY NO WARRANTY; see LICENSE for details.
""")


def exit_with_error(message: str):
    print()
    print(message)
    print()
    exit(1)


class RelationField:
    def __init__(
        self,
        csv_names: Tuple[str, ...],
        name: str,
        data_type: str,
        nullable: bool,
        null_values: Tuple,
        default,
        description: str,
        show_in_table: bool,
        additional_fields: Tuple,
        choices: Optional[Tuple] = None,
    ):
        self.csv_names = csv_names
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.null_values = null_values
        self.default = default
        self.description = description
        self.show_in_table = show_in_table
        self.additional_fields = additional_fields
        self.choices = choices

    def as_design_file_row(self):
        return [
            ";;".join(self.csv_names),
            self.name,
            self.data_type,
            str(self.nullable).lower(),
            "; ".join(str(n) for n in self.null_values),
            str(self.default),  # TODO: format / serialize
            self.description,
            str(self.show_in_table).lower(),
            *self.additional_fields
        ]

    def make_alternate(self):
        return RelationField(
            self.csv_names,
            self.name + "_alt",  # New field name (in database; alternate)
            DT_TEXT,  # Alternate fields are always text, possibly with choices
            False,  # Alt. fields cannot be null
            (),  # No null values (since not nullable)
            "",  # No default value
            self.description,   # Description
            self.show_in_table,  # Whether to show in the table view
            (),  # No additional attributes
            self.choices,  # Inherit choices (shouldn't be any normally)
        )

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<RelationField name={self.name}>"

    def __iter__(self):
        yield "csv_names", self.csv_names
        yield "name", self.name
        yield "data_type", self.data_type
        yield "nullable", self.nullable
        yield "null_values", self.null_values
        yield "default", self.default
        yield "description", self.description
        yield "show_in_table", self.show_in_table
        yield "additional_fields", self.additional_fields
        yield "choices", self.choices


class Relation:
    def __init__(self, design_name: str, fields: Sequence[RelationField], id_type: str):
        self.design_name = design_name.strip()
        self.fields = fields
        self.id_type = id_type

    @property
    def name(self) -> str:
        # Python class-style name for the relation
        return to_relation_name(self.design_name)

    @property
    def short_name(self) -> str:
        # Python class-style name for the relation, sans prefix
        return self.name[len(PDT_RELATION_PREFIX):]

    @property
    def name_lower(self) -> str:
        # Python variable-style (snake case) name for the relation
        return field_to_py_code(self.design_name)

    def __str__(self):
        return self.design_name

    def __repr__(self):
        return f"<Relation design_name={self.design_name}>"

    def __iter__(self):
        yield "name", self.name
        yield "name_lower", self.name_lower
        yield "fields", tuple(dict(f) for f in self.fields)
        yield "id_type", self.id_type
