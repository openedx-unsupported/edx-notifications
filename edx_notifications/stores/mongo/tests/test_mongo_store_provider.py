"""
Tests which exercise the MySQL test_data_provider
"""

from freezegun import freeze_time
import mock
import pytz
from datetime import datetime, timedelta

from django.test import TestCase
from edx_notifications.stores.mongo.store_provider import MongoNotificationStoreProvider
from edx_notifications.stores.sql.models import SQLUserNotification

from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider
from edx_notifications.data import (
    NotificationMessage,
    NotificationType,
    UserNotification,
    NotificationCallbackTimer
)
from edx_notifications.exceptions import (
    ItemNotFoundError,
    BulkOperationTooLarge
)
from edx_notifications import const


class TestMongoStoreProvider(TestCase):
    """
    This class exercises some of the implementation methods for the
    abstract DataProvider class
    """
    def tearDown(self):
        self.provider.collection.remove()

    def setUp(self):
        """
        Setup the test case
        """
        self.provider = MongoNotificationStoreProvider(
            host='localhost',
            port=27017,
            database_name='test_notifications'
        )
        self.test_user_id = 1

    def _save_notification_type(self):
        """
        Helper to set up a notification_type
        """

        notification_type = NotificationType(
            name='foo.bar.baz',
            renderer='foo.renderer',
            renderer_context={
                'param1': 'value1'
            },
        )

        result = self.provider.save_notification_type(notification_type)

        return result

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
            },
            resolve_links={
                'param1': 'value1'
            },
            object_id='foo-item'
        )

        result = self.provider.save_notification_message(msg)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result.id)
        return result

    def test_save_notification(self):
        """
        Test saving a single notification message
        """

        self._save_new_notification()

    def test_mark_user_notification_read(self):
        """

        """
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
        self.provider.mark_user_notifications_read(self.test_user_id)

        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1',
                    'read': False
                }
            ),
            0
        )

    def test_mark_read_namespaced(self):
        """

        """

        msg_type = self._save_notification_type()

        def _gen_notifications(count, namespace):
            """
            Helper to generate notifications
            """
            for __ in range(count):
                msg = self.provider.save_notification_message(NotificationMessage(
                    namespace=namespace,
                    msg_type=msg_type,
                    payload={
                        'foo': 'bar'
                    }
                ))

                self.provider.save_user_notification(UserNotification(
                    user_id=self.test_user_id,
                    msg=msg
                ))

        _gen_notifications(5, 'namespace1')
        _gen_notifications(5, 'namespace2')

        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1',
                }
            ),
            5
        )

        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace2',
                }
            ),
            5
        )

        # just mark notifications in namespace1
        # as read
        self.provider.mark_user_notifications_read(
            self.test_user_id,
            filters={
                'namespace': 'namespace1'
            }
        )

        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1',
                    'read': False
                }
            ),
            0
        )

        # namespace2's message should still be there
        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace2',
                    'read': False
                }
            ),
            5
        )

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
        self.assertEqual(msg.resolve_links, fetched_msg.resolve_links)
        self.assertEqual(msg.object_id, fetched_msg.object_id)

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

        self.assertEqual(
            self.provider.get_num_notifications_for_user(self.test_user_id),
            0
        )

        self.assertFalse(
            self.provider.get_notifications_for_user(self.test_user_id)
        )

    @mock.patch('edx_notifications.const.NOTIFICATION_MAX_LIST_SIZE', 1)
    def test_over_limit_counting(self):
        """
        Verifies that our counting operations will work as expected even when
        our count is greater that the NOTIFICATION_MAX_LIST_SIZE which is
        the maximum page size
        """

        self.assertEqual(const.NOTIFICATION_MAX_LIST_SIZE, 1)

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
        map1 = self.provider.get_notification_for_user(user_id=self.test_user_id, msg_id=msg1.id)

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
        map1 = self.provider.get_notification_for_user(user_id=self.test_user_id, msg_id=msg2.id)
        return map1, msg1, map2, msg2

    def test_get_notifications_for_user(self):
        """
        Test retrieving notifications for a user
        """

        # set up some notifications

        map1, msg1, map2, msg2 = self._setup_user_notifications()

        # read back and compare the notifications

        notifications = self.provider.get_notifications_for_user(self.test_user_id)

        self.assertEqual(notifications[0].msg, msg1)
        self.assertEqual(notifications[1].msg, msg2)

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

        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'type_name': msg1.msg_type.name
                }
            ),
            1
        )

        notifications = self.provider.get_notifications_for_user(
            self.test_user_id,
            filters={
                'type_name': msg1.msg_type.name
            }
        )

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].msg, msg1)

        # test with msg_type and namespace combos

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

        notifications = self.provider.get_notifications_for_user(
            self.test_user_id,
            filters={
                'namespace': 'does-not-exist',
                'type_name': msg1.msg_type.name
            }
        )
        self.assertEqual(len(notifications), 0)

        # #
        # # test start_date and end_date filtering.
        # #
        #
        # self.assertEqual(
        #     self.provider.get_num_notifications_for_user(
        #         self.test_user_id,
        #         filters={
        #             'start_date': msg1.created,
        #             'end_date': msg2.created + timedelta(days=1)
        #         }
        #     ),
        #     2
        # )

        # filters by end_date
        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'start_date': msg1.created + timedelta(days=1),
                    'end_date': msg1.created + timedelta(days=-1)
                }
            ),
            0
        )

        # # filters by end_date
        # self.assertEqual(
        #     self.provider.get_num_notifications_for_user(
        #         self.test_user_id,
        #         filters={
        #             'end_date': msg2.created + timedelta(days=1)
        #         }
        #     ),
        #     2
        # )

        # notifications = self.provider.get_notifications_for_user(
        #     self.test_user_id,
        #     filters={
        #         'start_date': msg1.created,
        #         'end_date': msg2.created + timedelta(days=1)
        #     }
        # )
        # self.assertEqual(len(notifications), 2)
        # self.assertEqual(notifications[0].msg, msg2)
        # self.assertEqual(notifications[1].msg, msg1)

        # update the created time for msg2 data object.
        # user_msg = SQLUserNotification.objects.get(msg_id=msg2.id)
        # user_msg.created = msg2.created - timedelta(days=1)
        # user_msg.save()
        #
        # # now the msg 2 should not be in the filtered_list
        # self.assertEqual(
        #     self.provider.get_num_notifications_for_user(
        #         self.test_user_id,
        #         filters={
        #             'start_date': msg1.created,
        #             'end_date': datetime.now(pytz.UTC) + timedelta(days=1)
        #         }
        #     ),
        #     1
        # )
        #
        # self.assertEqual(
        #     self.provider.get_num_notifications_for_user(
        #         self.test_user_id,
        #         filters={
        #             'start_date': msg1.created
        #         }
        #     ),
        #     1
        # )
        #
        # self.assertEqual(
        #     self.provider.get_num_notifications_for_user(
        #         self.test_user_id,
        #         filters={
        #             'end_date': user_msg.created - timedelta(days=1)
        #         }
        #     ),
        #     0
        # )

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

        self.provider.save_user_notification(map1)

        # there should be one read notification
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

        notifications = self.provider.get_notifications_for_user(
            self.test_user_id,
            filters={
                'read': True,
                'unread': False
            }
        )

        # there should be one unread notification
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

        notifications = self.provider.get_notifications_for_user(
            self.test_user_id,
            filters={
                'read': False,
                'unread': True
            }
        )
        self.assertEqual(notifications[0].msg, msg1)

    def test_get_notifications_paging(self):
        """
        Test retrieving notifications for a user
        """

        # make sure we can't pass along a huge limit size
        with self.assertRaises(ValueError):
            self.provider.get_notifications_for_user(
                self.test_user_id,
                options={
                    'limit': const.NOTIFICATION_MAX_LIST_SIZE + 1
                }
            )

        # set up some notifications
        map1, msg1, map2, msg2 = self._setup_user_notifications()

        notifications = self.provider.get_notifications_for_user(
            self.test_user_id,
            options={
                'limit': 1,
            }
        )

        self.assertEqual(len(notifications), 1)

        # test limit with offset, we should only get the 2nd one
        notifications = self.provider.get_notifications_for_user(
            self.test_user_id,
            options={
                'limit': 1,
                'offset': 1,
            }
        )

        self.assertEqual(len(notifications), 1)

        # test that limit should be able to exceed bounds

        notifications = self.provider.get_notifications_for_user(
            self.test_user_id,
            options={
                'offset': 1,
                'limit': 2,
            }
        )

        self.assertEqual(len(notifications), 1)

    def test_bulk_user_notification_create(self):
        """
        Test that we can create new UserNotifications using an optimized
        code path to minimize round trips to the database
        """
        msg_type = self._save_notification_type()

        # set up some notifications

        msg = self.provider.save_notification_message(NotificationMessage(
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

        user_msgs = []
        for user_id in range(const.NOTIFICATION_BULK_PUBLISH_CHUNK_SIZE):
            user_msgs.append(
                UserNotification(user_id=user_id, msg=msg)
            )

        # assert that this only takes one round-trip to the database
        # to insert all of them

        self.provider.bulk_create_user_notification(user_msgs)

        # now make sure that we can query each one
        for user_id in range(const.NOTIFICATION_BULK_PUBLISH_CHUNK_SIZE):
            notifications = self.provider.get_notifications_for_user(user_id)

            self.assertEqual(len(notifications), 1)
            self.assertEqual(notifications[0].msg, msg)

        # now test if we send in a size too large that an exception is raised
        user_msgs.append(
            UserNotification(user_id=user_id, msg=msg)
        )

        with self.assertRaises(BulkOperationTooLarge):
            self.provider.bulk_create_user_notification(user_msgs)
