#! /usr/bin/env sh
set -e
echo "Running inside /app/docker-prestart.sh"

# Don't stop building when compilemessages fail
cd /app
python manage.py migrate
python manage.py compilemessages || true

python manage.py initial_import --storages
# env

exec "$@"
