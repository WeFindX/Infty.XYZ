"""Production settings and globals."""



# from os import environ
from os.path import join, normpath

from .base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
# from django.core.exceptions import ImproperlyConfigured


# def get_env_setting(setting):
#     """ Get the environment setting or return exception """
#     try:
#         return environ[setting]
#     except KeyError:
#         error_msg = "Set the %s env variable" % setting
#         raise ImproperlyConfigured(error_msg)

# HOST CONFIGURATION
DEBUG = True
# See:
# https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = ['*']
# END HOST CONFIGURATION

# EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
DEFAULT_FROM_EMAIL = "noreply@infty.xyz"
EMAIL_BACKEND = "sgbackend.SendGridBackend"
SENDGRID_USER = "ironcoder-demo"
SENDGRID_PASSWORD = "123456789a"
# END EMAIL CONFIGURATION

# DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': normpath(join(DJANGO_ROOT, 'default.db')),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
# END DATABASE CONFIGURATION


# CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
# END CACHE CONFIGURATION

# LOGGING CONFIGURATION
# FOR SENTRY
# http://raven.readthedocs.org/en/latest/integrations/django.html#integration-with-logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# END LOGGING CONFIGURATION

# RAVEN CONFIGURATION
RAVEN_CONFIG = {
    'dsn': 'http://166c925c5d5c4059acd204ecf9b89627:292f0cf418ce46b4bd49e4406bc04d9e@sentry.7webpages.com/9',
}
INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)
# END RAVEN CONFIGURATION


try:
    from .secret import *
except ImportError:
    pass
