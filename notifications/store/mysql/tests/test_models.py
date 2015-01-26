"""
Specific tests for the models.py file
"""

from django.test import TestCase

from notifications.store.mysql.models import (
    SQLNotificationMessage
)

from notifications.data import (
    NotificationMessage
)


class SQLModelsTests(TestCase):
    """
    Test cases for the models.py classes
    """

    def test_from_data_object(self):
        """
        Make sure we can hydrate a SQLNotificationMessage from a NotificationMessage
        """
        orm_obj = SQLNotificationMessage()

        msg = NotificationMessage(
            id=2
        )

        orm_obj = SQLNotificationMessage.from_data_object(msg)

        self.assertEqual(orm_obj.id, msg.id)

    def test_to_data_object(self):
        """
        Test that we can create a NotificationMessage from a SQLNotificationMessage
        """
        orm_obj = SQLNotificationMessage(
            id=1
        )

        msg = orm_obj.to_data_object()
        self.assertIsNotNone(msg)
