"""Configuration for production OCI container image."""

from importlib import metadata
from datetime import timedelta
import environ
from pathlib import Path
from socket import getfqdn
from . import base

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


APP_VERSION = metadata.version('plana')

######################
# Path configuration #
######################

DJANGO_ROOT = Path(__file__).resolve(strict=True).parent.parent # project root
# read .env file
env = environ.FileAwareEnv()
env.read_env(env.str('ENV_PATH', default=env.path('SITE_ROOT', default=DJANGO_ROOT.parent)('.env')))
SITE_ROOT = env('SITE_ROOT',cast=Path, default=DJANGO_ROOT.parent)

REQUIRED=env.NOTSET


#######################
# Debug configuration #
#######################

DEBUG = env.bool('DEBUG', default=False)
TEMPLATE_DEBUG = env.bool('TEMPLATE_DEBUG', default=DEBUG)

##########################
# Manager configurations #
##########################

ADMINS = env.list('ADMINS', default=[])
    # ('Your Name', 'your_email@example.com'),

MANAGERS = env.list('MANAGERS', default=ADMINS)

DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default="plan-a.noreply@unistra.fr")


##########################
# Database configuration #
##########################

# In your virtualenv, edit the file $VIRTUAL_ENV/bin/postactivate and set
# properly the environnement variable defined in this file (ie: os.environ[KEY])
# ex: export DEFAULT_DB_USER='plana'

# Default values for default database are :
# engine : sqlite3
# name : PROJECT_ROOT_DIR/plana.db

# default db connection
# doc → https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': env('DATABASE_URL', cast=env.db_url_config, default=None) or {
        "ENGINE": env.str('DATABASE_ENGINE', default=env.DB_SCHEMES['postgresql']),
        "NAME": env.str('DATABASE_NAME', default='plana'),
        "USER": env.str('DATABASE_USER', default=''),
        "PASSWORD": env.str('DATABASE_PASSWORD', default=''),
        "HOST": env.str('DATABASE_HOST', default=REQUIRED),
        "PORT": env.str('DATABASE_PORT', default=''),
        "CONN_MAX_AGE": env.int('DATABASE_CONN_MAX_AGE', default=None),
        "CONN_HEALTH_CHECKS": env.bool('DATABASE_CONN_HEALTH_CHECKS', default=False),
        "OPTIONS": env.json('DATABASE_OPTIONS', default={})
    }
}


######################
# Site configuration #
######################

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[] if DEBUG else ["*"])

##########
# Emails #
##########

EMAIL_HOST = env.str('EMAIL_HOST', default="maildev")
EMAIL_PORT = env.int('EMAIL_PORT', default=1025)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default="")
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default="")
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)

EMAIL_TEMPLATE_FRONTEND_URL = env('EMAIL_TEMPLATE_FRONTEND_URL', default="maildev:3000/")

#########################
# General configuration #
#########################

# Local time zone for this installation. Choices can be found here:
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = env.str('TZ', default='Europe/Paris')

# Language code for this installation. All choices can be found here:
# https://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = env.str('LANGUAGE', default='fr-FR')

SITE_ID = env.int('SITE_ID', default=1)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
# USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


########################
# Locale configuration #
########################

LOCALE_PATHS = [
    DJANGO_ROOT / "locale"
]


#######################
# Media configuration #
#######################

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = env.str('MEDIA_ROOT', default=DJANGO_ROOT / "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = "/media/"


##############################
# Static files configuration #
##############################

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
#STATIC_ROOT = env.str('STATIC_ROOT', default=DJANGO_ROOT / "static")
STATIC_ROOT = "/app/static"

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/site_media/"

# Additional locations of static files
STATICFILES_DIRS = [
    DJANGO_ROOT / 'static',
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


############
# Dipstrap #
############

DIPSTRAP_STATIC_URL = env.str('DIPSTRAP_STATIC_URL', default='//django-static.u-strasbg.fr/dipstrap/')


##############
# Secret key #
##############

# Make this unique, and don't share it with anybody.
# Only for dev and test environnement. Should be redefined for production
# environnement
SECRET_KEY = env.str('SECRET_KEY', default=REQUIRED)


##########################
# Template configuration #
##########################

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            SITE_ROOT / 'templates',
            DJANGO_ROOT / 'templates',
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]


########
# CORS #
########

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = (
    "x-requested-with",
    "content-type",
    "accept",
    "origin",
    "authorization",
    "x-csrftoken",
    "range",
)

############################
# Middleware configuration #
############################

MIDDLEWARE = base.MIDDLEWARE

#####################
# Url configuration #
#####################

ROOT_URLCONF = base.ROOT_URLCONF

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "ssl")

