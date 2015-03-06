"""
Tests for the publisher.py and consumer.py methods
"""

from django.test import TestCase
from contracts import ContractNotRespected
from django.contrib.auth.models import User

from edx_notifications import const
from edx_notifications.lib.publisher import (
    publish_notification_to_user,
    bulk_publish_notification_to_users,
    register_notification_type,
)

from edx_notifications.lib.consumer import (
    get_notifications_count_for_user,
    get_notifications_for_user,
    mark_notification_read,
    mark_all_user_notification_as_read
)

from edx_notifications.data import (
    NotificationMessage,
    NotificationType,
    UserNotification,
)

from edx_notifications.exceptions import (
    ItemNotFoundError,
)

from edx_notifications.renderers.renderer import (
    clear_renderers
)


class TestPublisherLibrary(TestCase):
    """
    Go through exposed endpoints in the publisher library
    """

    def setUp(self):
        """
        Initialize some data
        """

        clear_renderers()

        self.test_user_id = 1001  # some bogus user identifier
        self.msg_type = NotificationType(
            name='open-edx.edx_notifications.lib.tests.test_publisher',
            renderer='edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
        )
        register_notification_type(self.msg_type)

    def test_multiple_types(self):
        """
        Make sure the same type can be registered more than once
        """

        # msg_type.name is a primary key, so verify this does
        # not throw an exception
        register_notification_type(self.msg_type)

    def test_publish_notification(self):
        """
        Go through and set up a notification and publish it
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        # make sure it asserts that user_id is an integer
        with self.assertRaises(ContractNotRespected):
            publish_notification_to_user('bad-id', msg)

        # now do happy path
        sent_user_msg = publish_notification_to_user(self.test_user_id, msg)

        # make sure type checking is happening
        with self.assertRaises(ContractNotRespected):
            get_notifications_count_for_user('bad-type')

        # now query back the notification to make sure it got stored
        # and we can retrieve it

        self.assertEquals(
            get_notifications_count_for_user(self.test_user_id),
            1
        )

        # make sure it asserts that user_id is an integer
        with self.assertRaises(ContractNotRespected):
            get_notifications_for_user('bad-id')

        notifications = get_notifications_for_user(self.test_user_id)

        self.assertTrue(isinstance(notifications, list))
        self.assertEqual(len(notifications), 1)
        self.assertTrue(isinstance(notifications[0], UserNotification))

        read_user_msg = notifications[0]
        self.assertEqual(read_user_msg.user_id, self.test_user_id)
        self.assertIsNone(read_user_msg.read_at)  # should be unread

        self.assertEqual(read_user_msg, sent_user_msg)
        self.assertEqual(read_user_msg.msg, sent_user_msg.msg)

    def test_bulk_publish_list(self):
        """
        Make sure we can bulk publish to a number of users
        passing in a list
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        # now send to more than our internal chunking size
        bulk_publish_notification_to_users(
            [user_id for user_id in range(1, const.MAX_BULK_USER_NOTIFICATION_SIZE * 2 + 1)],
            msg
        )

        # now read them all back
        for user_id in range(1, const.MAX_BULK_USER_NOTIFICATION_SIZE * 2 + 1):
            notifications = get_notifications_for_user(user_id)

            self.assertTrue(isinstance(notifications, list))
            self.assertEqual(len(notifications), 1)
            self.assertTrue(isinstance(notifications[0], UserNotification))

    def test_bulk_publish_list_exclude(self):
        """
        Make sure we can bulk publish to a number of users
        passing in a list, and also pass in an exclusion list to
        make sure the people in the exclude list does not get
        the notification
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        user_ids = [user_id for user_id in range(1, const.MAX_BULK_USER_NOTIFICATION_SIZE * 2 + 1, 2)]
        exclude_user_ids = [user_id for user_id in range(1, const.MAX_BULK_USER_NOTIFICATION_SIZE * 2 + 1)]

        # now send to more than our internal chunking size
        bulk_publish_notification_to_users(
            user_ids,
            msg,
            exclude_user_ids=exclude_user_ids
        )

        # now read them all back
        for user_id in range(1, const.MAX_BULK_USER_NOTIFICATION_SIZE * 2 + 1):
            notifications = get_notifications_for_user(user_id)

            self.assertTrue(isinstance(notifications, list))
            self.assertEqual(len(notifications), 1 if user_id not in exclude_user_ids else 0)
            if user_id not in exclude_user_ids:
                self.assertTrue(isinstance(notifications[0], UserNotification))

    def test_bulk_publish_generator(self):
        """
        Make sure we can bulk publish to a number of users
        passing in a generator function
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        def _user_id_generator():
            """
            Just spit our an generator that goes from 1 to 100
            """
            for user_id in range(1, 100):
                yield user_id

        # now send to more than our internal chunking size
        bulk_publish_notification_to_users(
            _user_id_generator(),
            msg
        )

        # now read them all back
        for user_id in range(1, 100):
            notifications = get_notifications_for_user(user_id)

            self.assertTrue(isinstance(notifications, list))
            self.assertEqual(len(notifications), 1)
            self.assertTrue(isinstance(notifications[0], UserNotification))

    def test_bulk_publish_orm_query(self):
        """
        Make sure we can bulk publish to a number of users
        passing in a resultset from a Django ORM query
        """

        # set up some test users in Django User's model
        User(username='tester1').save()
        User(username='tester2').save()
        User(username='tester3').save()

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        resultset = User.objects.values_list('id', flat=True).all()

        num_sent = bulk_publish_notification_to_users(
            resultset,
            msg
        )

        # make sure we sent 3
        self.assertEqual(num_sent, 3)

        # now read them back
        for user in User.objects.all():
            notifications = get_notifications_for_user(user.id)

            self.assertTrue(isinstance(notifications, list))
            self.assertEqual(len(notifications), 1)
            self.assertTrue(isinstance(notifications[0], UserNotification))

    def test_mark_all_as_read(self):
        """
        Verify proper behavior when marking user notifications as read/unread
        """
        for __ in range(10):
            msg = NotificationMessage(
                namespace='test-runner',
                msg_type=self.msg_type,
                payload={
                    'foo': 'bar'
                }
            )
            publish_notification_to_user(self.test_user_id, msg)

        # make sure we have 10 unreads before we do anything else
        self.assertEquals(
            get_notifications_count_for_user(
                self.test_user_id,
                filters={
                    'read': False,
                    'unread': True,
                },
            ),
            10
        )

        # now mark msg as read by this user
        mark_all_user_notification_as_read(self.test_user_id)

        # shouldn't be counted in unread counts
        self.assertEquals(
            get_notifications_count_for_user(
                self.test_user_id,
                filters={
                    'read': False,
                    'unread': True,
                },
            ),
            0
        )

        # Should be counted in read counts
        self.assertEquals(
            get_notifications_count_for_user(
                self.test_user_id,
                filters={
                    'read': True,
                    'unread': False,
                },
            ),
            10
        )

    def test_marking_read_state(self):
        """
        Verify proper behavior when marking notfications as read/unread
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        # now do happy path
        sent_user_msg = publish_notification_to_user(self.test_user_id, msg)

        # now mark msg as read by this user
        mark_notification_read(self.test_user_id, sent_user_msg.msg.id)

        # shouldn't be counted in unread counts
        self.assertEquals(
            get_notifications_count_for_user(
                self.test_user_id,
                filters={
                    'read': False,
                    'unread': True,
                },
            ),
            0
        )

        # Should be counted in read counts
        self.assertEquals(
            get_notifications_count_for_user(
                self.test_user_id,
                filters={
                    'read': True,
                    'unread': False,
                },
            ),
            1
        )

        # now mark msg as unread by this user
        mark_notification_read(self.test_user_id, sent_user_msg.msg.id, read=False)

        # Should be counted in unread counts
        self.assertEquals(
            get_notifications_count_for_user(
                self.test_user_id,
                filters={
                    'read': False,
                    'unread': True,
                },
            ),
            1
        )

        # Shouldn't be counted in read counts
        self.assertEquals(
            get_notifications_count_for_user(
                self.test_user_id,
                filters={
                    'read': True,
                    'unread': False,
                },
            ),
            0
        )

    def test_marking_invalid_msg_read(self):
        """
        Makes sure that we can't mark an invalid notification, e.g. someone elses
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        # publish that
        sent_user_msg = publish_notification_to_user(self.test_user_id, msg)

        with self.assertRaises(ItemNotFoundError):
            # this user doesn't have this notification!
            mark_notification_read(100, sent_user_msg.msg.id)
