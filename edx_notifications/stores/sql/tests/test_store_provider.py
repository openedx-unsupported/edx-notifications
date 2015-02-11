"""
Tests which exercise the MySQL test_data_provider
"""

import mock
from datetime import datetime

from django.test import TestCase

from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider
from edx_notifications.data import (
    NotificationMessage,
    NotificationType,
    UserNotification
)
from edx_notifications.exceptions import (
    ItemNotFoundError
)
from edx_notifications import const


class TestSQLStoreProvider(TestCase):
    """
    This class exercises all of the implementation methods for the
    abstract DataProvider class
    """

    def setUp(self):
        """
        Setup the test case
        """
        self.provider = SQLNotificationStoreProvider()
        self.test_user_id = 1

    def _save_notification_type(self):
        """
        Helper to set up a notification_type
        """

        notification_type = NotificationType(
            name='foo.bar.baz',
            renderer='foo.renderer',
        )

        result = self.provider.save_notification_type(notification_type)

        return result

    def test_save_notification_type(self):
        """
        Happy path saving (and retrieving) a new message type
        """

        with self.assertNumQueries(3):
            notification_type = self._save_notification_type()

        self.assertIsNotNone(notification_type)

        with self.assertNumQueries(1):
            result = self.provider.get_notification_type(notification_type.name)

        self.assertIsNotNone(result)
        self.assertEqual(result, notification_type)

        # re-getting notification type should pull from cache
        # so there should be no round-trips to SQL
        with self.assertNumQueries(0):
            result = self.provider.get_notification_type(notification_type.name)

        self.assertIsNotNone(result)
        self.assertEqual(result, notification_type)

        # re-save and make sure the cache entry got invalidated
        with self.assertNumQueries(3):
            notification_type = self._save_notification_type()

        # since we invalidated the cached entry on the last save
        # when we re-query we'll hit another SQL round trip
        with self.assertNumQueries(1):
            result = self.provider.get_notification_type(notification_type.name)

        self.assertIsNotNone(result)
        self.assertEqual(result, notification_type)

    def _save_new_notification(self, payload='This is a test payload'):
        """
        Helper method to create a new notification
        """

        msg_type = self._save_notification_type()

        msg = NotificationMessage(
            msg_type=msg_type,
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
        self.assertEqual(msg.msg_type.name, fetched_msg.msg_type.name)

        # by not selecting_related (default True), this will cause another round
        # trip to the database
        with self.assertNumQueries(2):
            fetched_msg = self.provider.get_notification_message_by_id(
                msg.id,
                options={
                    'select_related': False,
                }
            )

        self.assertIsNotNone(fetched_msg)
        self.assertEqual(msg.id, fetched_msg.id)
        self.assertEqual(msg.payload, fetched_msg.payload)
        self.assertEqual(msg.msg_type.name, fetched_msg.msg_type.name)

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
            name='foo.bar.baz',
            renderer='foo.renderer',
        )

        with self.assertNumQueries(3):
            self.provider.save_notification_type(notification_type)

        # This should be fine saving again, since nothing is changing

        with self.assertNumQueries(3):
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

    @mock.patch('edx_notifications.const.MAX_NOTIFICATION_LIST_SIZE', 1)
    def test_over_limit_counting(self):
        """
        Verifies that our counting operations will work as expected even when
        our count is greater that the MAX_NOTIFICATION_LIST_SIZE which is
        the maximum page size
        """

        self.assertEqual(const.MAX_NOTIFICATION_LIST_SIZE, 1)

        msg_type = self._save_notification_type()

        for __ in range(10):
            msg = self.provider.save_notification_message(NotificationMessage(
                namespace='namespace1',
                msg_type=msg_type,
                payload={
                    'foo': 'bar'
                }
            ))

            self.provider.save_user_notification(UserNotification(
                user_id=self.test_user_id,
                msg=msg
            ))

        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1',
                }
            ),
            10
        )

    def _setup_user_notifications(self):
        """
        Helper to build out some
        """

        msg_type = self._save_notification_type()

        # set up some notifications

        msg1 = self.provider.save_notification_message(NotificationMessage(
            namespace='namespace1',
            msg_type=msg_type,
            payload={
                'foo': 'bar',
                'one': 1,
                'none': None,
                'datetime': datetime.utcnow(),
                'iso8601-fakeout': '--T::',  # something to throw off the iso8601 parser heuristic
            }
        ))

        map1 = self.provider.save_user_notification(UserNotification(
            user_id=self.test_user_id,
            msg=msg1
        ))

        msg_type2 = self.provider.save_notification_type(
            NotificationType(
                name='foo.bar.another',
                renderer='foo.renderer',
            )
        )

        msg2 = self.provider.save_notification_message(NotificationMessage(
            namespace='namespace2',
            msg_type=msg_type2,
            payload={
                'foo': 'baz',
                'one': 1,
                'none': None,
                'datetime': datetime.utcnow(),
                'iso8601-fakeout': '--T::',  # something to throw off the iso8601 parser heuristic
            }
        ))

        map2 = self.provider.save_user_notification(UserNotification(
            user_id=self.test_user_id,
            msg=msg2
        ))

        return map1, msg1, map2, msg2

    def test_get_notifications_for_user(self):
        """
        Test retrieving notifications for a user
        """

        # set up some notifications

        map1, msg1, map2, msg2 = self._setup_user_notifications()

        # read back and compare the notifications
        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(self.test_user_id)

            # most recent one should be first
            self.assertEqual(notifications[0].msg, msg2)
            self.assertEqual(notifications[1].msg, msg1)

        #
        # test file namespace filtering
        #
        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1',
                }
            ),
            1
        )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1'
                }
            )

            self.assertEqual(notifications[0].msg, msg1)

        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace2'
                }
            ),
            1
        )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace2'
                }
            )

            self.assertEqual(notifications[0].msg, msg2)

        #
        # test read filtering, should be none right now
        #
        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'read': True,
                    'unread': False
                }
            ),
            0
        )

        # if you ask for both not read and not unread, that should be a ValueError as that
        # combination makes no sense
        with self.assertRaises(ValueError):
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'read': False,
                    'unread': False
                }
            )

        # test for filtering by msg_type
        with self.assertNumQueries(1):
            self.assertEqual(
                self.provider.get_num_notifications_for_user(
                    self.test_user_id,
                    filters={
                        'type_name': msg1.msg_type.name
                    }
                ),
                1
            )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                filters={
                    'type_name': msg1.msg_type.name
                }
            )

            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0].msg, msg1)

        # test with msg_type and namespace combos
        with self.assertNumQueries(1):
            self.assertEqual(
                self.provider.get_num_notifications_for_user(
                    self.test_user_id,
                    filters={
                        'namespace': 'does-not-exist',
                        'type_name': msg1.msg_type.name
                    }
                ),
                0
            )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'does-not-exist',
                    'type_name': msg1.msg_type.name
                }
            )
            self.assertEqual(len(notifications), 0)

    def test_bad_user_map_update(self):
        """
        Test exception when trying to update a non-existing
        ID
        """

        # set up some notifications
        map1, __, __, __ = self._setup_user_notifications()

        with self.assertRaises(ItemNotFoundError):
            map1.id = -1
            self.provider.save_user_notification(map1)

    def test_read_unread_flags(self):
        """
        Test read/unread falgs
        """

        # set up some notifications
        map1, msg1, map2, msg2 = self._setup_user_notifications()

        # mark one as read
        map1.read_at = datetime.utcnow()

        # Not sure I understand why Django ORM is making 3 calls here
        # seems like it should just be 2. I might investigate more
        # later, but writes are less of a priority as this
        # will be read intensive
        with self.assertNumQueries(3):
            self.provider.save_user_notification(map1)

        # there should be one read notification
        with self.assertNumQueries(1):
            self.assertEqual(
                self.provider.get_num_notifications_for_user(
                    self.test_user_id,
                    filters={
                        'read': True,
                        'unread': False
                    }
                ),
                1
            )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                filters={
                    'read': True,
                    'unread': False
                }
            )
            self.assertEqual(notifications[0].msg, msg1)

        # there should be one unread notification
        with self.assertNumQueries(1):
            self.assertEqual(
                self.provider.get_num_notifications_for_user(
                    self.test_user_id,
                    filters={
                        'read': False,
                        'unread': True
                    }
                ),
                1
            )

        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                filters={
                    'read': False,
                    'unread': True
                }
            )
            self.assertEqual(notifications[0].msg, msg2)

    def test_get_notifications_paging(self):
        """
        Test retrieving notifications for a user
        """

        # make sure we can't pass along a huge limit size
        with self.assertRaises(ValueError):
            self.provider.get_notifications_for_user(
                self.test_user_id,
                options={
                    'limit': const.MAX_NOTIFICATION_LIST_SIZE + 1
                }
            )

        # set up some notifications
        map1, msg1, map2, msg2 = self._setup_user_notifications()

        # test limit, we should only get the first one
        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                options={
                    'limit': 1,
                }
            )

            self.assertEqual(len(notifications), 1)
            # most recent one should be first
            self.assertEqual(notifications[0].msg, msg2)

        # test limit with offset, we should only get the 2nd one
        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                options={
                    'limit': 1,
                    'offset': 1,
                }
            )

            self.assertEqual(len(notifications), 1)
            # most recent one should be first, so msg1 should be 2nd
            self.assertEqual(notifications[0].msg, msg1)

        # test that limit should be able to exceed bounds
        with self.assertNumQueries(1):
            notifications = self.provider.get_notifications_for_user(
                self.test_user_id,
                options={
                    'offset': 1,
                    'limit': 2,
                }
            )

            self.assertEqual(len(notifications), 1)
            # most recent one should be first, so msg1 should be 2nd
            self.assertEqual(notifications[0].msg, msg1)
