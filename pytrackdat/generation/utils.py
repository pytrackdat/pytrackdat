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

from typing import Optional, Tuple
from ..common import DESIGN_SEPARATOR, RelationField


__all__ = [
    "get_choices_from_text_field",
]


def get_choices_from_text_field(f: RelationField) -> Optional[Tuple[str, ...]]:
    if len(f.additional_fields) == 2:
        # TODO: Choice human names
        choice_names = tuple(str(c).strip() for c in f.additional_fields[1].split(DESIGN_SEPARATOR)
                             if str(c).strip() != "")
        return choice_names if len(choice_names) > 0 else None
    return None
