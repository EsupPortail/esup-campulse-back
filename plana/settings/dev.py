"""Configuration for local dev environment."""

from os import environ
from os.path import normpath

from .base import *

#######################
# Debug configuration #
#######################

DEBUG = True


##########################
# Database configuration #
##########################

# In your virtualenv, edit the file $VIRTUAL_ENV/bin/postactivate and set
# properly the environnement variable defined in this file (ie: os.environ[KEY])
# ex: export DEFAULT_DB_NAME='project_name'

# Default values for default database are :
# engine : sqlite3
# name : PROJECT_ROOT_DIR/default.db


DATABASES = {
    "default": {
        "ENGINE": environ.get("DEFAULT_DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": environ.get("DEFAULT_DB_NAME", "plana"),
        "USER": environ.get("DEFAULT_DB_USER", "plana"),
        "PASSWORD": environ.get("DEFAULT_DB_PASSWORD", "plana"),
        "HOST": environ.get("DEFAULT_DB_HOST", "localhost"),
        "PORT": environ.get("DEFAULT_DB_PORT", "5432"),
    }
}


############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = ["*"]


#####################
# Log configuration #
#####################

LOGGING["handlers"]["file"]["filename"] = environ.get("LOG_DIR", normpath(join("/tmp", f"{SITE_NAME}.log")))
LOGGING["handlers"]["file"]["level"] = "DEBUG"

for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["level"] = "DEBUG"


###########################
# Unit test configuration #
###########################

INSTALLED_APPS += [
    "coverage",
    "debug_toolbar",
]


############
# Dipstrap #
############

DIPSTRAP_VERSION = environ.get("DIPSTRAP_VERSION", "latest")
DIPSTRAP_STATIC_URL += f"{DIPSTRAP_VERSION}/"


#################
# Debug toolbar #
#################

DEBUG_TOOLBAR_PATCH_SETTINGS = False
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"]


##########
# Emails #
##########

EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False

EMAIL_TEMPLATE_FRONTEND_URL = "http://localhost:3000/"


#########################
# DJANGO REST FRAMEWORK #
#########################

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
    "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
]


##################
# AUTHENTICATION #
##################

CAS_SERVER = "https://cas-dev.unistra.fr/cas/"
CAS_AUTHORIZED_SERVICES = [
    "http://localhost:8000/users/auth/cas_verify/",
    "http://localhost:3000/cas-login",
    "http://localhost:3000/cas-register",
]


########
# Misc #
########

MIGRATION_SITE_NAME = "Opaline"

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = environ.get('ACCOUNTS_API_SPORE_DESCRIPTION_FILE')
ACCOUNTS_API_CONF["BASE_URL"] = environ.get('ACCOUNTS_API_SPORE_BASE_URL')
ACCOUNTS_API_CONF["TOKEN"] = environ.get('ACCOUNTS_API_SPORE_TOKEN')
