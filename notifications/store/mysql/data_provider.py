"""
Concrete MySQL implementation of the data provider interface
"""


from django.core.exceptions import ObjectDoesNotExist

from notifications.store.base import NotificationDataProviderBase
from notifications.data import NotificationMessage
from notifications.exceptions import ItemNotFoundError

from notifications.store.mysql.models import (
    SQLNotificationMessage,
)


class MySQLNotificationDataProvider(NotificationDataProviderBase):
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

        msg = NotificationMessage(
            msg_id=obj.id,
            payload=obj.payload
        )
        return msg

    def save_notification_message(self, msg):
        """
        Saves a passed in NotificationMsg data object. If 'id' is set by the caller
        it will try to update the object. If it does not exist it will throw an
        exception.

        If it is created, then the id property will be set on the NotificationMsg and returned
        """

        if msg.msg_id:
            try:
                obj = SQLNotificationMessage.objects.get(id=msg.msg_id)
            except ObjectDoesNotExist:
                raise ItemNotFoundError()
        else:
            obj = SQLNotificationMessage(
                payload=msg.payload
            )

        obj.save()
        msg.msg_id = obj.id
        return msg
