"""
All URL mappings for HTTP-based APIs
"""
from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from edx_notifications.server.api import consumer as consumer_views

urlpatterns = patterns(  # pylint: disable=invalid-name
    '',
    url(
        r'consumer/notifications/count/*$',
        consumer_views.NotificationCount.as_view(),
        name='consumer.notifications.count'
    ),
    # url(r'/consumer/notifications/read/*$', consumer_views.NotificationListRead.as_view()),
    # url(r'/consumer/notifications/read/count/*$', consumer_views.NotificationReadCount.as_view()),
    # url(r'/consumer/notifications/unread/*$', consumer_views.NotificationListUnread.as_view()),
    # url(r'/consumer/notifications/unread/count/*$', consumer_views.NotificationUnreadCount.as_view()),
    # url(r'/consumer/notifications/^(?P<session_id>[0-9]+)$', consumer_views.NotificationDetail.as_view()),
    # url(r'/consumer/notifications/*$', consumer_views.NotificationList.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)  # pylint: disable=invalid-name
