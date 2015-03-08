"""
All in-proc API endpoints for acting as a Notification Publisher

IMPORTANT: All methods exposed here will also be exposed in as a
xBlock runtime service named 'notifications'. Be aware that adding
any new methods here will also be exposed to xBlocks!!!!
"""

import types
import datetime
from contracts import contract

from django.db.models.query import ValuesListQuerySet

from edx_notifications.channels.channel import get_notification_channel
from edx_notifications.stores.store import notification_store

from edx_notifications.data import (
    NotificationType,
    NotificationMessage,
    NotificationCallbackTimer,
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
def bulk_publish_notification_to_users(user_ids, msg, exclude_user_ids=None):
    """
    This top level API method will publish a notification
    to a group (potentially large). We have a distinct entry
    point to consider any optimizations that might be possible
    when doing bulk operations

    Ultimately this method will look up the user's preference
    to which NotificationChannel to distribute this over.

    ARGS:
        - user_ids: an iterator that we can enumerate over, say a list or a generator or a ORM resultset
        - msg: A NotificationMessage

    IMPORTANT: If caller wishes to send in a resutset from a Django ORM query, you must
    only select the 'id' column and flatten the results. For example, to send a notification
    to everyone in the Users table, do:

        num_sent = bulk_publish_notification_to_users(
            User.objects.values_list('id', flat=True).all(),
            msg
        )

    """

    if (not isinstance(user_ids, list) and not
            isinstance(user_ids, types.GeneratorType) and not
            isinstance(user_ids, ValuesListQuerySet)):

        err_msg = (
            'bulk_publish_notification_to_users() can only be called with a user_ids argument '
            'of type list, GeneratorType, or ValuesListQuerySet. Type {arg_type} was passed in!'
            .format(arg_type=type(user_ids))
        )
        raise TypeError(err_msg)

    # validate the msg, this will raise a ValidationError if there
    # is something malformatted or missing in the NotificationMessage
    msg.validate()

    # get the system defined msg_type -> channel mapping
    # note, when we enable user preferences, we will
    # have to change this
    channel = get_notification_channel(None, msg.msg_type)

    num_sent = channel.bulk_dispatch_notification(user_ids, msg, exclude_user_ids=exclude_user_ids)

    #
    # Here is where we will tie into the Analytics pipeline
    #

    return num_sent


@contract(msg=NotificationMessage, send_at=datetime.datetime, scope_name=basestring, scope_context=dict)
def publish_timed_notification(msg, send_at, scope_name, scope_context, timer_name=None):
    """
    Registers a new notification message to be dispatched
    at a particular time.

    IMPORTANT: There can only be one timer associated with
    a notification message. If it is called more than once on the
    same msg_id, then the existing one is updated.

    ARGS:
        send_at: datetime when the message should be sent
        msg: An instance of a NotificationMessage
        distribution_scope: enum of three values: 'user', 'course_group', 'course_enrollments'
               which describe the distribution scope of the message
        scope_context:
            if scope='user': then {'user_id': xxxx }
            if scope='course_group' then {'course_id': xxxx, 'group_id': xxxxx}
            if scope='course_enrollments' then {'course_id'}

        timer_name: if we know the name of the timer we want to use rather than auto-generating it.
                    use caution not to mess with other code's timers!!!

    RETURNS: instance of NotificationCallbackTimer
    """

    store = notification_store()

    # make sure we put the delivery timestamp on the message as well
    msg.deliver_no_earlier_than = send_at
    saved_msg = store.save_notification_message(msg)

    _timer_name = timer_name if timer_name else 'notification-dispatch-timer-{_id}'.format(_id=saved_msg.id)

    timer = NotificationCallbackTimer(
        name=_timer_name,
        callback_at=send_at,
        class_name='edx_notifications.callbacks.NotificationDispatchMessageCallback',
        is_active=True,
        context={
            'msg_id': saved_msg.id,
            'distribution_scope': {
                'scope_name': scope_name,
                'scope_context': scope_context,
            }
        }
    )

    saved_timer = store.save_notification_timer(timer)

    return saved_timer
