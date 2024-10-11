#! /usr/bin/env sh
set -e
echo "Running inside /app/prestart.sh"

# Don't stop building when compilemessages fail
cd /app
python manage.py migrate
python manage.py compilemessages || true
python manage.py collectstatic --no-input --clear

if [ ! -f keys/jwt-private-key.pem ]
then
    python manage.py generate_jwt_keys
fi

if [ ! -f keys/age-private-key.key ]
then
    python manage.py generate_age_keys
fi

python manage.py initial_import --test
# python manage.py loaddata_storages
env

exec "$@"
