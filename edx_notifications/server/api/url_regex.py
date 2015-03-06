"""
So we can share URL regex patterns across the real urls.py and the urls_mock.py files
"""

CONSUMER_NOTIFICATIONS_COUNT_REGEX = r'edx_notifications/v1/consumer/notifications/count$'
CONSUMER_NOTIFICATION_DETAIL_REGEX = r'edx_notifications/v1/consumer/notifications/(?P<msg_id>[0-9]+)$'
CONSUMER_NOTIFICATION_DETAIL_NO_PARAM_REGEX = r'edx_notifications/v1/consumer/notifications/$'
CONSUMER_NOTIFICATIONS_MARK_NOTIFICATIONS_REGEX = r'edx_notifications/v1/consumer/notifications/mark_notifications$'
CONSUMER_NOTIFICATIONS_REGEX = r'edx_notifications/v1/consumer/notifications$'
CONSUMER_RENDERERS_TEMPLATES_REGEX = r'edx_notifications/v1/consumer/renderers/templates$'
