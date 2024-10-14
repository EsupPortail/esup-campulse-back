"""Configuration for test server environment."""

from .base import *

#######################
# Debug configuration #
#######################

DEBUG = True


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

ALLOWED_HOSTS = [
    ".u-strasbg.fr",
    ".unistra.fr",
]

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "ssl")

CSRF_TRUSTED_ORIGINS = ["https://plana-api-test.app.unistra.fr"]


#####################
# Log configuration #
#####################

LOGGING["handlers"]["file"]["filename"] = "{{ remote_current_path }}/log/app.log"

for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["level"] = "DEBUG"


###############
# Secret keys #
###############

SECRET_KEY = ""


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

CAS_NAME = "{{ cas_name }}"  # "CAS Unistra"
CAS_SERVER = "{{ cas_server }}"  # "https://cas-dev.unistra.fr/cas/"
CAS_VERSION = "{{ cas_version }}"  # 3
CAS_AUTHORIZED_SERVICES = "{{ cas_authorized_services }}".split()
# ["https://plana-test.app.unistra.fr/cas-login", "https://plana-test.app.unistra.fr/cas-register"]

CAS_ATTRIBUTES_NAMES["email"] = "{{ cas_attribute_email }}"  # mail
CAS_ATTRIBUTES_NAMES["first_name"] = "{{ cas_attribute_first_name }}"  # first_name
CAS_ATTRIBUTES_NAMES["last_name"] = "{{ cas_attribute_last_name }}"  # last_name
CAS_ATTRIBUTES_NAMES["is_student"] = "{{ cas_attribute_is_student }}"  # affiliation
CAS_ATTRIBUTES_VALUES["is_student"] = "{{ cas_value_is_student }}"  # student

##########
# Emails #
##########

EMAIL_HOST = "{{ email_host }}"  # '127.0.0.1'
EMAIL_PORT = "{{ email_port }}"  # 25
EMAIL_HOST_USER = "{{ email_host_user }}"  # ''
EMAIL_HOST_PASSWORD = "{{ email_host_password }}"  # ''
EMAIL_USE_TLS = "{{ email_use_tls }}".lower() == "true"  # "False"

EMAIL_TEMPLATE_FRONTEND_URL = "{{ email_template_frontend_url }}"  # "https://plana-test.app.unistra.fr/"


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

MIGRATION_SITE_DOMAIN = "{{ migration_site_domain }}"  # "plana-test.app.unistra.fr"
MIGRATION_SITE_NAME = "{{ migration_site_name }}"  # "Campulse"
DEFAULT_FROM_EMAIL = "{{ default_from_email }}"  # "appli-plana-test@unistra.fr"

ASSOCIATION_IS_SITE_DEFAULT = "{{ association_is_site_default }}".lower() == "true"  # "False"

ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = "{{ association_default_amount_members_allowed }}"  # 4

LDAP_ENABLED = "{{ ldap_enabled }}".lower() == "true"  # True

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = "{{ accounts_api_spore_description_file }}"
ACCOUNTS_API_CONF["BASE_URL"] = "{{ accounts_api_spore_base_url }}"
ACCOUNTS_API_CONF["TOKEN"] = "{{ accounts_api_spore_token }}"
