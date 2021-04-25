import os
import subprocess
from argparse import Namespace


def test_site(args: Namespace):
    print("test site")

    manage_path = os.path.join(os.path.dirname(__file__), "ptd_site", "django_manage.py")

    current_env = os.environ.copy()
    current_env["PTD_DESIGN_FILE"] = args.design_file

    subprocess.run((manage_path, "makemigrations"), env=current_env)
    subprocess.run((manage_path, "migrate"), env=current_env)
    subprocess.run((manage_path, "runserver"), env=current_env)
