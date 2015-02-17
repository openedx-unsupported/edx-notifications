"""
All in-proc API endpoints for acting as a Notification Publisher
"""

from contracts import contract

from edx_notifications.channels.channel import get_notification_channel
from edx_notifications.stores.store import notification_store

from edx_notifications.data import (
    NotificationType,
    NotificationMessage,
)

from edx_notifications.renderers.renderer import (
    register_renderer
)


@contract(msg_type=NotificationType)
def register_notification_type(msg_type):
    """
    Registers a new notification type
    """

    # do validation
    msg_type.validate()

    notification_store().save_notification_type(msg_type)

    # also register the Renderer associated with this
    # type, note that the multiple msg types can have
    # the same renderer, but only one entry will
    # get placed in the registry
    register_renderer(msg_type.renderer)


@contract(type_name=basestring)
def get_notification_type(type_name):
    """
    Returns the NotificationType registered by type_name
    """

    return notification_store().get_notification_type(type_name)


def get_all_notification_types():
    """
    Returns all know Notification types
    """

    return notification_store().get_all_notification_types()


@contract(user_id='int,>0', msg=NotificationMessage)
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
        A new instance of UserNotification that includes any auto-generated
        fields
    """

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

    user_msg = channel.dispatch_notification_to_user(user_id, msg)

    #
    # Here is where we will tie into the Analytics pipeline
    #

    return user_msg


@contract(msg=NotificationMessage)
def bulk_publish_notification_to_users(user_ids, msg):
    """
    This top level API method will publish a notification
    to a user.

    Ultimately this method will look up the user's preference
    to which NotificationChannel to distribute this over.

    ARGS:
        - user_ids: an iterator that we can enumerate over, say a list or a generator
        - msg: A NotificationMessage

    """

    # validate the msg, this will raise a ValidationError if there
    # is something malformatted or missing in the NotificationMessage
    msg.validate()

    # get the system defined msg_type -> channel mapping
    # note, when we enable user preferences, we will
    # have to change this
    channel = get_notification_channel(None, msg.msg_type)

    channel.bulk_dispatch_notification(user_ids, msg)

    #
    # Here is where we will tie into the Analytics pipeline
    #
