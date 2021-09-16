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

from django.core.exceptions import ImproperlyConfigured
from django.db import models

try:
    from django.contrib.gis.db import models as gis_models
except ImproperlyConfigured:
    # No GDAL or something similar; GIS isn't configured / is misconfigured, so disable GIS support
    gis_models = None

from functools import wraps

import pytrackdat.common as c

from .errors import GISNotConfiguredError
from .utils import get_choices_from_text_field


__all__ = [
    "auto_key_formatter",
    "manual_key_formatter",
    "foreign_key_formatter",
    "basic_number_formatter",
    "decimal_formatter",
    "boolean_formatter",
    "DJANGO_TYPE_FORMATTERS",
]


BASIC_NUMBER_FIELD_CLASSES = {
    c.DT_INTEGER: models.IntegerField,
    c.DT_FLOAT: models.FloatField,
}


def auto_key_formatter(f: c.RelationField) -> models.Field:
    return models.AutoField(primary_key=True, help_text=f.description)


def manual_key_formatter(f: c.RelationField) -> models.Field:
    # TODO: Shouldn't be always text?
    return models.CharField(
        primary_key=True,
        max_length=127,
        help_text=f.description)


def foreign_key_formatter(f: c.RelationField) -> models.Field:
    return models.ForeignKey(
        c.to_relation_name(f.additional_fields[0]),
        help_text=f.description,
        blank=f.nullable,
        null=f.nullable,
        on_delete=models.SET_NULL if f.nullable else models.CASCADE)


def basic_number_formatter(f: c.RelationField) -> models.Field:
    return BASIC_NUMBER_FIELD_CLASSES[f.data_type](
        help_text=f.description,
        blank=f.nullable,
        null=f.nullable,
        **({} if f.default is None else {"default": f.default}))


def decimal_formatter(f: c.RelationField) -> models.Field:
    return models.DecimalField(
        help_text=f.description,
        max_digits=int(f.additional_fields[0]),
        decimal_places=int(f.additional_fields[1]),
        null=f.nullable,
        **({} if f.default is None else {"default": f.default}))


def boolean_formatter(f: c.RelationField) -> models.Field:
    return models.BooleanField(
        help_text=f.description,
        blank=f.nullable,
        null=f.nullable,
        **({} if f.default is None else {"default": f.default}))


def text_formatter(f: c.RelationField) -> models.Field:
    choices = ()
    max_length = None

    if len(f.additional_fields) >= 1:
        try:
            max_length = int(f.additional_fields[0])
        except ValueError:
            pass

    if len(f.additional_fields) == 2:
        # TODO: Choice human names
        # TODO: Use choices property?
        choice_names = get_choices_from_text_field(f)
        if choice_names is not None:
            choices = tuple(zip(choice_names, choice_names))

    return (models.TextField if max_length is None else models.CharField)(
        help_text=f.description,
        blank=len(choices) == 0 or f.nullable,
        **({} if f.default is None else {"default": f.default}),
        **({} if not choices else {"choices": choices}),
        **({} if max_length is None else {"max_length": max_length}))


def date_formatter(f: c.RelationField) -> models.Field:
    # TODO: standardize date formatting... I think this might already be standardized?
    return models.DateField(
        help_text=f.description,
        blank=f.nullable,
        null=f.nullable,
        **({} if f.default is None else {"default": f.default}))


def require_gis(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if gis_models is None:
            raise GISNotConfiguredError(
                "GIS was not configured correctly; check the GDAL_LIBRARY_PATH and SPATIALITE_LIBRARY_PATH environment "
                "variables")
        return func(*args, **kwargs)
    return wrapper


# All spatial fields cannot be null.


@require_gis
def point_formatter(f: c.RelationField) -> models.Field:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POINT FORMAT FOR DEFAULTS / IN GENERAL
    return gis_models.PointField(help_text=f.description)


@require_gis
def line_string_formatter(f: c.RelationField) -> models.Field:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT LINE STRING FORMAT FOR DEFAULTS / IN GENERAL
    return gis_models.LineStringField(help_text=f.description)


@require_gis
def polygon_formatter(f: c.RelationField) -> models.Field:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POLYGON FORMAT FOR DEFAULTS / IN GENERAL
    return gis_models.PolygonField(help_text=f.description)


@require_gis
def multi_point_formatter(f: c.RelationField) -> models.Field:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POINT FORMAT FOR DEFAULTS / IN GENERAL
    return gis_models.MultiPointField(help_text=f.description)


@require_gis
def multi_line_string_formatter(f: c.RelationField) -> models.Field:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT LINE STRING FORMAT FOR DEFAULTS / IN GENERAL
    return gis_models.MultiLineStringField(help_text=f.description)


@require_gis
def multi_polygon_formatter(f: c.RelationField) -> models.Field:
    # TODO: WARN IF NULLABLE
    # TODO: DO WE EVER MAKE THIS BLANK?
    # TODO: FIGURE OUT POLYGON FORMAT FOR DEFAULTS / IN GENERAL
    return gis_models.MultiPolygonField(help_text=f.description)


DJANGO_TYPE_FORMATTERS = {
    # Standard PyTrackDat Fields
    c.DT_AUTO_KEY: auto_key_formatter,
    c.DT_MANUAL_KEY: manual_key_formatter,
    c.DT_FOREIGN_KEY: foreign_key_formatter,
    c.DT_INTEGER: basic_number_formatter,
    c.DT_DECIMAL: decimal_formatter,
    c.DT_FLOAT: basic_number_formatter,
    c.DT_BOOLEAN: boolean_formatter,
    c.DT_TEXT: text_formatter,
    c.DT_DATE: date_formatter,
    # TODO: Missing: time_formatter

    # PyTrackDat GeoDjango Fields
    c.DT_GIS_POINT: point_formatter,
    c.DT_GIS_LINE_STRING: line_string_formatter,
    c.DT_GIS_POLYGON: polygon_formatter,
    c.DT_GIS_MULTI_POINT: multi_point_formatter,
    c.DT_GIS_MULTI_LINE_STRING: multi_line_string_formatter,
    c.DT_GIS_MULTI_POLYGON: multi_polygon_formatter,

    "unknown": text_formatter  # Default to text fields... TODO: Should give a warning
}
