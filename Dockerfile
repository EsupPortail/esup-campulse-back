FROM python:3.9-slim-bullseye

LABEL maintainer="DNum DIP - Université de Strasbourg <dnum-dip@unistra.fr>" \
      app="plana"

EXPOSE 8080

WORKDIR /app

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

COPY . .
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

RUN set -ex \
    && mkdir -p assets logs \
    && pip install --trusted-host pypi.python.org -r requirements/prod.txt \
    && pip cache purge

RUN chgrp -R 0 /app && \
    chmod -R g+rwX /app

ENTRYPOINT ["sh", "/app/prestart.sh"]

CMD ["uwsgi", "--ini", "/etc/uwsgi/uwsgi.ini", "--protocol", "http"]
