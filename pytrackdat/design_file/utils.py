from datetime import datetime
from decimal import Decimal
from typing import Optional, Tuple, Union

from pytrackdat import common as pc

from .parsers import DATA_TYPE_STRING_PARSERS


def get_default_from_csv_with_type(field_name: str, dv: str, dt: str, nullable: bool = False, null_values: tuple = ()) \
        -> Union[None, int, float, Decimal, datetime, str, bool]:
    if dv.strip() == "" and dt != pc.DT_BOOLEAN:
        return None

    if dt in DATA_TYPE_STRING_PARSERS:
        return DATA_TYPE_STRING_PARSERS[dt](dv, field_name, nullable, null_values)

    # Otherwise, keep string version
    return dv


def get_choices_from_text_field(f: pc.RelationField) -> Optional[Tuple[str, ...]]:
    if len(f.additional_fields) == 2:
        # TODO: Choice human names
        choice_names = tuple(str(c).strip() for c in f.additional_fields[1].split(pc.DESIGN_SEPARATOR)
                             if str(c).strip() != "")
        return choice_names if len(choice_names) > 0 else None
    return None
