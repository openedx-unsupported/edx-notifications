"""
All URL endpoints for HTML web server
"""

from django.conf.urls import patterns, url

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(r'^$', 'edx_notifications.server.web.views.hello', name="root"),
)
