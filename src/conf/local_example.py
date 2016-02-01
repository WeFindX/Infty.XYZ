"""Development settings and globals."""

import os
from .base import *


# DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
# END DEBUG CONFIGURATION

# EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
if DEBUG:
    # If debug is enabled this means we use the project locally
    # let's allow Django to display the letters in the console
    DEFAULT_FROM_EMAIL = "noreply@infty.xyz"
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # If DEBUG is disabled send letters throug sendgrid
    EMAIL_BACKEND = "sgbackend.SendGridBackend"
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@infty.xyz")
    SENDGRID_USER = os.getenv("SENDGRID_USER", "ironcoder-demo")
    SENDGRID_PASSWORD = os.getenv("SENDGRID_PASSWORD", "123456789a")
# END EMAIL CONFIGURATION

# DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("DATABASE_NAME", "infty"),
        'USER': os.getenv("DATABASE_USER", ""),
        'PASSWORD': os.getenv("DATABASE_PASSWORD", ""),
        'HOST': os.getenv("DATABASE_HOST", ""),
        'PORT': os.getenv("DATABASE_PORT", "")
    }
}
# END DATABASE CONFIGURATION

# CACHE CONFIGURATION
if not DEBUG:
    # Enable redis cache for production
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        },
    }

    # Set the cache backend to select2
    SELECT2_CACHE_BACKEND = 'default'
# END CACHE CONFIGURATION

# TOOLBAR CONFIGURATION
# See:
# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html#explicit-setup
if 'debug_toolbar' not in INSTALLED_APPS:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# http://django-debug-toolbar.readthedocs.org/en/latest/installation.html
INTERNAL_IPS = ('127.0.0.1',)
# END TOOLBAR CONFIGURATION
