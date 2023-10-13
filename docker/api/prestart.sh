#! /usr/bin/env sh
set -e
echo "Running inside /prestart.sh"

cd /app/plana-api
python manage.py migrate
# Don't stop building when compilemessages fail
python manage.py compilemessages || true
python manage.py initial_import --test
python manage.py loaddata_storages
mkdir -p keys
python manage.py generate_jwt_keys --keep-keys
python manage.py generate_age_keys --keep-keys

exec "$@"

