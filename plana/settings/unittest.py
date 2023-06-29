from os import environ
from os.path import normpath

from django.conf import settings

from .base import *

#######################
# Debug configuration #
#######################

DEBUG = True


##########################
# Database configuration #
##########################

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environ.get("DEFAULT_DB_TEST_NAME", "plana_test"),
        "USER": environ.get("DEFAULT_DB_TEST_USER", "plana"),
        "PASSWORD": environ.get("DEFAULT_DB_TEST_PASSWORD", "plana"),
        "HOST": environ.get("DEFAULT_DB_TEST_HOST", "postgres"),
        "PORT": environ.get("DEFAULT_DB_TEST_PORT", "5432"),
    }
}


############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = ["*"]


#####################
# Log configuration #
#####################

LOGGING["handlers"]["file"]["filename"] = environ.get(
    "LOG_DIR", normpath(join("/tmp", "test_%s.log" % SITE_NAME))
)
LOGGING["handlers"]["file"]["level"] = "DEBUG"

for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["level"] = "DEBUG"

TEST_RUNNER = "django.test.runner.DiscoverRunner"


##########
# Emails #
##########

EMAIL_TEMPLATE_FRONTEND_URL = "http://localhost:3000/"

USE_S3 = False
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
THUMBNAILS["METADATA"]["BACKEND"] = "thumbnails.backends.metadata.DatabaseBackend"
THUMBNAILS["STORAGE"]["BACKEND"] = "thumbnails.tests.storage.TemporaryStorage"


#########################
# DJANGO REST FRAMEWORK #
#########################

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
]


##################
# AUTHENTICATION #
##################

JWT_AUTH_COOKIE = "plana-auth"
JWT_AUTH_REFRESH_COOKIE = "plana-refresh-auth"

SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
}