#HEALTH_CHECK = {
#        # .....
#        "SUBSETS": {
#            "startup-probe": ["MigrationsHealthCheck", "DatabaseBackend"],
#            "liveness-probe": ["DatabaseBackend"],
#            "<SUBSET_NAME>": ["<Health_Check_Service_Name>"]
#        },
#        # .....
#    }

######################
# WSGI configuration #
######################

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'plana.wsgi.application'


#############################
# Application configuration #
#############################

INSTALLED_APPS = base.DJANGO_APPS + base.THIRD_PARTY_APPS + base.LOCAL_APPS

# remove ADMIN if denied (ADMIN_APP=False)
if not env.bool('ADMIN_APP',default=True):
    INSTALLED_APPS = [ app for app in INSTALLED_APPS if app != 'django.contrib.admin' ]

#########################
# Session configuration #
#########################

SESSION_SERIALIZER = base.SESSION_SERIALIZER


#####################
# Log configuration #
#####################

LOGGING = base.LOGGING
# drop file logging in containers
if 'file' in LOGGING['handlers']:
    del LOGGING['handlers']['file']
LOGGING['handlers']['console'] = {
    "level": "INFO",
    "class": "logging.StreamHandler",
    "stream": "ext://sys.stdout",
}
LOGGING['loggers'][''] = {
    "handlers": ["console"],
    "level": "INFO",
}
LOGGING['loggers']['plana']['handlers'] = [ 'console' ]
LOGGING['loggers']['external_accounts']['handlers'] = [ 'console' ]
LOGGING['loggers']['django']['handlers'] = [ 'console' ]

if 'LOGGING' in env:
    LOGGING.update(env.json('LOGGING'))

#########################
# DJANGO REST FRAMEWORK #
#########################

REST_FRAMEWORK = base.REST_FRAMEWORK

##################
# Storage config #
##################

STORAGES = base.STORAGES

USE_S3 = env.bool('USE_S3', default=True)  # TODO FileSystemStorage implementation not finished (encryption not available, migrations errors).
if USE_S3:
    AWS_S3_FILE_OVERWRITE = True
    AWS_DEFAULT_ACL = None
    AWS_USE_OBJECT_ACL = env.bool("AWS_USE_OBJECT_ACL", default=True)
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default=REQUIRED)
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default=REQUIRED)
    AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default=REQUIRED)
    AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default=REQUIRED)
    AWS_S3_PUBLIC_URL = env.str("AWS_S3_PUBLIC_URL", default=AWS_S3_ENDPOINT_URL+'/'+AWS_STORAGE_BUCKET_NAME)
else:
    AWS_USE_OBJECT_ACL = False
    AWS_S3_PUBLIC_URL = MEDIA_URL

S3_LOGOS_FILEPATH = base.S3_LOGOS_FILEPATH
S3_ASSOCIATIONS_LOGOS_FILEPATH = base.S3_ASSOCIATIONS_LOGOS_FILEPATH
S3_TEMPLATES_FILEPATH = base.S3_TEMPLATES_FILEPATH
S3_DOCUMENTS_FILEPATH = base.S3_DOCUMENTS_FILEPATH

AGE_PRIVATE_KEY = env.bytes('AGE_PRIVATE_KEY', default=REQUIRED)
AGE_PUBLIC_KEY = env.bytes('AGE_PUBLIC_KEY', default=None)

#####################
# DJANGO THUMBNAILS #
#####################

THUMBNAILS = base.THUMBNAILS
THUMBNAILS['STORAGE']['BACKEND'] = STORAGES["default"]["BACKEND"]

##################
# AUTHENTICATION #
##################

CAS_ID = env.str('CAS_ID', default=base.CAS_ID)
CAS_NAME = env.str('CAS_NAME', default=base.CAS_NAME)
CAS_SERVER = env.str('CAS_SERVER', default=base.CAS_SERVER)
CAS_VERSION = env.int('CAS_VERSION', default=base.CAS_VERSION)
CAS_AUTHORIZED_SERVICES = env.list('CAS_AUTHORIZED_SERVICES', default=["http://localhost:8000/users/auth/cas_verify/"])

