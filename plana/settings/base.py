from os import environ
from os.path import abspath, basename, dirname, join, normpath

from .permissions import *

######################
# Path configuration #
######################

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
SITE_ROOT = dirname(DJANGO_ROOT)
SITE_NAME = basename(DJANGO_ROOT)


#######################
# Debug configuration #
#######################

DEBUG = False
TEMPLATE_DEBUG = DEBUG


##########################
# Manager configurations #
##########################

ADMINS = [
    # ('Your Name', 'your_email@example.com'),
]

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = "plan-a.noreply@unistra.fr"


##########################
# Database configuration #
##########################

# In your virtualenv, edit the file $VIRTUAL_ENV/bin/postactivate and set
# properly the environnement variable defined in this file (ie: os.environ[KEY])
# ex: export DEFAULT_DB_USER='plana'

# Default values for default database are :
# engine : sqlite3
# name : PROJECT_ROOT_DIR/plana.db

# defaut db connection
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "plana",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "5432",
    }
}


######################
# Site configuration #
######################

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []


#########################
# General configuration #
#########################

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "Europe/Paris"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "fr-FR"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


########################
# Locale configuration #
########################

LOCALE_PATHS = [
    normpath(join(DJANGO_ROOT, "locale")),
]


#######################
# Media configuration #
#######################

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = normpath(join(DJANGO_ROOT, "media"))

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
STATIC_ROOT = normpath(join(SITE_ROOT, "assets"))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/site_media/"

# Additional locations of static files
STATICFILES_DIRS = [
    normpath(join(DJANGO_ROOT, "static")),
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

DIPSTRAP_STATIC_URL = "//django-static.u-strasbg.fr/dipstrap/"


##############
# Secret key #
##############

# Make this unique, and don't share it with anybody.
# Only for dev and test environnement. Should be redefined for production
# environnement
SECRET_KEY = "ma8r116)33!-#pty4!sht8tsa(1bfe%(+!&9xfack+2e9alah!"


##########################
# Template configuration #
##########################

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            normpath(join(DJANGO_ROOT, "templates")),
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
CORS_REPLACE_HTTPS_REFERER = True


############################
# Middleware configuration #
############################

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


#####################
# Url configuration #
#####################

ROOT_URLCONF = "%s.urls" % SITE_NAME


######################
# WSGI configuration #
######################

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "%s.wsgi.application" % SITE_NAME


#############################
# Application configuration #
#############################

DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Uncomment the next line to enable the admin:
    "django.contrib.admin",
    # 'django.contrib.admindocs',
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "django_extensions",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth_cas",
    "rest_framework_simplejwt",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "drf_spectacular",
    "djangorestframework_camel_case",
    "django_summernote",
    "storages",
    "thumbnails",
    "django_cleanup",
]

