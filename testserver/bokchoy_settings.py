#!/usr/bin/bash
# -*- coding: utf-8 -*
"""
Django settings for edx_notifications test project.
For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
# This is just a container for running tests
DEBUG = True
SECRET_KEY='SHHHHHH'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'testserver',
    'rest_framework',
    'edx_notifications',
    'edx_notifications.server.web',
    'django_nose',
)


LANGUAGE_COOKIE_NAME = "openedx-language-preference"
LANGUAGES = (
    ('en', u'English '),
    ('ar', u'العربية'),  # Arabic
    ('es', u'Español'),
    ('nl', u'Dutch '),
    ('pt', u'Português'),
    ('zh-ch', u'中文(简体)'),
    ('fr', u'Français'),
    ('jp', u'日本人'),
    ('de', u'Deutsche'),
)

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

MIDDLEWARE_CLASSES = (

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': '10/sec',
    }
}

ROOT_URLCONF = 'testserver.urls'

WSGI_APPLICATION = 'testserver.wsgi.application'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'testserver/templates')],
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    }
]

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test_notifications.db'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/


TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Disable the  Hide Link from
# the notification pane.
HIDE_LINK_IS_VISIBLE = True

# Enable the Notification Preferences settings
NOTIFICATION_PREFERENCES_IS_VISIBLE = True

NOTIFICATION_STORE_PROVIDER = {
    "class": "edx_notifications.stores.sql.store_provider.SQLNotificationStoreProvider",
    "options": {
    }
}

SOUTH_MIGRATION_MODULES = {
    'edx_notifications': 'edx_notifications.stores.sql.migrations',
}

# to prevent run-away queries from happening
MAX_NOTIFICATION_LIST_SIZE = 100

# list all known channel providers
NOTIFICATION_CHANNEL_PROVIDERS = {
    'durable': {
        'class': 'edx_notifications.channels.durable.BaseDurableNotificationChannel',
        'options': {}
    },
    'null': {
        'class': 'edx_notifications.channels.null.NullNotificationChannel',
        'options': {}
    }
}

# list all of the mappings of notification types to channel
NOTIFICATION_CHANNEL_PROVIDER_TYPE_MAPS = {
    '*': 'durable',  # default global mapping
}
