"""
Implements a durable notification channel which will be a base class
that saves Notifications to a database for later
retrieval
"""

from edx_notifications.channels.channel import BaseNotificationChannelProvider

from edx_notifications.stores.store import notification_store

from edx_notifications.data import (
    NotificationUserMap
)


class BaseDurableNotificationChannel(BaseNotificationChannelProvider):
    """
    A durable notification channel will save messages to
    the database
    """

    def dispatch_notification_to_user(self, user_id, msg):
        """
        Send a notification to a user, which - in a durable Notification -
        is simply store it in the database, and - soon in the future -
        raise some signal to a waiting client that a message is available
        """

        store = notification_store()

        msg = store.save_notification_message(msg)

        # create a new NotificationUserMap and point to the new message
        # this new mapping will have the message in an unread state
        # NOTE: We need to set this up after msg is saved otherwise
        # we won't have it's primary key (id)
        user_map = NotificationUserMap(
            user_id=user_id,
            msg=msg
        )

        store.save_notification_user_map(user_map)

        # When we support in-broswer push notifications
        # such as Comet/WebSockets, this is where we should
        # signal the client to come fetch the
        # notification
