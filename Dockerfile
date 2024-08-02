# syntax=docker/dockerfile:1.2
ARG PYTHON_VERSION=3.12

# build stage : collect wheels from requirements & dist/*.whl
FROM python:${PYTHON_VERSION}-slim AS builder

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt-get update && apt-get install -y \
        # gettext for compilemessages
        gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # DevSecOps: don't run as root
    && addgroup --system --gid 100 users \
    && useradd --system --no-log-init \
        --shell /usr/sbin/nologin \
        --create-home --home-dir /app \
        --gid 100 --uid 123 \
        plana

USER 123:100

# Prepare dependencies wheels (compile) from locked requirements
COPY --chown=123:100 requirements/prod.txt /app/requirements.txt
ARG PIP_CACHE_DIR=/var/run/pip/cache
RUN pip wheel \
        --wheel-dir /app/wheelhouse \
        --require-hashes --requirement /app/requirements.txt \
    # ….ldap accounts… need ldap3
    && pip wheel \
        --wheel-dir /app/wheelhouse \
        'ldap3<3'

# install plana and dependencies wheels
COPY --chown=123:100 dist/*.whl /app/dist/
RUN \
    # 'Prepare app wheel (compile)'
    pip wheel --no-cache-dir \
        --wheel-dir /app/wheelhouse \
        --no-deps /app/dist/*.whl \
    # 'install plana and dependencies wheels'
    && export HOME=/app \
    && pip install --root-user-action ignore --no-cache --no-index --no-deps --prefix /app/.local /app/wheelhouse/* \
    # env for settings
    && export HOME=/app SITE_ROOT=/app \
        DATABASE_URL=sqlite://:memory: \
        SECRET_KEY=not-needed-here \
        AGE_PRIVATE_KEY=not-needed-here \
        SIMPLE_JWT_SIGNING_KEY=not-needed-here \
        SIMPLE_JWT_VERIFYING_KEY=not-needed-here \
        USE_S3=False \
    # manage.py compilemessages
    && /app/.local/bin/django-admin \
        compilemessages --locale fr \
        --settings plana.settings.oci \
    # manage.py collectstatic
    && /app/.local/bin/django-admin \
        collectstatic \
            --no-input \
            --skip-checks \
            --settings plana.settings.oci \
    # clean up
    && rm -rf /app/dist /tmp/plana || true

## Compile installed code:
#RUN python -c "import compileall; \
#  compileall.compile_path(maxlevels=10)"
## Compile installed code:
# Compile code in a directory:
#RUN python -m compileall plana/

#
# base layer with plana installed
#
FROM python:${PYTHON_VERSION}-slim AS plana

RUN export DEBIAN_FRONTEND=noninteractive \
&& apt-get update && apt-get install -y \
        # libpango required by weasyprint (apt install weasyprint)
        libpango-1.0-0 libpangoft2-1.0-0 \
        locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8 \
    && mkdir -p /app

ENV SITE_ROOT=/app \
    PATH=/app/.local/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    LANGUAGE=fr \
    LANG=fr_FR.UTF-8 \
    TZ=Europe/Paris \
    DJANGO_SETTINGS_MODULE="plana.settings.oci"

# Tracebacks on crashes n C code
COPY --from=builder --chown=0:0 /app/.local /app/.local
RUN \
    # DevSecOps: prepare a user & group 'cause don't run as root
    addgroup --system --gid 789 app \
    && useradd --system --no-log-init \
        --shell /usr/sbin/nologin \
        --no-create-home --home-dir /app \
        --gid app --uid 987 plana \
    # needed writable directories (.cache for fc-cache)
    && install --owner=987 --group=789 --directory /app/.cache /app/media /app/keys \
    # additional mount points
    && install --owner=0 --group=789 --directory /app/static /app/templates \
    # env for settings
    && export HOME=/app SITE_ROOT=/app \
        DATABASE_URL=sqlite://:memory: \
        SECRET_KEY=not-needed-here \
        AGE_PRIVATE_KEY=not-needed-here \
        SIMPLE_JWT_SIGNING_KEY=not-needed-here \
        SIMPLE_JWT_VERIFYING_KEY=not-needed-here \
        USE_S3=False \
    # manage.py collectstatic (symlinks)
    && /app/.local/bin/django-admin \
        collectstatic --link \
            --no-input \
            --skip-checks \
            --settings plana.settings.oci \
    # link application dir for manage.py scripts
    && ln -sfT /app/.local/lib/python3.12/site-packages/plana /app/plana \
    # clean up
    && rm -rf /app/dist /tmp/plana || true

WORKDIR /app

#
# plana/static : plana/static on nginx
#
FROM nginx:mainline AS plana-static

RUN rm -f /usr/share/nginx/html/index.html
COPY --from=builder --chown=0:0 /app/static /usr/share/nginx/html/site_media

HEALTHCHECK \
    --interval=30s \
    --timeout=30s \
    --retries=3 \
    CMD curl -sIfo/dev/null http://127.0.0.1:${NGINX_PORT}/50x.html

#
# plana/admin : django-admin / manage.py commands
#
FROM plana AS plana-admin

USER 987:789
ENTRYPOINT ["/app/.local/bin/django-admin"]
CMD [ "help" ]

#
# plana/server : plana on gunicorn w/ healthcheck
#
FROM plana AS plana-back

# install curl for HEALTHCHECK
RUN apt-get update && apt-get install -y \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install gunicorn
ARG PIP_CACHE_DIR=/var/run/pip/cache
RUN pip install --root-user-action ignore gunicorn

USER 987:789

# gunicorn port
ENV PORT=8000
EXPOSE 8000/tcp

ENTRYPOINT ["gunicorn", \
    "--env", "DJANGO_SETTINGS_MODULE=plana.settings.oci", \
    "--name=plana", "plana.wsgi:application"]

HEALTHCHECK \
    --interval=30s \
    --timeout=30s \
    --retries=3 \
    CMD curl -sfIo/dev/null -H "Accept: application/json" http://localhost:${PORT}/_hc/ || exit 1
