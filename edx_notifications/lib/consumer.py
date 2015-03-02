"""
All in-proc API endpoints for acting as a Notifications Consumer
NOTE that we can only query for notifications that are "durable", i.e.
persisted in our database
"""

import pytz
from datetime import datetime
from contracts import contract

from edx_notifications.stores.store import notification_store


@contract(user_id='int,>0')
def get_notifications_count_for_user(user_id, filters=None):
    """
    Returns the number of notifications this user has

    ARGS:
        user_id: The id of the user to query
        filters: A dict containing the following optional keys
            - 'namespace': what namespace to search (defuault None)
            - 'read': Whether to return read notifications (default True)
            - 'unread': Whether to return unread notifications (default True)
            - 'type_name': what msg_types to count
    """

    # make sure user_id is an integer
    if not isinstance(user_id, int):
        raise TypeError("user_id must be an integer")

    return notification_store().get_num_notifications_for_user(
        user_id,
        filters=filters,
    )


@contract(user_id='int,>0', msg_id='int,>0')
def get_notification_for_user(user_id, msg_id):
    """
    Returns a single UserNotification object for the user_id/msg_id paid.

    If it is not found a ItemNotFoundError is raised
    """
    return notification_store().get_notification_for_user(user_id, msg_id)


@contract(user_id='int,>0')
def get_notifications_for_user(user_id, filters=None, options=None):
    """
    Returns a list of UserNotification for the passed in user. The list will be
    ordered by most recent first

    ARGS:
        - user_id: The id of the user
        - filters: a dict containing
            - namespace: what namespace to search (defuault None)
            - read: Whether to return read notifications (default True)
            - unread: Whether to return unread notifications (default True)
            - type_name: which type to return
        - options: a dict containing some optional parameters
            - limit: max number to return (up to some system defined max)
            - offset: offset into the list, to implement paging
    """

    # make sure user_id is an integer
    if not isinstance(user_id, int):
        raise TypeError("user_id must be an integer")

    return notification_store().get_notifications_for_user(
        user_id,
        filters=filters,
        options=options
    )


@contract(user_id='int,>0', msg_id='int,>0', read=bool)
def mark_notification_read(user_id, msg_id, read=True):
    """
    Will mark a given UserNotification as 'read' (or unread is 'unread' argument is passed in)

    ARGS:
        - user_id: The user that wishes to mark the msg as read/unread
        - msg_id: The corresponding message that is being marked
        - read: (Optional) indicate whether message should be marked as read or unread

    NOTE: If the corresponding user_id/msg_id cannot be found, then this will raise
    a ItemNotFoundError().
    """

    store = notification_store()
    user_msg = store.get_notification_for_user(user_id, msg_id)

    if read:
        # marking as read
        user_msg.read_at = datetime.now(pytz.UTC)
    else:
        # marking as unread
        user_msg.read_at = None

    store.save_user_notification(user_msg)


@contract(user_id='int,>0')
def mark_all_user_notification_as_read(user_id):
    """
    Will mark a given user notifications as 'read'

    ARGS:
        - user_id: The user that wishes to mark the msg as read/unread

    NOTE: If the corresponding user_id cannot be found, then this will raise
    a ItemNotFoundError().
    """

    store = notification_store()
    store.mark_user_notifications_read(user_id)
