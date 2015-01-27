"""
Specific tests for the models.py file
"""

from django.test import TestCase

from notifications.store.sql.models import (
    SQLNotificationMessage,
    SQLNotificationType
)

from notifications.data import (
    NotificationMessage,
    NotificationType
)


class SQLModelsTests(TestCase):
    """
    Test cases for the models.py classes
    """

    def test_from_data_object(self):
        """
        Make sure we can hydrate a SQLNotificationMessage from a NotificationMessage
        """

        msg_type = NotificationType(
            name='foo.bar.baz'
        )

        msg = NotificationMessage(
            id=2,
            msg_type=msg_type
        )

        orm_obj = SQLNotificationMessage.from_data_object(msg)

        self.assertEqual(orm_obj.id, msg.id)

    def test_to_data_object(self):
        """
        Test that we can create a NotificationMessage from a SQLNotificationMessage
        """
        orm_obj = SQLNotificationMessage(
            id=1,
            msg_type=SQLNotificationType()
        )

        msg = orm_obj.to_data_object()
        self.assertIsNotNone(msg)
