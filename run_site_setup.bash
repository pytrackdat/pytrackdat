#!/usr/bin/env bash

set -eu

cd $2/$1
rm -rf ./site_env 2> /dev/null
virtualenv -p python3 ./site_env
PS1="" source ./site_env/bin/activate
pip install -r ./requirements.txt
./manage.py makemigrations
./manage.py migrate
if [ ! -z "$3" ]; then
echo "from django.contrib.auth.models import User; User.objects.create_superuser('$3', '$4', '$5')" | ./manage.py shell > world
fi
deactivate
