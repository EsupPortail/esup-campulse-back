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

EMAIL_HOST = "maildev"
EMAIL_PORT = 1025
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False

EMAIL_TEMPLATE_FRONTEND_URL = "maildev:3000/"


#####################
# S3 storage config #
#####################

AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = environ.get("AWS_S3_ENDPOINT_URL")


########
# Misc #
########

MIGRATION_SITE_NAME = "Campulse"
MIGRATION_SITE_DOMAIN = environ.get("SITE_DOMAIN")

# External APIs
ACCOUNTS_API_CONF["DESCRIPTION_FILE"] = environ.get("ACCOUNTS_API_SPORE_DESCRIPTION_FILE")
ACCOUNTS_API_CONF["BASE_URL"] = environ.get("ACCOUNTS_API_SPORE_BASE_URL")
ACCOUNTS_API_CONF["TOKEN"] = environ.get("ACCOUNTS_API_SPORE_TOKEN")