# Keys are User model fields, values are CAS fields.
CAS_ATTRIBUTES_NAMES = env.dict("CAS_ATTRIBUTES_NAMES",default={
    "email": "mail",
    "first_name": "first_name",
    "last_name": "last_name",
    "is_student": "affiliation",
})
# Keys are User model fields, values are CAS values waited for those model fields.
CAS_ATTRIBUTES_VALUES = env.dict("CAS_ATTRIBUTES_VALUES",default={
    "is_student": "student",
})

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_ADAPTER = base.ACCOUNT_ADAPTER
ACCOUNT_UNIQUE_EMAIL = base.ACCOUNT_UNIQUE_EMAIL
ACCOUNT_EMAIL_REQUIRED = base.ACCOUNT_EMAIL_REQUIRED
ACCOUNT_EMAIL_VERIFICATION = base.ACCOUNT_EMAIL_VERIFICATION
ACCOUNT_DEFAULT_HTTP_PROTOCOL = base.ACCOUNT_DEFAULT_HTTP_PROTOCOL
ACCOUNT_USERNAME_BLACKLIST = base.ACCOUNT_USERNAME_BLACKLIST

SOCIALACCOUNT_ADAPTER = base.SOCIALACCOUNT_ADAPTER
SOCIALACCOUNT_EMAIL_VERIFICATION = base.SOCIALACCOUNT_EMAIL_VERIFICATION
SOCIALACCOUNT_EMAIL_REQUIRED = base.SOCIALACCOUNT_EMAIL_REQUIRED

SOCIALACCOUNT_PROVIDERS = base.SOCIALACCOUNT_PROVIDERS

# Using SimpleJWT with dj-rest-auth
SIMPLE_JWT = env.dict("SIMPLE_JWT",default=None) or {
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=1),
    "ALGORITHM": "RS256",
    "AUDIENCE": "plan_a",
    "ISSUER": "plan_a",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}
# get or compute VERIFYING_KEY
if SIMPLE_JWT.get('ALGORITHM') in ('RS256','RS384','RS512'):
    if "SIGNING_KEY" not in SIMPLE_JWT:
        SIMPLE_JWT["SIGNING_KEY"] = env.str("SIMPLE_JWT_SIGNING_KEY", default=REQUIRED),
    if "SIMPLE_JWT_VERIFYING_KEY" in env:
        SIMPLE_JWT["VERIFYING_KEY"] = env.str("SIMPLE_JWT_VERIFYING_KEY"),
    else:
        from cryptography.hazmat.primitives import serialization
        private_key = serialization.load_pem_private_key(SIMPLE_JWT["SIGNING_KEY"],password=None)
        public_key = private_key.public_key()
        SIMPLE_JWT["VERIFYING_KEY"] = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
    "LOGIN_SERIALIZER": "plana.apps.users.serializers.user_auth.LoginSerializer",
    "USER_DETAILS_SERIALIZER": "plana.apps.users.serializers.user.UserSerializer",
    "PASSWORD_RESET_SERIALIZER": "plana.apps.users.serializers.user_auth.PasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "plana.apps.users.serializers.user_auth.PasswordResetConfirmSerializer",
    "PASSWORD_CHANGE_SERIALIZER": "plana.apps.users.serializers.user_auth.PasswordChangeSerializer",
    "REGISTER_SERIALIZER": "plana.apps.users.serializers.user.CustomRegisterSerializer",
}


##########
# Sentry #
##########

STAGE = None
SENTRY_DSN = "https://72691d0aec61475a80d93ac9b634ca57@sentry.app.unistra.fr/54"


if "SENTRY_DSN" in env:
    """Init Sentry service."""
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        environment=env.str('SENTRY_ENVIRONMENT',default=REQUIRED),
        release=f"plana@{APP_VERSION}",
        send_default_pii=True,
        traces_sample_rate=1.0,
    )


###############
# Spectacular #
###############

SPECTACULAR_SETTINGS = base.SPECTACULAR_SETTINGS
SPECTACULAR_SETTINGS['VERSION']= APP_VERSION


################################
# URL parts in email templates #
################################

EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_PATH = base.EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_PATH
EMAIL_TEMPLATE_PASSWORD_RESET_PATH = base.EMAIL_TEMPLATE_PASSWORD_RESET_PATH
EMAIL_TEMPLATE_PASSWORD_CHANGE_PATH = base.EMAIL_TEMPLATE_PASSWORD_CHANGE_PATH
EMAIL_TEMPLATE_ACCOUNT_VALIDATE_PATH = base.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_PATH
EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH = base.EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH
EMAIL_TEMPLATE_DOCUMENT_VALIDATE_PATH = base.EMAIL_TEMPLATE_DOCUMENT_VALIDATE_PATH


################
# PDF Templates #
#################

