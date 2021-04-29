#!/usr/bin/env python3

import argparse

from pytrackdat.analysis import main as analyze
from pytrackdat.ptd_site.manage import main as django_manage
from pytrackdat.test_site import test_site
from pytrackdat.common import print_license


ACTIONS = {
    "analyze": {
        "fn": analyze,
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
                "required": True,
            })
        ),
    },
    "test": {
        "fn": test_site,
        "help": "Starts a site (using the specified design file) in test mode.",
        "args": ("design_file", {
            "type": str,
            "help": "Path to the design file to test.",
            "required": True,
        }),
    },
    "django-manage": {
        "fn": lambda args: django_manage(args.args),
        "help": "Runs site commands using the Django application's management script.",
        "args": ("args", {
            "nargs": "*",
            "help": "Arguments to pass to the Django manage.py script.",  # TODO
        }),  # TODO: Arbitrary?
    },

    # TODO: User creation wizard
}


def main():
    print_license()

    parser = argparse.ArgumentParser(description="A tool for generating online databases and data portals.")
    subparsers = parser.add_subparsers(
        title="action",
        dest="action",
        help="PyTrackDat action to perform (analyzing a CSV, testing a site, or sending commands to the internal "
             "Django project)",
        required=True)  # TODO

    for action, action_data in ACTIONS.items():
        action_parser = subparsers.add_parser(action, help=action_data["help"])
        for arg, opts_dict in action_data["args"]:
            action_parser.add_argument(arg, **opts_dict)

    args = parser.parse_args()
    ACTIONS[args.action]["fn"](args)


if __name__ == "__main__":
    main()
