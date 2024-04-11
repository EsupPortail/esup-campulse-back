"""Configuration for pre-production server environment."""

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

ALLOWED_HOSTS = [
    ".u-strasbg.fr",
    ".unistra.fr",
]

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

CAS_NAME = "{{ cas_name }}"
CAS_SERVER = "{{ cas_server }}"  # "https://cas-pprd.unistra.fr/cas/"
CAS_VERSION = int("{{ cas_version }}")
CAS_INSTITUTION_ID = int("{{ cas_institution_id }}")
CAS_AUTHORIZED_SERVICES = "{{ cas_authorized_services }}".split()
# ["https://plana-pprd.app.unistra.fr/cas-login", "https://plana-pprd.app.unistra.fr/cas-register"]


##########
# Emails #
##########

EMAIL_HOST = "{{ email_host }}"
EMAIL_PORT = "{{ email_port }}"
EMAIL_HOST_USER = "{{ email_host_user }}"
EMAIL_HOST_PASSWORD = "{{ email_host_password }}"
EMAIL_USE_TLS = "{{ email_use_tls }}".lower() == "true"

EMAIL_TEMPLATE_FRONTEND_URL = "{{ email_template_frontend_url }}"  # "https://plana-pprd.app.unistra.fr/"


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

CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION_WARNING = int("{{ cron_days_before_account_expiration_warning }}")
CRON_DAYS_BEFORE_ACCOUNT_EXPIRATION = int("{{ cron_days_before_account_expiration }}")
CRON_DAYS_BEFORE_PASSWORD_EXPIRATION_WARNING = int("{{ cron_days_before_password_expiration_warning }}")
CRON_DAYS_BEFORE_PASSWORD_EXPIRATION = int("{{ cron_days_before_password_expiration }}")
CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION_WARNING = int("{{ cron_days_before_association_expiration_warning }}")
CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION = int("{{ cron_days_before_association_expiration }}")
CRON_DAYS_BEFORE_DOCUMENT_EXPIRATION_WARNING = int("{{ cron_days_before_document_expiration_warning }}")
CRON_DAYS_BEFORE_REVIEW_EXPIRATION = int("{{ cron_days_before_review_expiration }}")
CRON_DAYS_BEFORE_HISTORY_EXPIRATION = int("{{ cron_days_before_history_expiration }}")


########
# Misc #
########

MIGRATION_SITE_DOMAIN = "{{ migration_site_domain }}"  # "plana-pprd.app.unistra.fr"
MIGRATION_SITE_NAME = "{{ migration_site_name }}"
DEFAULT_FROM_EMAIL = "{{ default_from_email }}"  # "appli-plana-pprd@unistra.fr"

APP_DOCUMENTATION_URL = "{{ app_documentation_url }}"

ASSOCIATION_IS_SITE_DEFAULT = "{{ association_is_site_default }}".lower() == "true"

ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = int("{{ association_default_amount_members_allowed }}")

NEW_YEAR_MONTH_INDEX = int("{{ new_year_month_index }}")

RESTRICTED_DOMAINS = "{{ restricted_domains }}".split()

LDAP_ENABLED = "{{ ldap_enabled }}".lower() == "true"

AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY = int("{{ amount_years_before_project_invisibility }}")
AMOUNT_YEARS_BEFORE_PROJECT_DELETION = int("{{ amount_years_before_project_deletion }}")

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = "{{ accounts_api_spore_description_file }}"
ACCOUNTS_API_CONF["BASE_URL"] = "{{ accounts_api_spore_base_url }}"
ACCOUNTS_API_CONF["TOKEN"] = "{{ accounts_api_spore_token }}"
