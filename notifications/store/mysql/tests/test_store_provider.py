"""
Tests which exercise the MySQL test_data_provider
"""

from datetime import datetime

from django.test import TestCase

from notifications.store.mysql.store_provider import MySQLNotificationStoreProvider
from notifications.data import (
    NotificationMessage,
    NotificationType,
    NotificationUserMap
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
        self.test_user_id = 1

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

    def test_update_notification(self):
        """
        Save and then update notification
        """

        msg = self._save_new_notification()
        msg.payload = {
            'updated': True,
        }

        saved_msg = self.provider.save_notification_message(msg)

        self.assertEqual(msg, saved_msg)

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

    def test_save_notification_type(self):
        """
        Happy path saving (and retrieving) a new message type
        """

        notification_type = NotificationType(
            name='foo.bar.baz'
        )

        with self.assertNumQueries(3):
            result = self.provider.save_notification_type(notification_type)

        self.assertIsNotNone(result)
        self.assertEqual(result, notification_type)

        with self.assertNumQueries(1):
            result = self.provider.get_notification_type(notification_type.name)

        self.assertIsNotNone(result)
        self.assertEqual(result, notification_type)

    def test_cant_find_notification_type(self):
        """
        Negative test for loading notification type
        """

        with self.assertRaises(ItemNotFoundError):
            self.provider.get_notification_type('non-existing')

    def test_update_notification_type(self):
        """
        Assert that we cannot change a notification type
        """

        notification_type = NotificationType(
            name='foo.bar.baz'
        )

        with self.assertNumQueries(3):
            self.provider.save_notification_type(notification_type)

        # This should be fine saving again, since nothing is changing

        with self.assertNumQueries(2):
            self.provider.save_notification_type(notification_type)

    def test_get_no_notifications_for_user(self):
        """
        Make sure that get_num_notifications_for_user and get_notifications_for_user
        return 0 and empty set respectively
        """

        with self.assertNumQueries(1):
            self.assertEqual(
                self.provider.get_num_notifications_for_user(self.test_user_id),
                0
            )

        with self.assertNumQueries(1):
            self.assertFalse(
                self.provider.get_notifications_for_user(self.test_user_id)
            )

    def test_get_notifications_for_user(self):
        """
        Test retrieving notifications for a user
        """

        # set up some notifications

        msg1 = self.provider.save_notification_message(NotificationMessage(
            namespace='namespace1',
            payload={
                'foo': 'bar',
                'one': 1,
                'none': None,
                'datetime': datetime.utcnow(),
                'iso8601-fakeout': '--T::',  # something to throw off the iso8601 parser heuristic
            }
        ))

        self.provider.save_notification_user_map(NotificationUserMap(
            user_id=self.test_user_id,
            msg=msg1
        ))

        msg2 = self.provider.save_notification_message(NotificationMessage(
            namespace='namespace2',
            payload={
                'foo': 'baz',
                'one': 1,
                'none': None,
                'datetime': datetime.utcnow(),
                'iso8601-fakeout': '--T::',  # something to throw off the iso8601 parser heuristic
            }
        ))

        self.provider.save_notification_user_map(NotificationUserMap(
            user_id=self.test_user_id,
            msg=msg2
        ))

        with self.assertNumQueries(1):
            self.assertEqual(
                self.provider.get_num_notifications_for_user(self.test_user_id),
                2
            )

        # make sure we get back what we put in
        #
        # NOTE because we are selecting_related() on the quering of
        # the notifications, this should be done in one round trip
        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(self.test_user_id)

            self.assertEqual(notifications[0].msg, msg1)
            self.assertEqual(notifications[1].msg, msg2)

        #
        # test file namespace filtering
        #
        self.assertEqual(
            self.provider.get_num_notifications_for_user(self.test_user_id, namespace='namespace1'),
            1
        )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(self.test_user_id, namespace='namespace1')

            self.assertEqual(notifications[0].msg, msg1)

        self.assertEqual(
            self.provider.get_num_notifications_for_user(self.test_user_id, namespace='namespace2'),
            1
        )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(self.test_user_id, namespace='namespace2')

            self.assertEqual(notifications[0].msg, msg2)

        #
        # test read filtering, should be none right now
        #
        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                read=True,
                unread=False
            ),
            0
        )

        # if you ask for both not read and not unread, that should be a ValueError as that
        # combination makes no sense
        with self.assertRaises(ValueError):
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                read=False,
                unread=False
            )



