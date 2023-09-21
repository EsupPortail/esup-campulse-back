# -*- coding: utf-8 -*-

"""
"""

from os.path import join

import pydiploy
from fabric.api import env, execute, roles, task

from . import sentry

# edit config here !

env.remote_owner = 'django'  # remote server user
env.remote_group = 'di'  # remote server group

env.application_name = 'plana'  # name of webapp
env.root_package_name = 'plana'  # name of app in webapp

env.remote_home = '/home/django'  # remote home root
env.remote_python_version = '3.9'  # python version
env.remote_virtualenv_root = join(env.remote_home, '.virtualenvs')  # venv root
env.remote_virtualenv_dir = join(env.remote_virtualenv_root, env.application_name)  # venv for webapp dir
# git repository url
env.remote_repo_url = 'git@git.unistra.fr:di/plan_a/plana.git'
env.local_tmp_dir = '/tmp'  # tmp dir
env.remote_static_root = '/var/www/static/'  # root of static files
env.locale = 'fr_FR.UTF-8'  # locale to use on remote
env.timezone = 'Europe/Paris'  # timezone for remote
env.keep_releases = 2  # number of old releases to keep before cleaning
env.extra_goals = ['preprod']  # add extra goal(s) to defaults (test,dev,prod)
env.dipstrap_version = 'latest'
env.verbose_output = False  # True for verbose output

# optional parameters

# env.dest_path = '' # if not set using env_local_tmp_dir
# env.excluded_files = ['pron.jpg'] # file(s) that rsync should exclude when deploying app
# env.extra_ppa_to_install = ['ppa:vincent-c/ponysay'] # extra ppa source(s) to use
# extra debian/ubuntu package(s) to install on remote
env.extra_pkg_to_install = ['age']
# env.cfg_shared_files = ['config','/app/path/to/config/config_file'] # config files to be placed in shared config dir
# dirs to be symlinked in shared directory
env.extra_symlink_dirs = ['keys']
# env.verbose = True # verbose display for pydiploy default value = True
# env.req_pydiploy_version = "0.9" # required pydiploy version for this fabfile
# env.no_config_test = False # avoid config checker if True
# env.maintenance_text = "" # add a customize maintenance text for maintenance page
# env.maintenance_title = "" # add a customize title for maintenance page
# env.oracle_client_version = '11.2'
# env.oracle_download_url = 'http://librepo.net/lib/oracle/'
# env.oracle_remote_dir = 'oracle_client'
# env.oracle_packages = ['instantclient-basic-linux-x86-64-11.2.0.2.0.zip',
#                        'instantclient-sdk-linux-x86-64-11.2.0.2.0.zip',
#                        'instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip']
#
# env.circus_package_name = 'https://github.com/morganbohn/circus/archive/master.zip'
env.no_circus_web = True  # Avoid using circusweb dashboard (buggy in last releases)
# env.circus_backend = 'gevent' # name of circus backend to use

env.chaussette_backend = (
    'waitress'  # name of chaussette backend to use. You need to add this backend in the app requirement file.
)


env.nginx_location_extra_directives = [
    'client_max_body_size 8M',
    'add_header Strict-Transport-Security "max-age=63072000"',
    'add_header Content-Security-Policy "upgrade-insecure-requests; default-src \'none\'; base-uri \'self\'; connect-src \'self\'; font-src \'self\' https://stackpath.bootstrapcdn.com; frame-ancestors \'self\'; frame-src \'self\'; img-src \'self\'; script-src \'self\' \'unsafe-inline\' \'unsafe-eval\' https://code.jquery.com https://stackpath.bootstrapcdn.com; style-src \'self\' \'unsafe-inline\' https://stackpath.bootstrapcdn.com;"',
]  # add directive(s) to nginx config file in location part
# env.nginx_start_confirmation = True # if True when nginx is not started
# needs confirmation to start it.
env.sentry_project_name = 'plan-a-back'


@task
def dev():
    """Define dev stage"""
    env.roledefs = {
        'web': ['192.168.1.2'],
        'lb': ['192.168.1.2'],
    }
    env.user = 'vagrant'
    env.backends = env.roledefs['web']
    env.server_name = 'plana-dev.net'
    env.short_server_name = 'plana-dev'
    env.static_folder = '/site_media/'
    env.server_ip = '192.168.1.2'
    env.no_shared_sessions = False
    env.server_ssl_on = False
    env.goal = 'dev'
    env.socket_port = '8001'
    env.map_settings = {}
    execute(build_env)