# S3 configuration for PDF templates (used to store PDF exports and notifications).
S3_PDF_FILEPATH = env.str("settings.S3_PDF_FILEPATH",default="pdf" if USE_S3 else ".")
TEMPLATES_PDF_EXPORTS_FOLDER = env.str("TEMPLATES_PDF_EXPORTS_FOLDER",default="templates/exports" if USE_S3 else "pdf/exports")
TEMPLATES_PDF_NOTIFICATIONS_FOLDER = env.str("TEMPLATES_PDF_NOTIFICATIONS_FOLDER",default="templates/notifications" if USE_S3 else "pdf/notifications")

TEMPLATES_PDF_FILEPATHS = env.dict("TEMPLATES_PDF_FILEPATHS",default={
    "association_charter_summary": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/association_charter_summary.html",
    "commission_projects_list": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/commission_projects_list.html",
    "project_summary": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/project_summary.html",
    "project_review_summary": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/project_review_summary.html",
})


########
# Misc #
########

# Defining default format for database identifiers.
DEFAULT_AUTO_FIELD = base.DEFAULT_AUTO_FIELD

# Extending the abstract User class.
AUTH_USER_MODEL = base.AUTH_USER_MODEL

# Avoid errors while testing the API with cURL.
APPEND_SLASH = base.APPEND_SLASH

# Site name as set in migration in contents module.
MIGRATION_SITE_DOMAIN = (
    env.str("MIGRATION_SITE_DOMAIN",default=None)
    or env.str("SITE_DOMAIN", default=None)
    or getfqdn()
)
MIGRATION_SITE_NAME = (
    env.str("MIGRATION_SITE_NAME",default=None)
    or env.str("SITE_NAME", default=None)
    or base.MIGRATION_SITE_NAME
)

# Random password are generated with this length.
DEFAULT_PASSWORD_LENGTH = env.int('DEFAULT_PASSWORD_LENGTH',default=base.DEFAULT_PASSWORD_LENGTH)

# Default value for is_site setting.
ASSOCIATION_IS_SITE_DEFAULT = env.bool("ASSOCIATION_IS_SITE_DEFAULT",default=base.ASSOCIATION_IS_SITE_DEFAULT)

# Default amount of users allowed in an association (None if no limit).
ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = env.int("ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED",default=base.ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED)

# Enable adding a LDAP account though Spore.
LDAP_ENABLED = env.bool('LDAP_ENABLED', default=False)

# External APIs.
if LDAP_ENABLED:
    if 'ACCOUNTS_API_SPORE_BASE_URL' in env:
        ACCOUNTS_API_CLIENT = "plana.libs.api.accounts.spore.SporeAccountsAPI"
        ACCOUNTS_API_CONF = {
            "DESCRIPTION_FILE": env.str("ACCOUNTS_API_SPORE_DESCRIPTION_FILE", default=REQUIRED),
            "BASE_URL": env.str("ACCOUNTS_API_SPORE_BASE_URL", default=REQUIRED),
            "TOKEN": env.str("ACCOUNTS_API_SPORE_TOKEN", default=REQUIRED),
        }
    else:
        ACCOUNTS_API_CLIENT = "plana.libs.api.accounts.ldap.LdapAccountsAPI"
        ACCOUNTS_API_CONF = {
            "HOST": env.str('ACCOUNTS_API_CONF_HOST', default=REQUIRED),
            "PORT": env.int('ACCOUNTS_API_CONF_PORT', default=None),
            "USE_TLS": env.bool('ACCOUNTS_API_CONF_USE_SSL', default=False),
            "BIND_DN": env.str('ACCOUNTS_API_CONF_BIND_DN', default=None),
            "PASSWORD": env.str('ACCOUNTS_API_CONF_PASSWORD', default=None),
            "BASE_DN": env.str('ACCOUNTS_API_CONF_BASE_DN', default=REQUIRED),
            "FILTER": env.bool('ACCOUNTS_API_CONF_FILTER', default=REQUIRED),
            "ATTRIBUTES": env.list('ACCOUNTS_API_CONF_ATTRIBUTES', default=[]),
        }
else:
    ACCOUNTS_API_CLIENT = "plana.libs.api.accounts.base.BaseAccountsAPI"
    ACCOUNTS_API_CONF = { }


# MIME types allowed for image uploads.
ALLOWED_IMAGE_MIME_TYPES = env.list("ALLOWED_IMAGE_MIME_TYPES",default=base.ALLOWED_IMAGE_MIME_TYPES)

# Special permissions for user_groups links.
GROUPS_STRUCTURE = base.GROUPS_STRUCTURE


########################
# Groups & Permissions #
########################
from .base import PERMISSIONS_GROUPS

