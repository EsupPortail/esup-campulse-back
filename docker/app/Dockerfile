FROM python:3.9-slim-bullseye

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .
COPY ./docker/app/entrypoint.sh /usr/local/bin/

RUN BUILD_DEPS=" \
  gettext \
  locales" \
  && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS; \
  sed -i 's/psycopg2==/psycopg2-binary==/g' /usr/src/app/requirements/common.txt; \
  pip install --no-cache-dir -r requirements/dev.txt; \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf '/var/lib/apt/lists/*';\
  sed -i 's/{{ goal }}/docker-dev/g' /usr/src/app/manage.py; \
  sed -i 's/\r$//g' /usr/local/bin/entrypoint.sh; \
  chmod +x /usr/local/bin/entrypoint.sh;

ENTRYPOINT ["entrypoint.sh"]
