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

# CSRF_TRUSTED_ORIGINS = "{{ csrf_trusted_origins }}".split()


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
# Authentication #
##################

CAS_NAME = "{{ cas_name }}"
CAS_SERVER = "{{ cas_server }}"  # "https://cas.unistra.fr/cas/"
CAS_VERSION = "{{ cas_version }}"
CAS_AUTHORIZED_SERVICES = "{{ cas_authorized_services }}".split()
# ["https://etu-campulse.fr/cas-login", "https://etu-campulse.fr/cas-register"]

CAS_ATTRIBUTES_NAMES["email"] = "{{ cas_attribute_email }}"
CAS_ATTRIBUTES_NAMES["first_name"] = "{{ cas_attribute_first_name }}"
CAS_ATTRIBUTES_NAMES["last_name"] = "{{ cas_attribute_last_name }}"
CAS_ATTRIBUTES_NAMES["is_student"] = "{{ cas_attribute_is_student }}"
CAS_ATTRIBUTES_VALUES["is_student"] = "{{ cas_value_is_student }}"


##########
# Emails #
##########

EMAIL_HOST = "{{ email_host }}"
EMAIL_PORT = "{{ email_port }}"
EMAIL_HOST_USER = "{{ email_host_user }}"
EMAIL_HOST_PASSWORD = "{{ email_host_password }}"
EMAIL_USE_TLS = "{{ email_use_tls }}".lower() == "true"

EMAIL_TEMPLATE_FRONTEND_URL = "{{ email_template_frontend_url }}"  # "https://etu-campulse.fr/"


#####################
# S3 storage config #
#####################

AWS_ACCESS_KEY_ID = "{{ s3_access_key }}"
AWS_SECRET_ACCESS_KEY = "{{ s3_secret_key }}"
AWS_STORAGE_PUBLIC_BUCKET_NAME = "{{ s3_bucket }}"
AWS_STORAGE_PRIVATE_BUCKET_NAME = "{{ s3_bucket_private }}"
AWS_S3_ENDPOINT_URL = "{{ s3_endpoint }}"


########
# Misc #
########

MIGRATION_SITE_DOMAIN = "{{ migration_site_domain }}"  # "etu-campulse.fr"
MIGRATION_SITE_NAME = "{{ migration_site_name }}"
DEFAULT_FROM_EMAIL = "{{ default_from_email }}"  # "no-reply@unistra.fr"

ASSOCIATION_IS_SITE_DEFAULT = "{{ association_is_site_default }}".lower() == "true"

ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = "{{ association_default_amount_members_allowed }}"

LDAP_ENABLED = "{{ ldap_enabled }}".lower() == "true"

ADMIN_TEST_FEATURES = False

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = "{{ accounts_api_spore_description_file }}"
ACCOUNTS_API_CONF["BASE_URL"] = "{{ accounts_api_spore_base_url }}"
ACCOUNTS_API_CONF["TOKEN"] = "{{ accounts_api_spore_token }}"
