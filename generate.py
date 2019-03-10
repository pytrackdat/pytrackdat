#!/usr/bin/env python3

# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2019 the PyTrackDat authors.
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

import getpass
import gzip
import os
import shutil
import subprocess
import sys

from pytrackdat.common import *
from pytrackdat.generation import *

# TODO: TIMEZONES
# TODO: Multiple date formats
# TODO: More ways for custom validation
# TODO: More customization options

TEMP_DIRECTORY = "tmp"


def print_usage():
    print("Usage: ./generate.py design.csv output_site_name")


def main(args):
    design_file = args[0]  # File name for design file input
    django_site_name = args[1]

    if not os.path.exists(TEMP_DIRECTORY):
        os.makedirs(TEMP_DIRECTORY)

    if os.name not in ("nt", "posix"):
        print("Unsupported platform.")
        exit(1)

    site_url = "localhost"

    a_buf = None
    m_buf = None

    # Process and validate design file, get contents of admin and models files
    try:
        print("Validating design file '{}'...".format(design_file))
        with open(design_file, "r") as df:
            try:
                a_buf, m_buf = create_admin_and_models(df, django_site_name)
            except GenerationError as e:
                exit_with_error(str(e))
        print("done.\n")

        prod_build = input("Is this a production build? (y/n): ")
        if prod_build.lower() in ("y", "yes"):
            site_url = input("Please enter the production site URL, without 'www.' or 'http://': ")
            while "http:" in site_url or "https:" in site_url or "/www." in site_url:
                site_url = input("Please enter the production site URL, without 'www.' or 'http://': ")
        elif prod_build.lower() not in ("n", "no"):
            print("Invalid answer '{}', assuming 'n'...".format(prod_build))

        print()

        with a_buf, m_buf:
            # Run site creation script
            # TODO: Make path more robust
            create_site_script = "os_scripts\\create_django_site.bat" if os.name == "nt" \
                else "./os_scripts/create_django_site.bash"
            create_site_options = [create_site_script, django_site_name, TEMP_DIRECTORY]
            subprocess.run(create_site_options, check=True)

            # Write admin and models file contents to disk
            with open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "models.py"), "w") as mf, \
                    open(os.path.join(TEMP_DIRECTORY, django_site_name, "core", "admin.py"), "w") as af:
                shutil.copyfileobj(a_buf, af)
                shutil.copyfileobj(m_buf, mf)

        with open(os.path.join(TEMP_DIRECTORY, django_site_name, "snapshot_manager", "models.py"), "w") as smf, \
                open(os.path.join(TEMP_DIRECTORY, django_site_name, "snapshot_manager", "admin.py"), "w") as saf:
            smf.write(MODELS_FILE_HEADER)
            smf.write("\n")
            smf.write(SNAPSHOT_MODEL.format(django_site_name))
            saf.write(SNAPSHOT_ADMIN_FILE_HEADER)
            saf.write("\n@admin.register(Snapshot)\n\n")
            saf.write("class SnapshotAdmin(admin.ModelAdmin):\n")
            saf.write("    exclude = ('snapshot_type', 'size', 'name')\n")

    except FileNotFoundError:
        exit_with_error("Design file not found.")

    with open(os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name, "settings.py"), "r+") as sf:
        old_contents = sf.read()
        sf.seek(0)
        sf.write(old_contents.replace(INSTALLED_APPS_OLD, INSTALLED_APPS_NEW)
                 .replace(DEBUG_OLD, DEBUG_NEW)
                 .replace(ALLOWED_HOSTS_OLD, ALLOWED_HOSTS_NEW.format(site_url))
                 .replace(STATIC_OLD, STATIC_NEW) + DISABLE_MAX_FIELDS)
        sf.truncate()

    with open(os.path.join(TEMP_DIRECTORY, django_site_name, django_site_name, "urls.py"), "r+") as uf:
        old_contents = uf.read()
        uf.seek(0)
        uf.write(old_contents.replace(URL_OLD, URL_NEW))
        uf.truncate()

    # Try to use password list created by Royce Williams and adapted for the Django project:
    # https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7
    common_passwords = ["password", "123456", "12345678"]  # Fallbacks if file not present
    try:
        with gzip.open(os.path.join(os.path.dirname(__file__), "common-passwords.txt.gz")) as f:
            common_passwords = {p.strip() for p in f.read().decode().splitlines()
                                if len(p.strip()) >= 8}  # Don't bother including too-short passwords
    except OSError:
        pass

    print("\n================ ADMINISTRATIVE SETUP ================")
    admin_username = input("Admin Account Username: ")
    while admin_username.strip() == "":
        print("Please enter a username.")
        admin_username = input("Admin Account Username: ")
    admin_email = input("Admin Account Email (Optional): ")
    admin_password = "1"
    admin_password_2 = "2"
    while admin_password != admin_password_2:
        admin_password = getpass.getpass("Admin Account Password: ")

        # TODO: Properly check password validity
        if len(admin_password.strip()) < 8:
            print("Please enter a secure password (8 or more characters).")
            admin_password = "1"
            admin_password_2 = "2"
            continue

        if admin_password.lower().strip() in common_passwords:
            print("Please enter in a less commonly-used password (8 or more characters).")
            admin_password = "1"
            admin_password_2 = "2"
            continue

        admin_password_2 = getpass.getpass("Admin Account Password Again: ")

        if admin_password != admin_password_2:
            print("Passwords do not match. Please try again.")
    print("======================================================\n")

    try:
        # TODO: Make path more robust
        site_setup_script = "os_scripts\\run_site_setup.bat" if os.name == "nt" \
            else "./os_scripts/run_site_setup.bash"
        site_setup_options = [site_setup_script, django_site_name, TEMP_DIRECTORY, admin_username, admin_email,
                              admin_password, site_url]
        subprocess.run(site_setup_options, check=True)

    except subprocess.CalledProcessError:
        # Need to catch subprocess errors to prevent password from being shown onscreen.
        exit_with_error("An error occurred while running the site setup script.\nTerminating...")

    shutil.make_archive(django_site_name, "zip", root_dir="tmp", base_dir=django_site_name)


if __name__ == "__main__":
    print_license()

    if len(sys.argv) != 3:
        print_usage()
        exit(1)

    main(sys.argv[1:])
