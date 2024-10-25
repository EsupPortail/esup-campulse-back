"""Configuration for new Docker server environment."""

from .base import *

##########################
# Database configuration #
##########################

DATABASES["default"]["HOST"] = environ.get("DEFAULT_DB_HOST", "localhost")
DATABASES["default"]["USER"] = environ.get("DEFAULT_DB_USER", "plana")
DATABASES["default"]["PASSWORD"] = environ.get("DEFAULT_DB_PASSWORD", "plana")
DATABASES["default"]["NAME"] = environ.get("DEFAULT_DB_NAME", "plana")


############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = ["*"]

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "ssl")

CSRF_TRUSTED_ORIGINS = environ.get("CSRF_TRUSTED_ORIGINS", "https://back-url.tld").split()


#####################
# Log configuration #
#####################

LOGGING["handlers"]["file"]["filename"] = environ.get("LOG_PATH", "/tmp/log")


###############
# Secret keys #
###############

SECRET_KEY = environ.get("SECRET_KEY", "")


############
# Dipstrap #
############

DIPSTRAP_VERSION = environ.get("DIPSTRAP_VERSION", "latest")
DIPSTRAP_STATIC_URL += f"{DIPSTRAP_VERSION}/"


##########
# Sentry #
##########

# STAGE = "docker"
# sentry_init(STAGE)


##################
# Authentication #
##################

CAS_NAME = environ.get("CAS_NAME", "CAS")
CAS_SERVER = environ.get("CAS_SERVER", "https://cas.domain.tld/")
CAS_VERSION = environ.get("CAS_VERSION", "3")
CAS_AUTHORIZED_SERVICES = environ.get("CAS_AUTHORIZED_SERVICES", "https://front-url.tld/cas-login https://front-url.tld/cas-register").split()

CAS_ATTRIBUTE_EMAIL = environ.get("CAS_ATTRIBUTE_EMAIL", "mail")
CAS_ATTRIBUTE_FIRST_NAME = environ.get("CAS_ATTRIBUTE_FIRST_NAME", "first_name")
CAS_ATTRIBUTE_LAST_NAME = environ.get("CAS_ATTRIBUTE_LAST_NAME", "last_name")
CAS_ATTRIBUTE_IS_STUDENT = environ.get("CAS_ATTRIBUTE_IS_STUDENT", "affliliation")
CAS_VALUE_IS_STUDENT = environ.get("CAS_VALUE_IS_STUDENT", "student")


##########
# Emails #
##########

EMAIL_HOST = environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = environ.get("EMAIL_PORT", "25")
EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = environ.get("EMAIL_USE_TLS", "False").lower() == "true"

EMAIL_TEMPLATE_FRONTEND_URL = environ.get("EMAIL_TEMPLATE_FRONTEND_URL", "https://front-url.tld/")


#####################
# S3 storage config #
#####################

AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = environ.get("AWS_STORAGE_BUCKET_NAME", "back-url.tld")
AWS_S3_ENDPOINT_URL = environ.get("AWS_S3_ENDPOINT_URL", "https://domain.tld")
AWS_USE_OBJECT_ACL = False


########
# Misc #
########

MIGRATION_SITE_DOMAIN = environ.get("MIGRATION_SITE_DOMAIN", "front-url.tld")
MIGRATION_SITE_NAME = environ.get("MIGRATION_SITE_NAME", "PlanA")
DEFAULT_FROM_EMAIL = environ.get("DEFAULT_FROM_EMAIL", "no-reply@domain.tld")

ASSOCIATION_IS_SITE_DEFAULT = environ.get("ASSOCIATION_IS_SITE_DEFAULT", "True").lower() == "true"

ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = environ.get("ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED", "4")

LDAP_ENABLED = environ.get("LDAP_ENABLED", "False").lower() == "true"

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = environ.get("ACCOUNTS_API_SPORE_DESCRIPTION_FILE", "https://domain.tld")
ACCOUNTS_API_CONF["BASE_URL"] = environ.get("ACCOUNTS_API_SPORE_BASE_URL", "https://domain.tld/description.json")
ACCOUNTS_API_CONF["TOKEN"] = environ.get("ACCOUNTS_API_SPORE_TOKEN", "70K3N")
