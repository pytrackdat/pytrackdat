#!/usr/bin/env python3

import os
import subprocess

from sys import argv

from .common import *


TEMP_DIRECTORY = os.path.join(os.getcwd(), "tmp")


def main():
    print_license()

    if len(argv) != 2:
        print("Usage: ptd-test site_name")
        exit(1)

    site_path = os.path.join(TEMP_DIRECTORY, argv[1])

    if not os.path.isdir(site_path) or not os.path.isfile(os.path.join(site_path, "manage.py")):
        print("Error: {} is not a valid site.".format(argv[1]))
        exit(1)

    try:
        subprocess.run(
            ('cmd /c "cd {} && site_env\\Scripts\\activate.bat && python manage.py runserver"' if os.name == "nt"
             else "/bin/bash -c 'cd {} && source site_env/bin/activate && ./manage.py runserver'").format(site_path),
            shell=True
        )
    except (subprocess.CalledProcessError, KeyboardInterrupt):
        print("\nExiting...")


if __name__ == "__main__":
    main()