LOCAL_APPS = [
    "plana",
    "plana.apps.associations",
    "plana.apps.commissions",
    "plana.apps.consents",
    "plana.apps.documents",
    "plana.apps.groups",
    "plana.apps.institutions",
    "plana.apps.projects",
    "plana.apps.users",
    "plana.libs.mail_template",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


#########################
# Session configuration #
#########################

SESSION_SERIALIZER = "django.contrib.sessions.serializers.JSONSerializer"


#####################
# Log configuration #
#####################

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s %(asctime)s %(name)s:%(lineno)s %(message)s"
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "",
            "maxBytes": 209715200,
            "backupCount": 3,
            "formatter": "default",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
        "plana": {
            "handlers": ["mail_admins", "file"],
            "level": "ERROR",
            "propagate": True,
        },
        'external_accounts': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


#########################
# DJANGO REST FRAMEWORK #
#########################

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ],
    "JSON_UNDERSCOREIZE": {
        "no_underscore_before_number": True,
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


#####################
# DJANGO THUMBNAILS #
#####################

THUMBNAILS = {
    "METADATA": {
        "BACKEND": "thumbnails.backends.metadata.DatabaseBackend",
    },
    "STORAGE": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "SIZES": {
        "list": {
            "PROCESSORS": [
                {
                    "PATH": "thumbnails.processors.resize",
                    "width": 100,
                    "height": 100,
                    "method": "fit",
                },
            ]
        },
        "detail": {
            "PROCESSORS": [
                {
                    "PATH": "thumbnails.processors.resize",
                    "width": 150,
                    "height": 150,
                    "method": "fit",
                },
            ]
        },
        "base": {
            "PROCESSORS": [
                {
                    "PATH": "thumbnails.processors.resize",
                    "width": 250,
                    "height": 250,
                    "method": "fit",
                },
                {"PATH": "thumbnails.processors.crop", "width": 250, "height": 250},
            ]
        },
    },
}


#####################
# S3 storage config #
#####################

DEFAULT_FILE_STORAGE = 'plana.storages.MediaStorage'
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_ENDPOINT_URL = environ.get('AWS_S3_ENDPOINT_URL', '')
S3_LOGO_FILEPATH = 'associations_logos'
S3_TEMPLATES_FILEPATH = 'associations_documents_templates'
S3_DOCUMENTS_FILEPATH = 'associations_documents'


##################
# AUTHENTICATION #
##################

CAS_ID = "cas"
CAS_NAME = "CAS Unistra"
CAS_SERVER = "https://cas.unistra.fr/cas/"
CAS_VERSION = 3

CAS_AUTHORIZED_SERVICES = [
    "http://localhost:8000/users/auth/cas_verify/",
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_ADAPTER = "plana.apps.users.adapter.PlanAAdapter"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_USERNAME_BLACKLIST = ["admin", "unistra", "plana", "plan-a", "plan_a"]

SOCIALACCOUNT_ADAPTER = "plana.apps.users.adapter.SocialAccountAdapter"
SOCIALACCOUNT_EMAIL_VERIFICATION = False
SOCIALACCOUNT_EMAIL_REQUIRED = True

SOCIALACCOUNT_PROVIDERS = {
    "cas": {
        "VERIFIED_EMAIL": True,
    }
}

# Using SimpleJWT with dj-rest-auth
REST_USE_JWT = True
JWT_AUTH_COOKIE = "plana-auth"
JWT_AUTH_REFRESH_COOKIE = "plana-refresh-auth"

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "plana.apps.users.serializers.user.UserSerializer",
    "PASSWORD_RESET_SERIALIZER": "plana.apps.users.serializers.user.PasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "plana.apps.users.serializers.user.PasswordResetConfirmSerializer",
    "PASSWORD_CHANGE_SERIALIZER": "plana.apps.users.serializers.user.PasswordChangeSerializer",
}

REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "plana.apps.users.serializers.user.CustomRegisterSerializer",
}


##########
# Sentry #
##########

STAGE = None


def sentry_init(environment):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn="https://72691d0aec61475a80d93ac9b634ca57@sentry.app.unistra.fr/54",
        integrations=[
            DjangoIntegration(),
        ],
        environment=environment,
        release=open(join(SITE_ROOT, "build.txt")).read(),
        send_default_pii=True,
    )


###############
# Spectacular #
###############

SPECTACULAR_SETTINGS = {
    "TITLE": "PlanA API",
    "DESCRIPTION": "API for PlanA",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "POST_PROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "COMPONENT_SPLIT_REQUEST": True,
}


########
# Misc #
########

# Defining default format for database identifiers.
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Extending the abstract User class.
AUTH_USER_MODEL = "users.User"

# Avoid errors while testing the API with cURL.
APPEND_SLASH = False

# Documentation URL sent in emails.
APP_DOCUMENTATION_URL = "https://ernest.unistra.fr/"

# Default value for is_site setting.
ASSOCIATION_IS_SITE_DEFAULT = False

# Default amount of users allowed in an association (None if no limit).
ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = 4

# Avoid registration with following email domains.
RESTRICTED_DOMAINS = ["unistra.fr", "etu.unistra.fr"]

# External APIs
ACCOUNTS_API_CLIENT = 'plana.libs.api.accounts.SporeAccountsAPI'
ACCOUNTS_API_CONF = {}

# Special permissions for user_groups links.
GROUPS_STRUCTURE = {
    "MANAGER_GENERAL": {
        "REGISTRATION_ALLOWED": False,
        "INSTITUTION_ID_POSSIBLE": True,
        "COMMISSION_ID_POSSIBLE": False,
    },
    "MANAGER_INSTITUTION": {
        "REGISTRATION_ALLOWED": False,
        "INSTITUTION_ID_POSSIBLE": True,
        "COMMISSION_ID_POSSIBLE": False,
    },
    "MANAGER_MISC": {
        "REGISTRATION_ALLOWED": False,
        "INSTITUTION_ID_POSSIBLE": True,
        "COMMISSION_ID_POSSIBLE": False,
    },
    "COMMISSION": {
        "REGISTRATION_ALLOWED": True,
        "INSTITUTION_ID_POSSIBLE": False,
        "COMMISSION_ID_POSSIBLE": True,
    },
    "STUDENT_INSTITUTION": {
        "REGISTRATION_ALLOWED": True,
        "INSTITUTION_ID_POSSIBLE": False,
        "COMMISSION_ID_POSSIBLE": False,
    },
    "STUDENT_MISC": {
        "REGISTRATION_ALLOWED": True,
        "INSTITUTION_ID_POSSIBLE": False,
        "COMMISSION_ID_POSSIBLE": False,
    },
}
