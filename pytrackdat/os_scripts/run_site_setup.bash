#!/usr/bin/env bash

set -eu

cd $3/$2
rm -rf ./site_env 2> /dev/null
virtualenv -p python3 ./site_env
PS1="" source ./site_env/bin/activate
pip install -r ./requirements.txt
./manage.py makemigrations
./manage.py migrate
if [[ ! -z "$4" ]]; then
echo "from django.contrib.auth.models import User; User.objects.create_superuser('$4', '$5', '$6')" \
  | ./manage.py shell > /dev/null
fi
deactivate
