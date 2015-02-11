"""
All URL mappings for HTTP-based APIs
"""
from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from edx_notifications.server.api import consumer as consumer_views

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(
        r'edx_notifications/v1/consumer/notifications/count$',
        consumer_views.NotificationCount.as_view(),
        name='edx_notifications.consumer.notifications.count'
    ),
    url(
        r'edx_notifications/v1/consumer/notifications/(?P<msg_id>[0-9]+)$',
        consumer_views.NotificationDetail.as_view(),
        name='edx_notifications.consumer.notifications.detail'
    ),
    url(
        r'edx_notifications/v1/consumer/notifications$',
        consumer_views.NotificationsList.as_view(),
        name='edx_notifications.consumer.notifications'
    ),
    url(
        r'edx_notifications/v1/consumer/renderers/templates$',
        consumer_views.RendererTemplatesList.as_view(),
        name='edx_notifications.consumer.renderers.templates'
    ),
)

urlpatterns = format_suffix_patterns(urlpatterns)  # pylint: disable=invalid-name
