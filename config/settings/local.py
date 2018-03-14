from .base import *

DEBUG = True

SECRET_KEY = get_env_variable('HASKER_SECRET_KEY')

ALLOWED_HOSTS = ('127.0.0.1', )

INTERNAL_IPS = ('127.0.0.1', )

INSTALLED_APPS += ['debug_toolbar', ]

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware',]

ROOT_URLCONF = 'config.urls.local'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'config',
        'USER': 'test',
        'PASSWORD': 'test'
    }
}