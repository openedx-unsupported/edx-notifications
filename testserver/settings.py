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
TEMPLATE_DEBUG = True
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
    'south',
)

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

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, 'testserver/templates'),
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

# Disable the  Hide Link from
# the notification pane.
HIDE_LINK_IS_VISIBLE = True

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
    'null': {
        'class': 'edx_notifications.channels.null.NullNotificationChannel',
        'options': {}
    }
}

# list all of the mappings of notification types to channel
NOTIFICATION_CHANNEL_PROVIDER_TYPE_MAPS = {
    '*': 'durable',  # default global mapping
}
