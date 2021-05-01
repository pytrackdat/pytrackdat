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

import os
import subprocess
from argparse import Namespace


def test_site(args: Namespace):
    manage_path = os.path.join(os.path.dirname(__file__), "ptd_site", "django_manage.py")

    current_env = os.environ.copy()
    current_env["PTD_DESIGN_FILE"] = args.design_file

    subprocess.run((manage_path, "makemigrations"), env=current_env)
    subprocess.run((manage_path, "migrate"), env=current_env)
    subprocess.run((manage_path, "runserver"), env=current_env)
