from .base import *

##########################
# Database configuration #
##########################

DATABASES['default']['HOST'] = environ.get('DEFAULT_DB_HOST', 'postgres')
DATABASES['default']['USER'] = environ.get('DEFAULT_DB_USER', 'plana')
DATABASES['default']['PASSWORD'] = environ.get('DEFAULT_DB_PASSWORD', 'plana')
DATABASES['default']['NAME'] = environ.get('DEFAULT_DB_NAME', 'plana')
DATABASES['default']['PORT'] = environ.get('DEFAULT_DB_PORT', '5432')


############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = ["*"]

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "ssl")


#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = environ.get('LOG_PATH', '/tmp/log')


##############
# Secret key #
##############

SECRET_KEY = environ.get('SECRET_KEY', '94a5@7gp*n&k_+-fbt=&69==sg%@evqfk8^kzztw2514f97y%0')


##########
# Emails #
##########

EMAIL_HOST = environ.get("EMAIL_HOST", 5432)
EMAIL_PORT = environ.get("EMAIL_PORT", 25)
EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = environ.get("EMAIL_USE_TLS", False)

EMAIL_TEMPLATE_FRONTEND_URL = environ.get("EMAIL_TEMPLATE_FRONTEND_URL", "http://localhost:3000/")


#####################
# S3 storage config #
#####################

AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = environ.get("AWS_STORAGE_BUCKET_NAME", "")
AWS_S3_ENDPOINT_URL = environ.get("AWS_S3_ENDPOINT_URL", "")


########
# Misc #
########

MIGRATION_SITE_NAME = environ.get("MIGRATION_SITE_NAME", "PlanA")
MIGRATION_SITE_DOMAIN = environ.get("MIGRATION_SITE_DOMAIN", "")

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = environ.get("ACCOUNTS_API_SPORE_DESCRIPTION_FILE", "")
ACCOUNTS_API_CONF["BASE_URL"] = environ.get("ACCOUNTS_API_SPORE_BASE_URL", "")
ACCOUNTS_API_CONF["TOKEN"] = environ.get("ACCOUNTS_API_SPORE_TOKEN", "")

ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED = environ.get("ASSOCIATION_DEFAULT_AMOUNT_MEMBERS_ALLOWED", "")
ASSOCIATION_IS_SITE_DEFAULT = environ.get("ASSOCIATION_IS_SITE_DEFAULT", True)
CAS_ATTRIBUTE_EMAIL = environ.get("CAS_ATTRIBUTE_EMAIL", "email")
CAS_ATTRIBUTE_FIRST_NAME = environ.get("CAS_ATTRIBUTE_FIRST_NAME", "first_name")
CAS_ATTRIBUTE_IS_STUDENT = environ.get("CAS_ATTRIBUTE_IS_STUDENT", "affliliation")
CAS_ATTRIBUTE_LAST_NAME = environ.get("CAS_ATTRIBUTE_LAST_NAME", "last_name")
CAS_AUTHORIZED_SERVICES = environ.get("CAS_AUTHORIZED_SERVICES", "https://localhost:3000/cas-login https://localhost:3000/cas-register")
CAS_NAME = environ.get("CAS_NAME", "CAS")
CAS_SERVER = environ.get("CAS_SERVER", "")
CAS_VALUE_IS_STUDENT = environ.get("CAS_VALUE_IS_STUDENT", "student")
CAS_VERSION = environ.get("CAS_VERSION", 3)
CSRF_TRUSTED_ORIGINS = environ.get("CSRF_TRUSTED_ORIGINS", "")
DEFAULT_FROM_EMAIL = environ.get("DEFAULT_FROM_EMAIL", 3)
LDAP_ENABLED = environ.get("LDAP_ENABLED", False)