@task
def test():
    """Define test stage"""
    env.roledefs = {
        'web': ['django-test2.u-strasbg.fr'],
        'lb': ['django-test2.u-strasbg.fr'],
    }
    # env.user = 'root'  # user for ssh
    env.backends = ['127.0.0.1']
    env.server_name = 'plana-api-test.app.unistra.fr'
    env.short_server_name = 'plana-test'
    env.static_folder = '/site_media/'
    env.server_ip = ''
    env.no_shared_sessions = False
    env.server_ssl_on = True
    env.path_to_cert = '/etc/ssl/certs/mega_wildcard.pem'
    env.path_to_cert_key = '/etc/ssl/private/mega_wildcard.key'
    env.goal = 'test'
    env.socket_port = '8038'
    env.socket_host = '127.0.0.1'
    env.map_settings = {
        'default_db_host': 'DATABASES["default"]["HOST"]',
        'default_db_user': 'DATABASES["default"]["USER"]',
        'default_db_password': 'DATABASES["default"]["PASSWORD"]',
        'default_db_name': 'DATABASES["default"]["NAME"]',
        's3_access_key': "AWS_ACCESS_KEY_ID",
        's3_secret_key': "AWS_SECRET_ACCESS_KEY",
        's3_bucket': "AWS_STORAGE_BUCKET_NAME",
        's3_endpoint': "AWS_S3_ENDPOINT_URL",
        'accounts_api_spore_description_file': 'ACCOUNTS_API_CONF["DESCRIPTION_FILE"]',
        'accounts_api_spore_base_url': 'ACCOUNTS_API_CONF["BASE_URL"]',
        'accounts_api_spore_token': 'ACCOUNTS_API_CONF["TOKEN"]',
    }
    execute(build_env)


@task
def preprod():
    """Define preprod stage"""
    env.roledefs = {
        'web': ['django-pprd-w3.di.unistra.fr', 'django-pprd-w4.di.unistra.fr'],
        'lb': ['rp-dip-pprd-public.di.unistra.fr'],
    }
    # env.user = 'root'  # user for ssh
    env.backends = env.roledefs['web']
    env.server_name = 'plana-api-pprd.app.unistra.fr'
    env.short_server_name = 'plana-pprd'
    env.static_folder = '/site_media/'
    env.server_ip = '130.79.245.212'
    env.no_shared_sessions = False
    env.server_ssl_on = True
    env.path_to_cert = '/etc/ssl/certs/mega_wildcard.pem'
    env.path_to_cert_key = '/etc/ssl/private/mega_wildcard.key'
    env.goal = 'preprod'
    env.socket_port = '8056'
    env.map_settings = {
        'default_db_host': 'DATABASES["default"]["HOST"]',
        'default_db_user': 'DATABASES["default"]["USER"]',
        'default_db_password': 'DATABASES["default"]["PASSWORD"]',
        'default_db_name': 'DATABASES["default"]["NAME"]',
        's3_access_key': "AWS_ACCESS_KEY_ID",
        's3_secret_key': "AWS_SECRET_ACCESS_KEY",
        's3_bucket': "AWS_STORAGE_BUCKET_NAME",
        's3_endpoint': "AWS_S3_ENDPOINT_URL",
        'secret_key': 'SECRET_KEY',
        'health_check_secret_key': 'HEALTH_CHECK_SECRET_KEY',
        'accounts_api_spore_description_file': 'ACCOUNTS_API_CONF["DESCRIPTION_FILE"]',
        'accounts_api_spore_base_url': 'ACCOUNTS_API_CONF["BASE_URL"]',
        'accounts_api_spore_token': 'ACCOUNTS_API_CONF["TOKEN"]',
    }
    execute(build_env)


