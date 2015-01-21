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

    def get_notification_message_by_id(self, message_id):
        """
        For the given message id return the corresponding NotificationMsg data object
        """

        try:
            msg = SQLNotificationMessage.objects.get(id=message_id)
        except ObjectDoesNotExist:
            raise ItemNotFoundError()

        msg = NotificationMessage(
            payload=msg.payload
        )
        return msg
