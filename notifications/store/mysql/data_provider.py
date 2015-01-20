"""
Concrete MySQL implementation of the data provider interface
"""

from notifications.store.data_provider import NotificationDataProviderBase
from notifications.data import NotificationMessage


class MySQLNotificationDataProvider(NotificationDataProviderBase):
    """
    Concrete MySQL implementation of the abstract base class (interface)
    """

    def get_notification_message_by_id(self, message_id):
        """
        For the given message id return the corresponding NotificationMsg data object
        """

        msg = NotificationMessage()
        return msg
