edx-notifications [![Build Status](https://travis-ci.org/edx/edx-notifications.svg?branch=master)](https://travis-ci.org/edx/edx-notifications) [![Coverage Status](https://img.shields.io/coveralls/edx/edx-notifications.svg)](https://coveralls.io/r/edx/edx-notifications?branch=master)

========================

This is the development repository for the Open edX Notification subsystem. This repository is a work in progress.



Developer's Documentation
-------------

Please see the github repository for [developer's documentation](https://github.com/edx/edx-notifications/wiki)


Standalone Testing
------------------

Please always run tests before committing code back to origin. It is required that all contributions have 100% (or close)
unit test coverage and no code convention violations (pep8/pylint).

        $ ./run_tests


Open edX Platform Integration
-----------------------------
* Add desired commit hash (tip of master) from github code repository
    * edx-platform/requirements/github.txt
    * "Our libraries" section

* Add required configuration in your settings file, e.g. common.py:

```

# add to the INSTALLED_APPS list
INSTALLED_APPS = (
    :
    'edx_notifications',
    'edx_notifications.server.web',
    :
)

# make sure that 'django.template.loaders.app_directories.Loader' is
# in the list of TEMPLATE_LOADERS
TEMPLATE_LOADERS = (
    :
    'django.template.loaders.app_directories.Loader',
    :
)

# for now we just support SQL backed stores
NOTIFICATION_STORE_PROVIDER = {
    "class": "edx_notifications.stores.sql.store_provider.SQLNotificationStoreProvider",
    "options": {
    }
}

# By default django looks for migrations in migrations package for each app but
# we can override this on per-apps basis by updating MIGRATION_MODULES setting.
# This setting already exists in the LMS, please update it
MIGRATION_MODULES = {
    'djcelery': 'ignore',
    'edx_notifications': 'edx_notifications.stores.sql.migrations',
}

# to prevent run-away queries from happening
MAX_NOTIFICATION_LIST_SIZE = 100

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
    # A null channel basically implements the Channel interface, but does not
    # do anything. This is useful for when you want to not dispatch certain notification
    # types.
    'null': {
        'class': 'edx_notifications.channels.null.NullNotificationChannel',
        'options': {}
    }
}

# list all of the mappings of notification types to channel
NOTIFICATION_CHANNEL_PROVIDER_TYPE_MAPS = {
    '*': 'durable',  # default global mapping
}
```


Development and Test HTTP Server
--------------------------------

This repository comes with a simple development and test server so that is possible to develop
and test in an isolated environment (i.e. not have to run the LMS in edx-platform). In order to
use the test server, it is recommended that you make a new dedicated Python virtual-environment:

```
virtualenv edxnotifications_env (just do this once)

source edxnotifications_env/bin/activate

pip install -r requirements.txt
pip install -r test_requirements.txt

./manage.py syncdb --settings=testserver.settings
./manage.py migrate --settings=testserver.settings

./manage.py runserver --settings=testserver.settings (run the test server)
```

The development server will provide very raw basic login/register functionality in order to
allow for authentication. Overall, the testserver is not meant to be styled, it is merely
to provide a development environment, plus to act as a HTTP server for all automated UI
test frameworks.


Bok-Choy Tests
--------------

Bok-choy tests are present in the directory

```
/testserver/test/acceptance
```

To run these tests just use the following command

```
bash run_bokchoy_tests.sh
```

To run an individual test use the above command with test name at end, for example

```
bash run_bokchoy_tests.sh test_00_show_notification_pane
```

Jasmine Tests
--------------


Before running Jasmine tests you need to install node.js, you can get it from
[here ](http://nodejs.org "get Node.JS from here")

After installing node.js just run the following command, it install all the required software for running jasmine tests.

```
npm install
```

To run the tests in normal mode with coverage enabled use following command

```
gulp test

- or (depending on search paths) -

node node_modules/gulp/bin/gulp.js test
```

To run the tests in debug mode use

```
gulp debug
```

This will start the tests in debug mode, coverage is turned off in debug mode so it will always show coverage of 0/0 in
debug mode


Writing Jasmine Tests

Jasmine tests are present in the directory

```
/edx_notifications/server/web/static/edx_notifications/js/test/spec
```

While creating a new test file make sure that file name ends in _Spec.js

Note: Jasmine checks the presence of js files in the folder mentioned in karma.config.js file, if any new directory
is added in the code, it's path should be added to karma.config


How to Contribute
-----------------
Contributions are very welcome, but please note that edx-notifications is currently an
early stage work-in-progress and is changing frequently at this time.

See our
[CONTRIBUTING](https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst)
file for more information -- it also contains guidelines for how to maintain
high code quality, which will make your contribution more likely to be accepted.


Reporting Security Issues
-------------------------
Please do not report security issues in public. Please email security@edx.org.


Mailing List and IRC Channel
----------------------------
You can discuss this code on the [edx-code Google Group](https://groups.google.com/forum/#!forum/edx-code) or in the
`edx-code` IRC channel on Freenode.
