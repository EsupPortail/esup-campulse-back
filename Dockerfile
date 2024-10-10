FROM python:3.9-slim-bullseye

LABEL maintainer="DNum DIP - Université de Strasbourg <dnum-dip@unistra.fr>" \
      app="plana"

EXPOSE 8080

RUN useradd -m -s /bin/bash django

# Install the application
RUN set -ex \
    && apt-get update \
    && apt-get install -y gettext gcc locales tzdata \
    && localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8 \
    && ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && pip install -U pip uwsgi \
    # Key gen
    && apt-get install -y age openssh-client \
    # Weasyprint dependencies
    && apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG fr_FR.UTF-8

COPY --chown=django:django . /app
COPY --chown=django:django uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY --chown=django:django --chmod=755 prestart.sh /prestart.sh

WORKDIR /app

USER django

RUN set -ex \
    && mkdir assets logs \
    && pip install --trusted-host pypi.python.org -r /app/requirements/prod.txt \
    && pip cache purge

ENTRYPOINT ["sh", "/prestart.sh"]

CMD ["uwsgi", "--uid", "django", "--ini", "/etc/uwsgi/uwsgi.ini", "--protocol", "http"]
