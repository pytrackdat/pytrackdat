# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2020 the PyTrackDat authors.
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

from typing import Dict

from ..common import *
from .constants import BASIC_NUMBER_TYPES
from .utils import get_choices_from_text_field


__all__ = [
   "clean_field_help_text",
   "auto_key_formatter",
   "manual_key_formatter",
   "foreign_key_formatter",
   "basic_number_formatter",
   "decimal_formatter",
   "boolean_formatter",
]


def clean_field_help_text(d: str) -> str:
    return d.replace("\\", "\\\\").replace("'", "\\'")


def auto_key_formatter(f: Dict) -> str:
    return "models.AutoField(primary_key=True, help_text='{}')".format(clean_field_help_text(f["description"]))


def manual_key_formatter(f: Dict) -> str:
    # TODO: Shouldn't be always text?
    return "models.CharField(primary_key=True, max_length=127, " \
           "help_text='{}')".format(clean_field_help_text(f["description"]))


def foreign_key_formatter(f: Dict) -> str:
    return (
        "models.ForeignKey('{relation}', help_text='{help_text}', blank={nullable}, null={nullable}, "
        "on_delete=models.{on_delete})".format(
            relation=to_relation_name(f["additional_fields"][0]),
            help_text=f["description"].replace("'", "\\'"),
            nullable=str(f["nullable"]),
            on_delete="SET_NULL" if f["nullable"] else "CASCADE"
        ))


def basic_number_formatter(f: Dict) -> str:
    t = BASIC_NUMBER_TYPES[f["data_type"]]
    return "models.{type}(help_text='{help_text}', blank={nullable}, null={nullable}{default})".format(
        type=t,
        help_text=clean_field_help_text(f["description"]),
        nullable=str(f["nullable"]),
        default="" if f["default"] is None else ", default={}".format(f["default"])
    )


def decimal_formatter(f: Dict) -> str:
    return (
        "models.DecimalField(help_text='{help_text}', max_digits={max_digits}, decimal_places={decimals}, "
        "blank={nullable}, null={nullable}{default})".format(
            help_text=clean_field_help_text(f["description"]),
            max_digits=f["additional_fields"][0],
            decimals=f["additional_fields"][1],
            nullable=str(f["nullable"]),
            default="" if f["default"] is None else ", default=Decimal({})".format(f["default"])
        ))


def boolean_formatter(f: Dict) -> str:
    return "models.BooleanField(help_text='{help_text}', blank={nullable}, null={nullable}{default})".format(
        help_text=clean_field_help_text(f["description"]),
        nullable=str(f["nullable"]),
        default="" if f["default"] is None else ", default={}".format(f["default"])
    )


def text_formatter(f: Dict) -> str:
    choices = ()
    max_length = None

    if len(f["additional_fields"]) >= 1:
        try:
            max_length = int(f["additional_fields"][0])
        except ValueError:
            pass

    if len(f["additional_fields"]) == 2:
        # TODO: Choice human names
        choice_names = get_choices_from_text_field(f)
        if choice_names is not None:
            choices = tuple(zip(choice_names, choice_names))

    return "models.{field_type}(help_text='{help_text}', blank={blank_value}{default}{choices}{length})".format(
        field_type="TextField" if max_length is None else "CharField",
        help_text=clean_field_help_text(f["description"]),
        blank_value=str(len(choices) == 0 or f["nullable"]),

        # TODO: Make sure default is cleaned
        default="" if f["default"] is None else ", default='{}'".format(f["default"]),
        choices="" if len(choices) == 0 else ", choices={}".format(str(choices)),
        length="" if max_length is None else ", max_length={}".format(max_length)
    )


def date_formatter(f: Dict) -> str:
    # TODO: standardize date formatting... I think this might already be standardized?
    return "models.DateField(help_text='{help_text}', blank={nullable}, null={nullable}{default})".format(
        help_text=clean_field_help_text(f["description"]),
        nullable=str(f["nullable"]),
        default="" if f["default"] is None else ", default=datetime.strptime('{}', '%Y-%m-%d')".format(
            f["default"].strftime("%Y-%m-%d")
        )
    )


# All spatial fields cannot be null.


def point_formatter(f: Dict) -> str:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POINT FORMAT FOR DEFAULTS / IN GENERAL
    return "models.PointField(help_text='{}')".format(f["description"].replace("'", "\\'"))


def line_string_formatter(f: Dict) -> str:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT LINE STRING FORMAT FOR DEFAULTS / IN GENERAL
    return "models.LineStringField(help_text='{}')".format(f["description"].replace("'", "\\'"))


def polygon_formatter(f: Dict) -> str:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POLYGON FORMAT FOR DEFAULTS / IN GENERAL
    return "models.PolygonField(help_text='{}')".format(f["description"].replace("'", "\\'"))


def multi_point_formatter(f: Dict) -> str:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POINT FORMAT FOR DEFAULTS / IN GENERAL
    return "models.MultiPointField(help_text='{}')".format(f["description"].replace("'", "\\'"))


def multi_line_string_formatter(f: Dict) -> str:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT LINE STRING FORMAT FOR DEFAULTS / IN GENERAL
    return "models.MultiLineStringField(help_text='{}')".format(f["description"].replace("'", "\\'"))


def multi_polygon_formatter(f: Dict) -> str:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POLYGON FORMAT FOR DEFAULTS / IN GENERAL
    return "models.MultiPolygonField(help_text='{}')".format(f["description"].replace("'", "\\'"))


DJANGO_TYPE_FORMATTERS = {
    # Standard PyTrackDat Fields
    DT_AUTO_KEY: auto_key_formatter,
    DT_MANUAL_KEY: manual_key_formatter,
    DT_FOREIGN_KEY: foreign_key_formatter,
    DT_INTEGER: basic_number_formatter,
    DT_DECIMAL: decimal_formatter,
    DT_FLOAT: basic_number_formatter,
    DT_BOOLEAN: boolean_formatter,
    DT_TEXT: text_formatter,
    DT_DATE: date_formatter,
    # TODO: Missing: time_formatter

    # PyTrackDat GeoDjango Fields
    DT_GIS_POINT: point_formatter,
    DT_GIS_LINE_STRING: line_string_formatter,
    DT_GIS_POLYGON: polygon_formatter,
    DT_GIS_MULTI_POINT: multi_point_formatter,
    DT_GIS_MULTI_LINE_STRING: multi_line_string_formatter,
    DT_GIS_MULTI_POLYGON: multi_polygon_formatter,

    "unknown": text_formatter  # Default to text fields... TODO: Should give a warning
}
