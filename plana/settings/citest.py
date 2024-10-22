"""Configuration for unit tests environment."""

from os import environ
from django.core.management.utils import get_random_secret_key
from pyrage import x25519

secret_key = get_random_secret_key()
age = x25519.Identity.generate()

environ.update({
    "DEBUG": "True",
    "API_PREFIX": "",
    "SECRET_KEY": secret_key,
    "AGE_PRIVATE_KEY": str(age),
    "AGE_PUBLIC_KEY": str(age.to_public()),
    "SIMPLE_JWT": f"ALGORITHM=HS256,SIGNING_KEY={secret_key},VERIFYING_KEY=",
    "USE_S3": "False",
})

from .oci import * #NOSONAR python:S2208 https://rules.sonarsource.com/python/RSPEC-2208/

TEST_RUNNER = "xmlrunner.extra.djangotestrunner.XMLTestRunner"
TEST_OUTPUT_DIR = "test-results"
TEST_OUTPUT_VERBOSE = 2
TEST_OUTPUT_DESCRIPTIONS = True

STORAGES["default"]["BACKEND"] = "django.core.files.storage.FileSystemStorage"
AWS_USE_OBJECT_ACL = True

REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = [
    "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
]
REST_AUTH.update({
    "JWT_AUTH_COOKIE": "plana-auth",
    "JWT_AUTH_REFRESH_COOKIE": "plana-refresh-auth",
})
