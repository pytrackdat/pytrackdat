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
from argparse import Namespace

from pytrackdat.ptd_site.manage import main as django_manage


def test_site(args: Namespace):
    old_df_val = os.environ.get("PTD_DESIGN_FILE")

    try:
        # Apparently the underlying syscall is a memory leak here on macOS/FreeBSD... TODO
        os.environ["PTD_DESIGN_FILE"] = args.design_file

        print("[PyTrackDat] Making any required migrations...")
        django_manage(["django-manage", "makemigrations"])

        print("\n[PyTrackDat] Running any migrations not yet applied...")
        django_manage(["django-manage", "migrate"])

        print("[PyTrackDat] Collecting static files...")
        django_manage(["django-manage", "collectstatic", "--noinput"])

        print("\n[PyTrackDat] Running development server...")
        # Reloader will raise a ModuleNotFound error on pytrackdat
        django_manage(["django-manage", "runserver", "--noreload"])

    finally:
        if old_df_val is not None:
            os.environ["PTD_DESIGN_FILE"] = old_df_val
