from os import environ
from os.path import normpath
from .base import *

#######################
# Debug configuration #
#######################

DEBUG = True


##########################
# Database configuration #
##########################

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DEFAULT_DB_TEST_NAME', 'postgres'),
        'USER': environ.get('DEFAULT_DB_TEST_USER', 'postgres'),
        'PASSWORD': environ.get('DEFAULT_DB_TEST_PASSWORD', 'postgres'),
        'HOST': environ.get('DEFAULT_DB_TEST_HOST', 'localhost'),
        'PORT': environ.get('DEFAULT_DB_TEST_PORT', '5432'),
    }
}

############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = ['*']

#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = environ.get('LOG_DIR', normpath(join('/tmp', 'test_%s.log' % SITE_NAME)))
LOGGING['handlers']['file']['level'] = 'DEBUG'

for logger in LOGGING['loggers']:
    LOGGING['loggers'][logger]['level'] = 'DEBUG'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
