#!/usr/bin/env bash

set -eu

cd $2/$1
rm -rf ./site_env 2> /dev/null
virtualenv -p python3 ./site_env
PS1="" source site_env/bin/activate
pip install -r ./requirements.txt
python ./manage.py makemigrations
python ./manage.py migrate
deactivate
