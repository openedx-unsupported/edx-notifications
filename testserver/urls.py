"""
URL mappings for Notifications Server
"""

from django.conf.urls import patterns, url, include


urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(r'^$', 'testserver.views.index'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'testserver.views.logout_page'),
    url(r'^register/$', 'testserver.views.register'),
    url(r'^register/success/$', 'testserver.views.register_success'),

    url(r'^api/', include('edx_notifications.server.api.urls')),
)
