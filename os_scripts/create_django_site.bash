#!/usr/bin/env bash

set -eu

# Enter the temporary site construction directory
cd $2

# Remove existing site data if it exists
rm -rf ./tmp_env 2> /dev/null
rm -rf ./$1 2> /dev/null

# Create and activate the virtual environment used for setup
virtualenv -p python3 ./tmp_env
PS1="" source ./tmp_env/bin/activate

# Install the dependencies required for setup
pip install -r ../util_files/requirements_setup.txt

# Start the Django site
python ./tmp_env/bin/django-admin startproject $1

# Copy pre-built files to the site folder
cp ../util_files/requirements.txt $1/
cp ../util_files/Dockerfile.template $1/
cp ../util_files/docker-compose.yml $1/
cp ../util_files/nginx.conf $1/
cp ../util_files/export_labels.R $1/
cp ../util_files/install_dependencies.R $1/

# Enter the Django site directory
cd $1

# Create the storage directory for snapshots
mkdir snapshots

# Add site name to Dockerfile template
sed -e "s/SITE_NAME/$1/g" ./Dockerfile.template > ./Dockerfile
rm ./Dockerfile.template

# Make Django site manager script executable
chmod +x ./manage.py

# Create the Django application for the models
./manage.py startapp core

# Create the Django application for database snapshots
./manage.py startapp snapshot_manager

# Copy pre-built application scripts to the application
cp -r ../../app_includes/* ./core/
cp ../../pytrackdat/common.py ./core/

# Deactivate the temporary setup virtual environment
deactivate
