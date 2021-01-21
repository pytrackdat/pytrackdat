#!/usr/bin/env python3

import os
from sys import argv

from pytrackdat.common import print_license
from pytrackdat.ptd_site.manage import main as manage_main


TEMP_DIRECTORY = os.path.join(os.getcwd(), "tmp")


def main():
    print_license()
    manage_main(argv)


if __name__ == "__main__":
    main()
