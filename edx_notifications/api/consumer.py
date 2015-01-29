"""
All in-proc API endpoints for acting as a Notifications Consumer
NOTE that we can only query for notifications that are "durable", i.e.
persisted in our database
"""

import pytz
from datetime import datetime

from edx_notifications.stores.store import notification_store

from edx_notifications.exceptions import (
    ItemNotFoundError,
    ItemIntegrityError
)


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


def get_notifications_for_user(user_id, filters=None, options=None):
    """
    Returns a list of NotificationUserMap for the passed in user. The list will be
    ordered by most recent first

    ARGS:
        - user_id: The id of the user
        - filters: a dict containing
            - msg_id: a particular notification id to retrieve
                ( if this is used in conjuction with other filters, it may
                  result in an empty set being returned )
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


def mark_notification_read(user_id, msg_id, read=True):
    """
    Will mark a given NotificationUserMap as 'read' (or unread is 'unread' argument is passed in)
    """

    store = notification_store()
    notifications = store.get_notifications_for_user(
        user_id,
        filters={
            'msg_id': msg_id,
        },
        options={
            'select_related': False,
        }
    )

    if not notifications:
        err_msg = (
            'Could not find notification msg_id {msg_id} for {user_id}'
        ).format(msg_id=msg_id, user_id=user_id)
        raise ItemNotFoundError(err_msg)

    if len(notifications) > 1:
        # There should be at most one match, else raise an exception
        err_msg = (
            'There should be at most 1 NotificationUserMap items found for '
            'msg_id {msg_id} and user_id {user_id}. {cnt} were found!'
        ).format(msg_id=msg_id, user_id=user_id, cnt=len(notifications))

        raise ItemIntegrityError(err_msg)

    user_map = notifications[0]

    if read:
        # marking as read
        user_map.read_at = datetime.now(pytz.UTC)
    else:
        # marking as unread
        user_map.read_at = None

    store.save_notification_user_map(user_map)
