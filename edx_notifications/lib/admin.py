"""
All in-proc API endpoints for acting as a Notifications Admin
"""
from edx_notifications.stores.store import notification_store


def purge_user_data(user_ids):
    """
    This will purge the notifications and preferences for the given user IDs
    :param user_ids: and iterable of user IDs
    """
    store = notification_store()
    store.purge_notifications_for_users(user_ids)


def purge_notifications_with_payload(payload):
    """
    This will purge the notifications and containing the given payload
    :payload: string content contained in notifications payload
    """
    store = notification_store()
    store.purge_notifications_containing(payload)
