import re

from decimal import Decimal
from datetime import datetime
from typing import Optional

from pytrackdat import common as c


__all__ = ["DATA_TYPE_STRING_PARSERS"]


def parse_dt_integer(dv: str):
    return int(re.sub(c.RE_NUMBER_GROUP_SEPARATOR, "", dv.strip()))


def parse_dt_float(dv: str):
    return float(re.sub(c.RE_NUMBER_GROUP_SEPARATOR, "", dv.lower().strip()))


def parse_dt_decimal(dv: str):
    return Decimal(re.sub(c.RE_NUMBER_GROUP_SEPARATOR, "", dv.lower().strip()))


def parse_dt_date(dv: str, field_name: str):
    # TODO: adjust format based on heuristics
    # TODO: Allow extra column setting with date format from python docs?

    dt_interpretations = tuple(datetime.strptime(dv.strip(), df) for dr, df in c.DATE_FORMATS)
    if len(dt_interpretations) == 0:
        # TODO: Warning
        print("Warning: Value '{}' the date-typed field '{}' does not match any PyTrackDat-compatible "
              "formats.".format(dv.strip(), field_name))
        return None

    if re.match(c.RE_DATE_DMY_D, dv.strip()) or re.match(c.RE_DATE_DMY_S, dv.strip()):
        print("Warning: Assuming d{sep}m{sep}Y date format for ambiguously-formatted date field '{field}'.".format(
            sep="-" if "-" in dv.strip() else "/", field=field_name))

    return dt_interpretations[0]


def parse_dt_time(dv: str):
    # TODO: adjust format based on MORE heuristics
    # TODO: Allow extra column setting with time format from python docs?
    return datetime.strptime(dv.strip(), "%H:%M" if len(dv.strip().split(":")) == 2 else "%H:%M:%S")


def parse_dt_boolean(dv: str, _field_name: str, nullable: bool, null_values: tuple) -> Optional[bool]:
    if nullable and ((len(null_values) != 0 and dv.strip() in null_values) or (dv.strip() == "")):
        return None

    return dv.strip().lower() in c.BOOLEAN_TRUE_VALUES


# TODO: GIS default parsers
DATA_TYPE_STRING_PARSERS = {
    c.DT_INTEGER: parse_dt_integer,
    c.DT_FLOAT: parse_dt_float,
    c.DT_DECIMAL: parse_dt_decimal,
    c.DT_DATE: parse_dt_date,
    c.DT_TIME: parse_dt_time,
    c.DT_BOOLEAN: parse_dt_boolean,
}
