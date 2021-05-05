#!/usr/bin/env python3

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

import argparse

from pytrackdat.analysis import analyze_entry
from pytrackdat.ptd_site.manage import main as django_manage
from pytrackdat.test_site import test_site
from pytrackdat.common import print_license


ACTIONS = {
    "analyze": {
        "fn": analyze_entry,
        "help": "Analyzes a series of CSVs and outputs a best-attempt generated design file.",
        "args": (
            ("--design-out", {
                "type": str,
                "help": "The filename for the design file which will be generated.",
                "default": "design_out.csv",
            }),
            ("name-file-pairs", {
                "nargs": "+",
                "help": "Alternating pairs of file name and relation (table) name for the CSVs to analyze.",
            }),
        ),
    },
    "test": {
        "fn": test_site,
        "help": "Runs a server for a site (using the specified design file) in test mode.",
        "args": (
            ("design_file", {
                "type": str,
                "help": "Path to the design file to test.",
            }),
        ),
    },
    "django-manage": {
        "fn": lambda args: django_manage(args.args),
        "help": "Runs site commands using the Django application's management script.",
        "args": (
            ("args", {
                "nargs": "*",
                "help": "Arguments to pass to the Django manage.py script.",  # TODO
            }),
        ),  # TODO: Arbitrary?
    },

    # TODO: User creation wizard
}


def main():
    parser = argparse.ArgumentParser(description="A tool for generating online databases and data portals.")
    parser.add_argument("--no-license", help="Suppress license printing.", action="store_true")

    subparsers = parser.add_subparsers(
        title="action",
        dest="action",
        help="PyTrackDat action to perform (analyzing a CSV, testing a site, or sending commands to the internal "
             "Django project)",
        required=True)

    for action, action_data in ACTIONS.items():
        action_parser = subparsers.add_parser(action, help=action_data["help"])
        for arg, opts_dict in action_data["args"]:
            action_parser.add_argument(arg, **opts_dict)

    args = parser.parse_args()

    if not args.no_license:
        print_license()

    ACTIONS[args.action]["fn"](args)


if __name__ == "__main__":
    main()
