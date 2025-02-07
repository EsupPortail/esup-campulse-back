"""Base configuration for all environments."""

from datetime import timedelta
from os import environ
from os.path import join, normpath
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


def load_key(keyfile):
    """Load JWT and AGE keys."""
    try:
        keyfile = SITE_ROOT / "keys" / keyfile
        with open(keyfile, "rb") as file:
            return file.read()
    except FileNotFoundError:
        return b""


APP_VERSION = "1.2.4"

######################
# Path configuration #
######################

DJANGO_ROOT = Path(__file__).resolve(strict=True).parent.parent
SITE_ROOT = DJANGO_ROOT.parent
SITE_NAME = DJANGO_ROOT.name


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
# https://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "Europe/Paris"

# Language code for this installation. All choices can be found here:
# https://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "fr-FR"

SITE_ID = 1

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


############################
# Middleware configuration #
############################

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware"
]


#####################
# Url configuration #
#####################

ROOT_URLCONF = f"{SITE_NAME}.urls"


######################
# WSGI configuration #
######################

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = f"{SITE_NAME}.wsgi.application"


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
    'django_filters',
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "drf_spectacular",
    "djangorestframework_camel_case",
    "django_summernote",
    "storages",
    "thumbnails",
    "django_cleanup",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    'health_check.contrib.migrations',
    "health_check.contrib.s3boto3_storage",
]

