from .base import *

DEBUG = True

SECRET_KEY = get_env_variable('HASKER_SECRET_KEY')

ALLOWED_HOSTS = ('127.0.0.1', 'localhost',)

INTERNAL_IPS = ('127.0.0.1', )

DATABASES['default'].update({
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': get_env_variable('DB_NAME'),
    'USER': get_env_variable('DB_USER'),
    'PASSWORD': get_env_variable('DB_PASSWORD'),
})

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa F405

INSTALLED_APPS += ['debug_toolbar', ]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025
