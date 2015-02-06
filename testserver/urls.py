"""
URL mappings for Notifications Server
"""

from django.conf.urls import patterns, url, include

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(r'^$', 'testserver.views.index', name='index'),
    url(r'^login/*$', 'testserver.views.login', name='login'),
    url(r'^api/', include('edx_notifications.server.api.urls')),
)
