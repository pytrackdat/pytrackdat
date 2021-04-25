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

__all__ = [
    "is_common_password",
]


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
