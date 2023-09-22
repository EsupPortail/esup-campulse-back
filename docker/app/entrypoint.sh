#!/bin/sh
set -e
cd /home/plana/api

python manage.py migrate
python manage.py compilemessages
python manage.py initial_import
python manage.py generate_jwt_keys
python manage.py generate_age_keys

exec "$@"
