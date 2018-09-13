#!/usr/bin/env bash

set -eu

cd $2
rm -rf ./tmp_env 2> /dev/null
rm -rf ./$1 2> /dev/null
virtualenv -p python3 ./tmp_env
PS1="" source tmp_env/bin/activate
pip install -r ../util_files/requirements_setup.txt
django-admin startproject $1
cp ../util_files/requirements.txt $1/
cd $1
chmod +x ./manage.py
./manage.py startapp core
cp -r ../../app_includes/* ./core/
deactivate
