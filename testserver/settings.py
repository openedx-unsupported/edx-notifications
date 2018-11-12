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

js_info_dict = {
    'packages': 'edx_notifications.server.web',
 }
# js_info_dict = {
#     'packages': 'edx_notifications.server.web',
#  }
#
# LANGUAGE_CODE = 'en'
# LANGUAGES = (
#     ('en', u'English '),
#     ('ar', u'العربية'),  # Arabic
#     ('Ar-sa', u'Arabic'),  # Arabic Saudi Arabia
#     ('zh', u'中文(简体)'),
#     ('ES419', u'Latin Spanish'),
#     ('es', u'Español'),
#     ('ja', u'Japanese'),
#     ('de', u'German'),
#     ('fr', u'french'),
#     ('nl', u'Dutch '),
#     ('pt', u'Português')
# )
#
# LOCALE_PATHS = [
#     os.path.join(BASE_DIR, 'locale'),
# ]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
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

# smtp configuration settings.
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'your-user-email'
EMAIL_HOST_PASSWORD = 'user-email-password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

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
        'NAME': os.path.join(BASE_DIR, 'notifications.db'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Disable the Hide Link from
# the notification pane.
HIDE_LINK_IS_VISIBLE = False

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
NOTIFICATION_MAX_LIST_SIZE = 100

# a mapping table which is used by the MsgTypeToUrlLinkResolver
# to map a notification type to a statically defined URL path
NOTIFICATION_CLICK_LINK_URL_MAPS = {
    # To serve as a test exampe this will convert
    # msg type 'open-edx.edx_notifications.lib.tests.test_publisher'
    # to /path/to/{param1}/url/{param2} with param subsitutations
    # that are passed in with the message
    'testserver.*': '/resolved_path/{param1}/url/{param2}',
}

# list all known channel providers
NOTIFICATION_CHANNEL_PROVIDERS = {
    'durable': {
        'class': 'edx_notifications.channels.durable.BaseDurableNotificationChannel',
        'options': {
            # list out all link resolvers
            'link_resolvers': {
                # right now the only defined resolver is 'type_to_url', which
                # attempts to look up the msg type (key) via
                # matching on the value
                'msg_type_to_url': {
                    'class': 'edx_notifications.channels.link_resolvers.MsgTypeToUrlLinkResolver',
                    'config': {
                        '_click_link': NOTIFICATION_CLICK_LINK_URL_MAPS,
                    }
                }
            }
        }
    },
    'triggered-email': {
        'class': 'edx_notifications.channels.triggered_email.TriggeredEmailChannelProvider',
        'options': {
            # list out all link resolvers
            'link_resolvers': {
                # right now the only defined resolver is 'type_to_url', which
                # attempts to look up the msg type (key) via
                # matching on the value
                'msg_type_to_url': {
                    'class': 'edx_notifications.channels.link_resolvers.MsgTypeToUrlLinkResolver',
                    'config': {
                        '_click_link': NOTIFICATION_CLICK_LINK_URL_MAPS,
                    }
                }
            }
        }
    },
    'null': {
        'class': 'edx_notifications.channels.null.NullNotificationChannel',
        'options': {}
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.i18n', # this one
 )

# list all of the mappings of notification types to channel
NOTIFICATION_CHANNEL_PROVIDER_TYPE_MAPS = {
    '*': 'durable',  # default global mapping
}

NOTIFICATION_ARCHIVE_ENABLED = False

# default preferences must be strings
NOTIFICATIONS_PREFERENCE_DEFAULTS = {
    'DAILY_DIGEST': 'false',
    'WEEKLY_DIGEST': 'true',
}

import sys
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    }
}

# digest email logos
NOTIFICATION_BRANDED_DEFAULT_LOGO = 'img/edx-openedx-logo-tag.png'

# digest email css
#NOTIFICATION_DIGEST_EMAIL_CSS = 'css/email_digests.css'

NOTIFICATION_SITE_NAME = "http://localhost:8000/"

try:
    from local_settings import *
except Exception:
    pass