LOCAL_APPS = [
    "plana",
    "plana.apps.associations",
    "plana.apps.commissions",
    "plana.apps.consents",
    "plana.apps.documents",
    "plana.apps.groups",
    "plana.apps.history",
    "plana.apps.institutions",
    "plana.apps.projects",
    "plana.apps.users",
    "plana.apps.contents",
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
        "default": {"format": "%(levelname)s %(asctime)s %(name)s:%(lineno)s %(message)s"},
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
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
    ],
    "DEFAULT_FILTER_BACKENDS": (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
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


##################
# Storage config #
##################

# DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
# DEFAULT_FILE_STORAGE = "plana.storages.MediaStorage"
STORAGES = {
    "default": {
        "BACKEND": "plana.storages.MediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
USE_S3 = True  # TODO FileSystemStorage implementation not finished (encryption not available, migrations errors).
AWS_S3_FILE_OVERWRITE = True
AWS_DEFAULT_ACL = None
AWS_USE_OBJECT_ACL = True
AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = environ.get("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_ENDPOINT_URL = environ.get("AWS_S3_ENDPOINT_URL", "")
S3_LOGOS_FILEPATH = "logos"
S3_ASSOCIATIONS_LOGOS_FILEPATH = "associations_logos"
S3_TEMPLATES_FILEPATH = "associations_documents_templates"
S3_DOCUMENTS_FILEPATH = "associations_documents"
AGE_PUBLIC_KEY = load_key("age-public-key.key")
AGE_PRIVATE_KEY = load_key("age-private-key.key")


#####################
# DJANGO THUMBNAILS #
#####################

THUMBNAILS = {
    "METADATA": {
        "BACKEND": "thumbnails.backends.metadata.DatabaseBackend",
    },
    "STORAGE": {
        "BACKEND": STORAGES["default"]["BACKEND"],
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

##################
# AUTHENTICATION #
##################

CAS_ID = "cas"
CAS_NAME = "CAS Unistra"
CAS_SERVER = "https://cas.unistra.fr/cas/"
CAS_VERSION = 3
CAS_AUTHORIZED_SERVICES = ["http://localhost:8000/users/auth/cas_verify/"]

# Keys are User model fields, values are CAS fields.
CAS_ATTRIBUTES_NAMES = {
    "email": "mail",
    "first_name": "first_name",
    "last_name": "last_name",
    "is_student": "affiliation",
}
# Keys are User model fields, values are CAS values waited for those model fields.
CAS_ATTRIBUTES_VALUES = {
    "is_student": "student",
}

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
ACCOUNT_USERNAME_BLACKLIST = [
    "admin",
    "unistra",
    "plana",
    "plan-a",
    "plan_a",
    "campulse",
    "etu-campulse",
    "campulse-etu",
]

SOCIALACCOUNT_ADAPTER = "plana.apps.users.adapter.SocialAccountAdapter"
SOCIALACCOUNT_EMAIL_VERIFICATION = False
SOCIALACCOUNT_EMAIL_REQUIRED = True

SOCIALACCOUNT_PROVIDERS = {
    "cas": {
        "VERIFIED_EMAIL": True,
    }
}

# Using SimpleJWT with dj-rest-auth
SIMPLE_JWT = {
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=1),
    "ALGORITHM": "RS256",
    "SIGNING_KEY": load_key("jwt-private-key.pem"),
    "VERIFYING_KEY": load_key("jwt-public-key.pem"),
    "AUDIENCE": "plan_a",
    "ISSUER": "plan_a",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

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


def sentry_init(environment):
    """Init Sentry service."""
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        environment=environment,
        release=open(join(SITE_ROOT, "build.txt"), encoding="utf-8").read(),
        send_default_pii=True,
        traces_sample_rate=1.0,
    )


###############
# Spectacular #
###############

SPECTACULAR_SETTINGS = {
    "TITLE": "PlanA API",
    "DESCRIPTION": "API for PlanA",
    "VERSION": APP_VERSION,
    "SERVE_INCLUDE_SCHEMA": False,
    "POST_PROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
        "drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields",
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "jwtAuth": {
                "type": "http",
                "scheme": "bearer",
            }
        }
    },
}


################################
# URL parts in email templates #
################################

EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_PATH = "register-verify-email/"
EMAIL_TEMPLATE_PASSWORD_RESET_PATH = "password-reset-confirm/"
EMAIL_TEMPLATE_PASSWORD_CHANGE_PATH = "dashboard/password-change-url/"
EMAIL_TEMPLATE_ACCOUNT_VALIDATE_PATH = "dashboard/validate-users/"
EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH = "dashboard/validate-association-users/"
EMAIL_TEMPLATE_DOCUMENT_VALIDATE_PATH = "charter/manage/"


################
# PDF Templates #
#################

# S3 configuration for PDF templates (used to store PDF exports and notifications).
S3_PDF_FILEPATH = "pdf"  # "." if local
TEMPLATES_PDF_EXPORTS_FOLDER = "templates/exports"  # "pdf/exports" if local
TEMPLATES_PDF_NOTIFICATIONS_FOLDER = "templates/notifications"  # "pdf/notifications" if local

TEMPLATES_PDF_FILEPATHS = {
    "association_charter_summary": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/association_charter_summary.html",
    "commission_projects_list": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/commission_projects_list.html",
    "project_summary": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/project_summary.html",
    "project_review_summary": f"{S3_PDF_FILEPATH}/{TEMPLATES_PDF_EXPORTS_FOLDER}/project_review_summary.html",
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

# Site name as set in migration in contents module.
MIGRATION_SITE_DOMAIN = "localhost:3000"
MIGRATION_SITE_NAME = "Campulse"

# Random password are generated with this length.
DEFAULT_PASSWORD_LENGTH = 16

# Default value for is_site setting.
ASSOCIATION_IS_SITE_DEFAULT = False

# Default amount of users allowed in an association (None if no limit).
ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = 4

# External APIs.
ACCOUNTS_API_CLIENT = "plana.libs.api.accounts.SporeAccountsAPI"
ACCOUNTS_API_CONF = {}

# Enable adding a LDAP account though Spore.
LDAP_ENABLED = True

# MIME types allowed for image uploads.
ALLOWED_IMAGE_MIME_TYPES = ["image/jpeg", "image/png"]

# Special permissions for user_groups links.
GROUPS_STRUCTURE = {
    "MANAGER_GENERAL": {
        "REGISTRATION_ALLOWED": False,
        "INSTITUTION_ID_POSSIBLE": True,
        "FUND_ID_POSSIBLE": False,
        "ASSOCIATIONS_POSSIBLE": False,
    },
    "MANAGER_INSTITUTION": {
        "REGISTRATION_ALLOWED": False,
        "INSTITUTION_ID_POSSIBLE": True,
        "FUND_ID_POSSIBLE": False,
        "ASSOCIATIONS_POSSIBLE": False,
    },
    "MANAGER_MISC": {
        "REGISTRATION_ALLOWED": False,
        "INSTITUTION_ID_POSSIBLE": True,
        "FUND_ID_POSSIBLE": False,
        "ASSOCIATIONS_POSSIBLE": False,
    },
    "MEMBER_FUND": {
        "REGISTRATION_ALLOWED": True,
        "INSTITUTION_ID_POSSIBLE": False,
        "FUND_ID_POSSIBLE": True,
        "ASSOCIATIONS_POSSIBLE": False,
    },
    "STUDENT_INSTITUTION": {
        "REGISTRATION_ALLOWED": True,
        "INSTITUTION_ID_POSSIBLE": False,
        "FUND_ID_POSSIBLE": False,
        "ASSOCIATIONS_POSSIBLE": True,
    },
    "STUDENT_MISC": {
        "REGISTRATION_ALLOWED": True,
        "INSTITUTION_ID_POSSIBLE": False,
        "FUND_ID_POSSIBLE": False,
        "ASSOCIATIONS_POSSIBLE": False,
    },
}


########################
# Groups & Permissions #
########################

PERMISSIONS_GROUPS = {
    "MANAGER_GENERAL": [
        # associations
        "add_association",
        "add_association_any_institution",
        "add_association_all_fields",
        "change_association",
        "change_association_any_institution",
        "change_association_all_fields",
        "delete_association",
        "delete_association_any_institution",
        "view_association_all_fields",
        "view_association_not_enabled",
        "view_association_not_public",
        # commissions
        "add_commission",
        "change_commission",
        "delete_commission",
        "add_commissionfund",
        "delete_commissionfund",
        # contents
        "change_content",
        # documents
        "add_document",
        "add_document_any_fund",
        "add_document_any_institution",
        "change_document",
        "change_document_any_fund",
        "change_document_any_institution",
        "delete_document",
        "delete_document_any_fund",
        "delete_document_any_institution",
        "add_documentupload_all",
        "change_documentupload",
        "delete_documentupload",
        "delete_documentupload_all",
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "change_project",
        "change_project_as_validator",
        "view_project",
        "view_project_any_fund",
        "view_project_any_institution",
        "view_project_any_status",
        "view_projectcategory",
        "view_projectcategory_any_fund",
        "view_projectcategory_any_institution",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "view_projectcomment_any_fund",
        "view_projectcomment_any_institution",
        "view_projectcomment_not_visible",
        "change_projectcommissionfund",
        "change_projectcommissionfund_as_validator",
        "view_projectcommissionfund",
        "view_projectcommissionfund_any_fund",
        "view_projectcommissionfund_any_institution",
        # users
        "add_user",
        "add_user_misc",
        "change_user",
        "change_user_misc",
        "change_user_all_fields",
        "delete_user",
        "delete_user_misc",
        "view_user",
        "view_user_misc",
        "view_user_anyone",
        "change_associationuser",
        "change_associationuser_any_institution",
        "delete_associationuser",
        "delete_associationuser_any_institution",
        "view_associationuser",
        "view_associationuser_anyone",
        "add_groupinstitutionfunduser_any_group",
        "delete_groupinstitutionfunduser",
        "delete_groupinstitutionfunduser_any_group",
        "view_groupinstitutionfunduser",
        "view_groupinstitutionfunduser_any_group",
    ],
    "MANAGER_INSTITUTION": [
        # associations
        "add_association",
        "add_association_all_fields",
        "change_association",
        "change_association_all_fields",
        "delete_association",
        "view_association_all_fields",
        "view_association_not_enabled",
        "view_association_not_public",
        # commissions
        "change_commission",
        # documents
        "add_document",
        "change_document",
        "delete_document",
        "add_documentupload_all",
        "change_documentupload",
        "delete_documentupload",
        "delete_documentupload_all",
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "change_project",
        "change_project_as_validator",
        "view_project",
        "view_project_any_status",
        "view_projectcategory",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "view_projectcomment_not_visible",
        "change_projectcommissionfund",
        "change_projectcommissionfund_as_validator",
        "view_projectcommissionfund",
        "view_projectcommissionfund_any_fund",
        "view_projectcommissionfund_any_institution",
        # users
        "add_user",
        "change_user",
        "change_user_all_fields",
        "delete_user",
        "view_user",
        "view_user_anyone",
        "change_associationuser",
        "delete_associationuser",
        "view_associationuser",
        "view_associationuser_anyone",
        "delete_groupinstitutionfunduser",
        "view_groupinstitutionfunduser",
        "view_groupinstitutionfunduser_any_group",
    ],
    "MANAGER_MISC": [
        # associations
        "add_association",
        "change_association",
        "change_association_all_fields",
        "delete_association",
        "view_association_all_fields",
        "view_association_not_enabled",
        "view_association_not_public",
        # commissions
        "change_commission",
        # documents
        "add_document",
        "change_document",
        "delete_document",
        "add_documentupload_all",
        "change_documentupload",
        "delete_documentupload",
        "delete_documentupload_all",
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "change_project",
        "change_project_as_validator",
        "view_project",
        "view_project_any_status",
        "view_projectcategory",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "view_projectcomment_not_visible",
        "change_projectcommissionfund",
        "change_projectcommissionfund_as_validator",
        "view_projectcommissionfund",
        "view_projectcommissionfund_any_fund",
        "view_projectcommissionfund_any_institution",
        # users
        "add_user",
        "add_user_misc",
        "change_user",
        "change_user_misc",
        "change_user_all_fields",
        "delete_user",
        "delete_user_misc",
        "view_user",
        "view_user_misc",
        "view_user_anyone",
        "change_associationuser",
        "delete_associationuser",
        "view_associationuser",
        "view_associationuser_anyone",
        "delete_groupinstitutionfunduser",
        "view_groupinstitutionfunduser",
        "view_groupinstitutionfunduser_any_group",
    ],
    "MEMBER_FUND": [
        # associations
        "view_association_not_public",
        # documents
        "view_documentupload",
        "view_documentupload_all",
        # projects
        "view_project",
        "view_projectcategory",
        "add_projectcomment",
        "change_projectcomment",
        "delete_projectcomment",
        "view_projectcomment",
        "view_projectcomment_not_visible",
        "view_projectcommissionfund",
        "view_projectcommissionfund_any_fund",
        "view_projectcommissionfund_any_institution",
        # users
        "view_user",
        "view_user_misc",
        "view_user_anyone",
        "view_associationuser",
        "view_groupinstitutionfunduser",
    ],
    "STUDENT_INSTITUTION": [
        # associations
        "change_association",
        # documents
        "delete_documentupload",
        "view_documentupload",
        # projects
        "add_project",
        "add_project_association",
        "change_project",
        "change_project_as_bearer",
        "delete_project",
        "view_project",
        "add_projectcategory",
        "delete_projectcategory",
        "view_projectcategory",
        "view_projectcomment",
        "add_projectcommissionfund",
        "change_projectcommissionfund",
        "change_projectcommissionfund_as_bearer",
        "delete_projectcommissionfund",
        "view_projectcommissionfund",
        # users
        "view_user",
        "change_associationuser",
        "delete_associationuser",
        "view_associationuser",
        "view_groupinstitutionfunduser",
    ],
    "STUDENT_MISC": [
        # documents
        "delete_documentupload",
        "view_documentupload",
        # projects
        "add_project",
        "add_project_user",
        "change_project",
        "change_project_as_bearer",
        "delete_project",
        "view_project",
        "add_projectcategory",
        "delete_projectcategory",
        "view_projectcategory",
        "view_projectcomment",
        "add_projectcommissionfund",
        "change_projectcommissionfund",
        "change_projectcommissionfund_as_bearer",
        "delete_projectcommissionfund",
        "view_projectcommissionfund",
        # users
        "view_groupinstitutionfunduser",
    ],
}
