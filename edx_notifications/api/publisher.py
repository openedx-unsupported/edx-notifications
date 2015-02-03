"""
All in-proc API endpoints for acting as a Notification Publisher
"""

from edx_notifications.channels.channel import get_notification_channel
from edx_notifications.stores.store import notification_store


def register_notification_type(msg_type):
    """
    Registers a new notification type
    """

    # do validation
    msg_type.validate()

    notification_store().save_notification_type(msg_type)


def publish_notification_to_user(user_id, msg):
    """
    This top level API method will publish a notification
    to a user.

    Ultimately this method will look up the user's preference
    to which NotificationChannel to distribute this over.

    ARGS:
        - user_id: An unconstrained identifier to some user identity
        - msg: A NotificationMessage

    RETURNS:
        A new instance of NotificationUserMap that includes any auto-generated
        fields
    """

    # make sure user_id is an integer
    if not isinstance(user_id, int):
        raise TypeError("user_id must be an integer")

    # validate the msg, this will raise a ValidationError if there
    # is something malformatted or missing in the NotificationMessage
    msg.validate()

    # get the notification channel associated
    # for this message type as well as this user
    # as users will be able to choose how to
    # receive their notifications per type.
    #
    # This call will never return None, if there is
    # a problem, it will throw an exception
    channel = get_notification_channel(user_id, msg.msg_type)

    _user_map = channel.dispatch_notification_to_user(user_id, msg)

    #
    # Here is where we will tie into the Analytics pipeline
    #

    return _user_map
