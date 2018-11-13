"""
URL mappings for Notifications Server
"""

from django.conf.urls import url, include
from django.views.i18n import JavaScriptCatalog

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^web/', include('edx_notifications.server.web.urls')),
    url(r'^api/', include('edx_notifications.server.api.urls')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
