#! /usr/bin/env sh
set -e
echo "Running inside /prestart.sh"

cd /app
python manage.py migrate
# Don't stop building when compilemessages fail
python manage.py compilemessages || true
python manage.py initial_import
python manage.py generate_jwt_keys
python manage.py generate_age_keys

exec "$@"

