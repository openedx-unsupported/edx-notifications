"""
Implement a NullNotificationChannel which basically sinks any notification publishing.
This can be used when a system does not want to actually transmit a particular
NotificationType
"""

from edx_notifications.channels.channel import BaseNotificationChannelProvider


class NullNotificationChannel(BaseNotificationChannelProvider):
    """
    A NotificationChannel which drops all notifications. This is useful for shunting
    NotificationMessages
    """

    def dispatch_notification_to_user(self, user_id, msg):
        """
        Will not send the msg to the user_id
        """

        return None

    def bulk_dispatch_notification(self, user_ids, msg):
        """
        Will not send the msg to the list of users
        """

        # we did not send any, so return zero as a count of number of
        # dispatches
        return 0
