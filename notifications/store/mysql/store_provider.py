"""
Concrete MySQL implementation of the data provider interface
"""

from django.core.exceptions import ObjectDoesNotExist

from notifications.store.store import BaseNotificationStoreProvider
from notifications.exceptions import ItemNotFoundError

from notifications.store.mysql.models import (
    SQLNotificationMessage,
)


class MySQLNotificationStoreProvider(BaseNotificationStoreProvider):
    """
    Concrete MySQL implementation of the abstract base class (interface)
    """

    def get_notification_message_by_id(self, msg_id):
        """
        For the given message id return the corresponding NotificationMessage data object
        """

        try:
            obj = SQLNotificationMessage.objects.get(id=msg_id)
        except ObjectDoesNotExist:
            raise ItemNotFoundError()

        return obj.to_data_object()

    def save_notification_message(self, msg):
        """
        Saves a passed in NotificationMsg data object. If 'id' is set by the caller
        it will try to update the object. If it does not exist it will throw an
        exception.

        If it is created, then the id property will be set on the NotificationMsg and returned
        """

        if msg.id:
            try:
                obj = SQLNotificationMessage.objects.get(id=msg.id)
            except ObjectDoesNotExist:
                raise ItemNotFoundError()
        else:
            obj = SQLNotificationMessage()

        # copy over all of the fields from the data object into the
        # ORM object
        obj.from_data_object(msg)
        obj.save()
        msg.id = obj.id
        return msg

    def get_notifications_for_user(self, user_id, read=True, unread=True):
        """
        Returns a (unsorted) collection (list) of notifications for the user.

        NOTE: We will have to add paging (with sorting/filtering) in the future

        ARGS:
            - user_id: The id of the user
            - read: Whether to return read notifications (default True)
            - unread: Whether to return unread notifications (default True)

        RETURNS: list   i.e. []
        """

        result_set = []

        return result_set
