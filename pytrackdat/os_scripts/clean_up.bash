#!/usr/bin/env bash

set -eu

# Enter the temporary site construction directory
cd $3

# Remove existing site data if it exists
rm -rf ./tmp_env 2> /dev/null
rm -rf ./$2 2> /dev/null
