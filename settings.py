"""
Django settings file for local development purposes
"""

DEBUG=True
TEST_MODE=True
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_ROOT = "tests"
TRANSACTIONS_MANAGED = {}
USE_TZ = True
TIME_ZONE = {}
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
    'django_nose',
    'south',
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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

ROOT_URLCONF = 'edx_notifications.server.urls'

WSGI_APPLICATION = 'edx_notifications.server.wsgi.application'

TEMPLATE_DIRS = ['edx_notifications/server/web/templates']

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
