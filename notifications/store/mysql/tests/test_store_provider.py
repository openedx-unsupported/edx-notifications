"""
Tests which exercise the MySQL test_data_provider
"""

from datetime import datetime

from django.test import TestCase

from notifications.store.mysql.store_provider import MySQLNotificationStoreProvider
from notifications.data import (
    NotificationMessage,
)

from notifications.exceptions import (
    ItemNotFoundError
)


class TestMySQLStoreProvider(TestCase):
    """
    This class exercises all of the implementation methods for the
    abstract DataProvider class
    """

    def setUp(self):
        """
        Setup the test case
        """
        self.provider = MySQLNotificationStoreProvider()

    def _save_new_notification(self, payload='This is a test payload'):
        """
        Helper method to create a new notification
        """

        msg = NotificationMessage(
            payload={
                'foo': 'bar',
                'one': 1,
                'none': None,
                'datetime': datetime.utcnow(),
                'iso8601-fakeout': '--T::',  # something to throw off the iso8601 parser heuristic
            }
        )

        with self.assertNumQueries(1):
            result = self.provider.save_notification_message(msg)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)
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

        with self.assertNumQueries(1):
            fetched_msg = self.provider.get_notification_message_by_id(msg.id)

        self.assertIsNotNone(fetched_msg)
        self.assertEqual(msg.id, fetched_msg.id)
        self.assertEqual(msg.payload, fetched_msg.payload)

    def test_load_nonexisting_notification(self):
        """
        Negative testing when trying to load a notification that does not exist
        """

        with self.assertRaises(ItemNotFoundError):
            with self.assertNumQueries(1):
                self.provider.get_notification_message_by_id(0)

    def test_bad_message_msg(self):
        """
        Negative testing when trying to update a msg which does not exist already
        """

        msg = self._save_new_notification()
        with self.assertRaises(ItemNotFoundError):
            msg.id = 9999999
            self.provider.save_notification_message(msg)
