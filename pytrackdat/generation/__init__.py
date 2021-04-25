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

import gzip
import os

from ..common import *
from .constants import *

from . import constants
from . import errors
from . import formatters
from . import utils


__all__ = [
    "constants",
    "errors",
    "formatters",
    "utils",
    "print_usage",
    "is_common_password",
    "API_FILTERABLE_FIELD_TYPES"
]


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


TEMP_DIRECTORY = os.path.join(os.getcwd(), "tmp")


def print_usage():
    print("Usage: ptd-generate design.csv output_site_name")


def is_common_password(password: str, package_dir: str) -> bool:
    # Try to use password list created by Royce Williams and adapted for the Django project:
    # https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7

    common_passwords = {"password", "123456", "12345678"}  # Fallbacks if file not present
    try:
        with gzip.open(os.path.join(package_dir, "common-passwords.txt.gz")) as f:
            common_passwords = {p.strip() for p in f.read().decode().splitlines()
                                if len(p.strip()) >= 8}  # Don't bother including too-short passwords
    except OSError:
        pass

    return password.lower().strip() in common_passwords


# TODO: TIMEZONES
# TODO: Multiple date formats
# TODO: More ways for custom validation
# TODO: More customization options
