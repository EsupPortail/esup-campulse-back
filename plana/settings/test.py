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


#####################
# Log configuration #
#####################

LOGGING["handlers"]["file"]["filename"] = "{{ remote_current_path }}/log/app.log"

for logger in LOGGING["loggers"]:
    LOGGING["loggers"][logger]["level"] = "DEBUG"


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

CAS_ID = "{{ cas_id }}"  # cas
CAS_NAME = "{{ cas_name }}"  # CAS Unistra
CAS_SERVER = "{{ cas_server }}"  # "https://cas-dev.unistra.fr/cas/"
CAS_VERSION = "{{ cas_version }}"  # 3
CAS_INSTITUTION_ID = "{{ cas_institution_id }}"  # 2
CAS_AUTHORIZED_SERVICES = "{{ cas_authorized_services }}".split()
# ["https://plana-test.app.unistra.fr/cas-login", "https://plana-test.app.unistra.fr/cas-register"]


##########
# Emails #
##########

EMAIL_HOST = "{{ email_host }}"  # '127.0.0.1'
EMAIL_PORT = "{{ email_port }}"  # 25
EMAIL_HOST_USER = "{{ email_host_user }}"  # ''
EMAIL_HOST_PASSWORD = "{{ email_host_password }}"  # ''
EMAIL_USE_TLS = "{{ email_use_tls }}".lower() == "true"  # False

EMAIL_TEMPLATE_FRONTEND_URL = "{{ email_template_frontend_url }}"  # "https://plana-test.app.unistra.fr/"


#####################
# S3 storage config #
#####################

AWS_ACCESS_KEY_ID = "{{ s3_access_key }}"
AWS_SECRET_ACCESS_KEY = "{{ s3_secret_key }}"
AWS_STORAGE_BUCKET_NAME = "{{ s3_bucket }}"
AWS_S3_ENDPOINT_URL = "{{ s3_endpoint }}"


########
# CRON #
########

CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION_WARNING = "{{ cron_days_before_account_expiration_warning }}"  # 335
CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION = "{{ cron_days_before_account_expiration }}"  # 365
CRON_DAYS_BEFORE_PASSWORD_EXPIRATION_WARNING = "{{ cron_days_before_password_expiration_warning }}"  # 335
CRON_DAYS_BEFORE_PASSWORD_EXPIRATION = "{{ cron_days_before_password_expiration }}"  # 365
CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION_WARNING = "{{ cron_days_before_association_expiration_warning }}"  # 355
CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION = "{{ cron_days_before_association_expiration }}"  # 365
CRON_DAYS_BEFORE_DOCUMENT_EXPIRATION_WARNING = "{{ cron_days_before_document_expiration_warning }}"  # 10
CRON_DAYS_BEFORE_REVIEW_EXPIRATION = "{{ cron_days_before_review_expiration }}"  # 30
CRON_DAYS_BEFORE_HISTORY_EXPIRATION = "{{ cron_days_before_history_expiration }}"  # 90


########
# Misc #
########

MIGRATION_SITE_DOMAIN = "{{ migration_site_domain }}"  # "plana-test.app.unistra.fr"
MIGRATION_SITE_NAME = "{{ migration_site_name }}"  # "PlanA"
DEFAULT_FROM_EMAIL = "{{ default_from_email }}"  # "appli-plana-test@unistra.fr"

APP_DOCUMENTATION_URL = "{{ app_documentation_url }}"  # "https://ernest.unistra.fr/"

ASSOCIATION_IS_SITE_DEFAULT = "{{ association_is_site_default }}"  # False

ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = "{{ association_default_amount_members_allowed }}"  # 4

NEW_YEAR_MONTH_INDEX = "{{ new_year_month_index }}"  # 9

RESTRICTED_DOMAINS = "{{ restricted_domains }}"  # ["unistra.fr", "etu.unistra.fr"]

LDAP_ENABLED = "{{ ldap_enabled }}"  # True

AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY = "{{ amount_years_before_project_invisibility }}"  # 5
AMOUNT_YEARS_BEFORE_PROJECT_DELETION = "{{ amount_years_before_project_deletion }}"  # 10

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = "{{ accounts_api_spore_description_file }}"
ACCOUNTS_API_CONF["BASE_URL"] = "{{ accounts_api_spore_base_url }}"
ACCOUNTS_API_CONF["TOKEN"] = "{{ accounts_api_spore_token }}"
