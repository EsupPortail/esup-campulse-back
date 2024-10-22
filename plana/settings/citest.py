"""Configuration for unit tests environment."""

from os import environ
from django.core.management.utils import get_random_secret_key
from pyrage import x25519

environ['DEBUG'] = "True"

environ['SECRET_KEY'] = get_random_secret_key()

age = x25519.Identity.generate()
environ['AGE_PRIVATE_KEY'] = str(age)
environ['AGE_PUBLIC_KEY'] = str(age.to_public())

environ['SIMPLE_JWT'] = f"ALGORITHM=HS256,SIGNING_KEY={environ['SECRET_KEY']},VERIFYING_KEY="

environ['USE_S3'] = "False"
environ['AWS_ACCESS_KEY_ID'] = "FAKE"
environ['AWS_SECRET_ACCESS_KEY'] = "FAKE"
environ['AWS_STORAGE_BUCKET_NAME'] = "FAKE"
environ['AWS_S3_ENDPOINT_URL'] = "FAKE"

from .oci import *

TEST_RUNNER = 'xmlrunner.extra.djangotestrunner.XMLTestRunner'
TEST_OUTPUT_DIR = 'test-results'
TEST_OUTPUT_VERBOSE = 2
TEST_OUTPUT_DESCRIPTIONS = True

API_PREFIX = ''

STORAGES["default"]["BACKEND"] = "django.core.files.storage.FileSystemStorage"

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
]
REST_AUTH["JWT_AUTH_COOKIE"] = "plana-auth"
REST_AUTH["JWT_AUTH_REFRESH_COOKIE"] = "plana-refresh-auth"

TEMPLATES_PDF_EXPORTS_FOLDER = "pdf/exports"
TEMPLATES_PDF_NOTIFICATIONS_FOLDER = "pdf/notifications"

AWS_USE_OBJECT_ACL = True
