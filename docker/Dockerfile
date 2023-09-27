# production stage
FROM python:3.9-slim-buster

EXPOSE 8080

RUN useradd -m -s /bin/bash django

# Install the application
RUN set -ex \
    && apt update \
    && apt install -y gettext gcc \
    # Third libraries dependencies
    # && apk --update add ... \
    && pip install -U pip uwsgi

COPY --chown=django:django .. /app
RUN set -ex \
    && pip install --trusted-host pypi.python.org -r /app/requirements/dev.txt

COPY --chown=django:django docker/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY --chown=django:django docker/prestart.sh /prestart.sh

WORKDIR /app

USER django

RUN chmod +x /prestart.sh

ENTRYPOINT ["sh", "/prestart.sh"]

CMD ["uwsgi", "--uid", "django", "--ini", "/etc/uwsgi/uwsgi.ini", "--protocol", "http"]
