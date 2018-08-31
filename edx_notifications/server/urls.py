"""
URL mappings for Notifications Server
"""

from django.conf.urls import url, include

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^web/', include('edx_notifications.server.web.urls')),
    url(r'^api/', include('edx_notifications.server.api.urls')),
]
