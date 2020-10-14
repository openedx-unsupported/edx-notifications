"""
All URL mappings for the API's which do not get mapped to Django REST Frameworks view handlers
This is useful for when we need a UI tier to do a reverse on URL's where we don't need to import
all of the backend
"""


from django.http import HttpResponseBadRequest
from django.urls import re_path

from .url_regex import (
    CONSUMER_NOTIFICATIONS_REGEX,
    CONSUMER_USER_PREFERENCES_REGEX,
    CONSUMER_NOTIFICATION_DETAIL_REGEX,
    CONSUMER_NOTIFICATIONS_COUNT_REGEX,
    CONSUMER_RENDERERS_TEMPLATES_REGEX,
    CONSUMER_USER_PREFERENCES_DETAIL_REGEX,
    CONSUMER_NOTIFICATIONS_PREFERENCES_REGEX,
    CONSUMER_NOTIFICATION_DETAIL_NO_PARAM_REGEX,
    CONSUMER_NOTIFICATIONS_MARK_NOTIFICATIONS_REGEX,
    CONSUMER_USER_PREFERENCES_DETAIL_NO_PARAM_REGEX,
    ADMIN_USERS_DELETE
)


def mock_handler(request):  # pylint: disable=unused-argument
    """
    Simply return a 400
    """
    return HttpResponseBadRequest()


urlpatterns = [  # pylint: disable=invalid-name
    re_path(
        CONSUMER_NOTIFICATIONS_COUNT_REGEX,
        mock_handler,
        name='edx_notifications.consumer.notifications.count'
    ),
    re_path(
        CONSUMER_NOTIFICATION_DETAIL_REGEX,
        mock_handler,
        name='edx_notifications.consumer.notifications.detail'
    ),
    re_path(
        CONSUMER_NOTIFICATION_DETAIL_NO_PARAM_REGEX,
        mock_handler,
        name='edx_notifications.consumer.notifications.detail.no_param'
    ),
    re_path(
        CONSUMER_NOTIFICATIONS_MARK_NOTIFICATIONS_REGEX,
        mock_handler,
        name='edx_notifications.consumer.notifications.mark_notifications_as_read'
    ),
    re_path(
        CONSUMER_NOTIFICATIONS_REGEX,
        mock_handler,
        name='edx_notifications.consumer.notifications'
    ),
    re_path(
        CONSUMER_RENDERERS_TEMPLATES_REGEX,
        mock_handler,
        name='edx_notifications.consumer.renderers.templates'
    ),
    re_path(
        CONSUMER_NOTIFICATIONS_PREFERENCES_REGEX,
        mock_handler,
        name='edx_notifications.consumer.notification_preferences'
    ),
    re_path(
        CONSUMER_USER_PREFERENCES_REGEX,
        mock_handler,
        name='edx_notifications.consumer.user_preferences'
    ),
    re_path(
        CONSUMER_USER_PREFERENCES_DETAIL_REGEX,
        mock_handler,
        name='edx_notifications.consumer.user_preferences.detail'
    ),
    re_path(
        CONSUMER_USER_PREFERENCES_DETAIL_NO_PARAM_REGEX,
        mock_handler,
        name='edx_notifications.consumer.user_preferences.detail.no_param'
    ),
    url(
        ADMIN_USERS_DELETE,
        mock_handler,
        name='edx_notifications.admin.delete_user_notifications'
    ),
]
