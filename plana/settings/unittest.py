"""Configuration for unit tests environment."""

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

LOGGING["handlers"]["file"]["filename"] = environ.get("LOG_DIR", normpath(join("/tmp", f"test_{SITE_NAME}.log")))
LOGGING["handlers"]["file"]["level"] = "DEBUG"

for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["level"] = "DEBUG"

TEST_RUNNER = "django.test.runner.DiscoverRunner"


##########
# Emails #
##########

EMAIL_TEMPLATE_FRONTEND_URL = "http://localhost:3000/"

USE_S3 = False
# DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
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

SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
}

REST_AUTH["JWT_AUTH_COOKIE"] = "plana-auth"
REST_AUTH["JWT_AUTH_REFRESH_COOKIE"] = "plana-refresh-auth"


#####################
# S3 storage config #
#####################

AWS_ACCESS_KEY_ID = "FAKE"
AWS_SECRET_ACCESS_KEY = "FAKE"
AWS_STORAGE_BUCKET_NAME = "FAKE"
AWS_S3_ENDPOINT_URL = "FAKE"

S3_PDF_FILEPATH = "."
TEMPLATES_PDF_EXPORTS_FOLDER = "pdf/exports"
TEMPLATES_PDF_NOTIFICATIONS_FOLDER = "pdf/notifications"
TEMPLATES_PDF_FILEPATHS = {
    "association_charter_summary": f"{TEMPLATES_PDF_EXPORTS_FOLDER}/association_charter_summary.html",
    "commission_projects_list": f"{TEMPLATES_PDF_EXPORTS_FOLDER}/commission_projects_list.html",
    "project_summary": f"{TEMPLATES_PDF_EXPORTS_FOLDER}/project_summary.html",
    "project_review_summary": f"{TEMPLATES_PDF_EXPORTS_FOLDER}/project_review_summary.html",
}