@task
def prod():
    """Define prod stage"""
    env.roledefs = {
        'web': ['django-w7.di.unistra.fr', 'django-w8.di.unistra.fr'],
        'lb': ['rp-dip-public-m.di.unistra.fr', 'rp-dip-public-s.di.unistra.fr'],
    }
    # env.user = 'root'  # user for ssh
    env.backends = env.roledefs['web']
    env.server_name = 'api.etu-campulse.fr'
    env.short_server_name = 'plana-api'
    env.static_folder = '/site_media/'
    env.server_ip = '130.79.245.214'
    env.no_shared_sessions = False
    env.server_ssl_on = True
    env.path_to_cert = '/etc/ssl/certs/mega_wildcard.pem'
    env.path_to_cert_key = '/etc/ssl/private/mega_wildcard.key'
    env.goal = 'prod'
    env.socket_port = '8014'
    env.map_settings = {
        'default_db_host': 'DATABASES["default"]["HOST"]',
        'default_db_user': 'DATABASES["default"]["USER"]',
        'default_db_password': 'DATABASES["default"]["PASSWORD"]',
        'default_db_name': 'DATABASES["default"]["NAME"]',
        's3_access_key': "AWS_ACCESS_KEY_ID",
        's3_secret_key': "AWS_SECRET_ACCESS_KEY",
        's3_bucket': "AWS_STORAGE_BUCKET_NAME",
        's3_endpoint': "AWS_S3_ENDPOINT_URL",
        'secret_key': 'SECRET_KEY',
        'health_check_secret_key': 'HEALTH_CHECK_SECRET_KEY',
        'accounts_api_spore_description_file': 'ACCOUNTS_API_CONF["DESCRIPTION_FILE"]',
        'accounts_api_spore_base_url': 'ACCOUNTS_API_CONF["BASE_URL"]',
        'accounts_api_spore_token': 'ACCOUNTS_API_CONF["TOKEN"]',
    }
    execute(build_env)


# dont touch after that point if you don't know what you are doing !


@task
def tag(version_number):
    """Set the version to deploy to `version_number`."""
    execute(pydiploy.prepare.tag, version=version_number)


@roles(['web', 'lb'])
def build_env():
    execute(pydiploy.prepare.build_env)


@task
def pre_install():
    """Pre install of backend & frontend"""
    execute(pre_install_backend)
    execute(pre_install_frontend)


@roles('web')
@task
def pre_install_backend():
    """Setup server for backend"""
    execute(pydiploy.django.pre_install_backend, commands='/usr/bin/rsync')


@roles('lb')
@task
def pre_install_frontend():
    """Setup server for frontend"""
    execute(pydiploy.django.pre_install_frontend)


@task
def deploy(update_pkg=False):
    """Deploy code on server"""
    execute(deploy_backend, update_pkg)
    execute(declare_release_to_sentry)
    execute(deploy_frontend)


@roles('web')
@task
def deploy_backend(update_pkg=False):
    """Deploy code on server"""
    execute(pydiploy.django.deploy_backend, update_pkg)


@roles('lb')
@task
def deploy_frontend():
    """Deploy static files on load balancer"""
    execute(pydiploy.django.deploy_frontend)


@roles('web')
@task
def rollback():
    """Rollback code (current-1 release)"""
    execute(pydiploy.django.rollback)


@task
def post_install():
    """post install for backend & frontend"""
    execute(post_install_backend)
    execute(post_install_frontend)


@roles('web')
@task
def post_install_backend():
    """Post installation of backend"""
    execute(pydiploy.django.post_install_backend)


@roles('lb')
@task
def post_install_frontend():
    """Post installation of frontend"""
    execute(pydiploy.django.post_install_frontend)


@roles('web')
@task
def install_postgres(user=None, dbname=None, password=None):
    """Install Postgres on remote"""
    execute(
        pydiploy.django.install_postgres_server,
        user=user,
        dbname=dbname,
        password=password,
    )


@task
def reload():
    """Reload backend & frontend"""
    execute(reload_frontend)
    execute(reload_backend)


@task
def declare_release_to_sentry():
    execute(sentry.declare_release)


@roles('lb')
@task
def reload_frontend():
    execute(pydiploy.django.reload_frontend)


@roles('web')
@task
def reload_backend():
    execute(pydiploy.django.reload_backend)


@roles('lb')
@task
def set_down():
    """Set app to maintenance mode"""
    execute(pydiploy.django.set_app_down)


@roles('lb')
@task
def set_up():
    """Set app to up mode"""
    execute(pydiploy.django.set_app_up)


@roles('web')
@task
def custom_manage_cmd(cmd):
    """Execute custom command in manage.py"""
    execute(pydiploy.django.custom_manage_command, cmd)


@roles("web")
@task
def update_python_version():
    """Update python version"""
    execute(pydiploy.django.update_python_version)
