"""
WSGI config for edx-notifications project. This is normally used
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testserver.settings")

from .startup import start_up

from django.core.wsgi import get_wsgi_application
# application is the standard name to use here
application = get_wsgi_application()  # pylint: disable=invalid-name

start_up()
