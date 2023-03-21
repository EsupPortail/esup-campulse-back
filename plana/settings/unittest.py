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
