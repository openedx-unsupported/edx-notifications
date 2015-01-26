"""
Django settings file for local development purposes
"""

DEBUG=True
TEST_MODE=True
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_ROOT = "tests"
TRANSACTIONS_MANAGED = {}
USE_TZ = False
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

    'notifications',
    'django_nose',
    'south',
)

NOTIFICATION_STORE_PROVIDER = {
    "class": "notifications.store.mysql.store_provider.MySQLNotificationStoreProvider",
    "options": {
    }
}

MIDDLEWARE_CLASSES = {}

SOUTH_MIGRATION_MODULES = {
    'notifications': 'notifications.store.mysql.migrations',
}

