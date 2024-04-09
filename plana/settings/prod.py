"""Configuration for production server environment."""

from .base import *

##########################
# Database configuration #
##########################

DATABASES["default"]["HOST"] = "{{ default_db_host }}"
DATABASES["default"]["USER"] = "{{ default_db_user }}"
DATABASES["default"]["PASSWORD"] = "{{ default_db_password }}"
DATABASES["default"]["NAME"] = "{{ default_db_name }}"


############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = ["*"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "ssl")


#####################
# Log configuration #
#####################

LOGGING["handlers"]["file"]["filename"] = "{{ remote_current_path }}/log/app.log"


###############
# Secret keys #
###############

SECRET_KEY = "{{ secret_key }}"


############
# Dipstrap #
############

DIPSTRAP_VERSION = "{{ dipstrap_version }}"
DIPSTRAP_STATIC_URL += f"{DIPSTRAP_VERSION}/"

##########
# Sentry #
##########

STAGE = "{{ goal }}"
sentry_init(STAGE)


##################
# AUTHENTICATION #
##################

CAS_SERVER = "https://cas.unistra.fr/cas/"
CAS_AUTHORIZED_SERVICES = [
    "https://etu-campulse.fr/cas-login",
    "https://etu-campulse.fr/cas-register",
]


##########
# Emails #
##########

# EMAIL_HOST = "{{ email_host }}"
# EMAIL_PORT = "{{ email_port }}"
# EMAIL_HOST_USER = "{{ email_host_user }}"
# EMAIL_HOST_PASSWORD = "{{ email_host_password }}"
# EMAIL_USE_TLS = "{{ email_use_tls }}".lower() == "true"

EMAIL_TEMPLATE_FRONTEND_URL = "https://etu-campulse.fr/"


#####################
# S3 storage config #
#####################

AWS_ACCESS_KEY_ID = "{{ s3_access_key }}"
AWS_SECRET_ACCESS_KEY = "{{ s3_secret_key }}"
AWS_STORAGE_BUCKET_NAME = "{{ s3_bucket }}"
AWS_S3_ENDPOINT_URL = "{{ s3_endpoint }}"


########
# Misc #
########

MIGRATION_SITE_DOMAIN = "etu-campulse.fr"
DEFAULT_FROM_EMAIL = "no-reply@unistra.fr"

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = "{{ accounts_api_spore_description_file }}"
ACCOUNTS_API_CONF["BASE_URL"] = "{{ accounts_api_spore_base_url }}"
ACCOUNTS_API_CONF["TOKEN"] = "{{ accounts_api_spore_token }}"
