#!/usr/bin/bash
# -*- coding: utf-8 -*
"""
Django settings file for local development purposes
"""
import sys


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG=True
TEST_MODE=True
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_ROOT = "tests"
TRANSACTIONS_MANAGED = {}
USE_TZ = True
TIME_ZONE = 'UTC'
SECRET_KEY='SHHHHHH'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '{}/db/notifications.db'.format(TEST_ROOT)
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'rest_framework',
    'edx_notifications',
    'edx_notifications.server.web',
    'django_nose',
)

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.UserRateThrottle',
    ),
}

if not TEST_MODE:
    # we don't want to throttle unit tests
    REST_FRAMEWORK.update({
        'DEFAULT_THROTTLE_RATES': {
            'user': '10/sec',
        }
    })


js_info_dict = {
    # 'packages': 'edx_notifications.server.web',
 }
LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', u'English '),
    ('ar', u'العربية'),  # Arabic
    ('Ar-sa', u'Arabic'),  # Arabic Saudi Arabia
    ('zh', u'中文(简体)'),
    ('ES419', u'Latin Spanish'),
    ('es', u'Español'),
    ('ja', u'Japanese'),
    ('de', u'German'),
    ('fr', u'french'),
    ('nl', u'Dutch '),
    ('pt', u'Português')
)
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'static_cache/locale'),
]

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'edx_notifications.server.urls'

WSGI_APPLICATION = 'edx_notifications.server.wsgi.application'


TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['edx_notifications/server/web/templates']
}]

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
    'open-edx.edx_notifications.lib.tests.test_publisher': '/path/to/{param1}/url/{param2}',
    'open-edx.edx_notifications.lib.tests.*': '/alternate/path/to/{param1}/url/{param2}',
    'open-edx-edx_notifications.lib.*': '/third/way/to/get/to/{param1}/url/{param2}',
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
    'parse-push': {
        'class': 'edx_notifications.channels.parse_push.ParsePushNotificationChannelProvider',
        'options': {
            'application_id': 'test_id',
            'rest_api_key': 'test_rest_api_key',
        }
    },
    'urban-airship': {
        'class': 'edx_notifications.channels.urban_airship.UrbanAirshipNotificationChannelProvider',
        'options': {}
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

# list all of the mappings of notification types to channel
NOTIFICATION_CHANNEL_PROVIDER_TYPE_MAPS = {
    '*': 'durable',  # default global mapping
}

# Constants to set how long (in days) old READ and UNREAD notifications can remain in the system before being purged.
NOTIFICATION_PURGE_READ_OLDER_THAN_DAYS = 30
NOTIFICATION_PURGE_UNREAD_OLDER_THAN_DAYS = 60

# digest email logos
NOTIFICATION_BRANDED_DEFAULT_LOGO = 'edx_notifications/img/edx-openedx-logo-tag.png'

# digest email css
NOTIFICATION_DIGEST_EMAIL_CSS = 'edx_notifications/css/email_digests.css'
