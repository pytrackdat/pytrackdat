from datetime import datetime
from decimal import Decimal
from typing import Union
from pytrackdat import common as c

from .parsers import DATA_TYPE_STRING_PARSERS


def get_default_from_csv_with_type(field_name: str, dv: str, dt: str, nullable: bool = False, null_values: tuple = ()) \
        -> Union[None, int, float, Decimal, datetime, str, bool]:
    if dv.strip() == "" and dt != c.DT_BOOLEAN:
        return None

    if dt in DATA_TYPE_STRING_PARSERS:
        return DATA_TYPE_STRING_PARSERS[dt](dv, field_name, nullable, null_values)

    # Otherwise, keep string version
    return dv
