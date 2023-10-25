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


########
# Misc #
########

MIGRATION_SITE_NAME = "Campulse"
MIGRATION_SITE_DOMAIN = environ.get('SITE_DOMAIN')
