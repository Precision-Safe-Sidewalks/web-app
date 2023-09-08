#!/bin/bash
set -e


python3 manage.py migrate sites
python3 manage.py makemigrations microsoft_auth
python3 manage.py makemigrations --check --dry-run
