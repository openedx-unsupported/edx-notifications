"""
Tests which exercise the MySQL test_data_provider
"""

from django.test import TestCase

from notifications.store.mysql.data_provider import MySQLNotificationDataProvider
from notifications.data import (
    NotificationMessage,
)


class TestMySQLDataProvider(TestCase):
    """
    This class exercises all of the implementation methods for the
    abstract DataProvider class
    """

    def setUp(self):
        """
        Setup the test case
        """
        self.provider = MySQLNotificationDataProvider()

    def _save_new_notification(self, payload='This is a test payload'):
        """
        Helper method to create a new notification
        """

        msg = NotificationMessage(
            payload="This is a test payload"
        )

        result = self.provider.save_notification_message(msg)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.msg_id)
        return result

    def test_save_notification(self):
        """
        Test saving a single notification message
        """

        self._save_new_notification()

    def test_load_notification(self):
        """
        Save and fetch a new notification
        """

        msg = self._save_new_notification()

        fetched_msg = self.provider.get_notification_message_by_id(msg.msg_id)

        self.assertIsNotNone(fetched_msg)
        self.assertEqual(msg.msg_id, fetched_msg.msg_id)
        self.assertEqual(msg.payload, fetched_msg.payload)
