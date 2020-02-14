"""
URL mappings for Notifications Server
"""

from __future__ import absolute_import

from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

urlpatterns = [  # pylint: disable=invalid-name
    path('web/', include('edx_notifications.server.web.urls')),
    path('api/', include('edx_notifications.server.api.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
