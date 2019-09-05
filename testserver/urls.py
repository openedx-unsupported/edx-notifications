"""
URL mappings for Notifications Server
"""

from __future__ import absolute_import

from django.conf.urls import url, include
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.views import login

from . import views as testserver_views

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$', testserver_views.index),
    url(r'^accounts/login/$', login),
    url(r'^logout/$', testserver_views.logout_page),
    url(r'^register/$', testserver_views.register),
    url(r'^register/success/$', testserver_views.register_success),

    url(r'^api/', include('edx_notifications.server.api.urls')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
