"""
All URL endpoints for HTML web server
"""

from django.conf.urls import patterns, url

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(
        r'/notifications/count*$',
        'edx_notifications.server.web.views.notification_count',
        name='web.notifications.count'
    ),
)
