"""
Tests for the publisher.py and consumer.py methods
"""

from django.test import TestCase
from contracts import ContractNotRespected

from edx_notifications.lib.publisher import (
    publish_notification_to_user,
    register_notification_type
)

from edx_notifications.lib.consumer import (
    get_notifications_count_for_user,
    get_notifications_for_user,
    mark_notification_read
)

from edx_notifications.data import (
    NotificationMessage,
    NotificationType,
    UserNotification,
)

from edx_notifications.exceptions import (
    ItemNotFoundError,
)


class TestPublisherLibrary(TestCase):
    """
    Go through exposed endpoints in the publisher library
    """

    def setUp(self):
        """
        Initialize some data
        """

        self.test_user_id = 1001  # some bogus user identifier
        self.msg_type = NotificationType(
            name='open-edx.edx_notifications.lib.tests.test_publisher'
        )
        register_notification_type(self.msg_type)

    def test_multiple_type_registrations(self):
        """
        Make sure the same type can be registered more than once
        """

        # msg_type.name is a primary key, so verify this does
        # not throw an exception
        register_notification_type(self.msg_type)

    def test_publish_notification_to_user(self):
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
        sent_user_map = publish_notification_to_user(self.test_user_id, msg)

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

        read_user_map = notifications[0]
        self.assertEqual(read_user_map.user_id, self.test_user_id)
        self.assertIsNone(read_user_map.read_at)  # should be unread

        # print 'read_user_map = {}'.format(read_user_map)
        # print 'sent_user_map = {}'.format(sent_user_map)

        self.assertEqual(read_user_map, sent_user_map)
        self.assertEqual(read_user_map.msg, sent_user_map.msg)

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
        sent_user_map = publish_notification_to_user(self.test_user_id, msg)

        # now mark msg as read by this user
        mark_notification_read(self.test_user_id, sent_user_map.msg.id)

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
        mark_notification_read(self.test_user_id, sent_user_map.msg.id, read=False)

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

    def test_marking_invalid_msg_as_read(self):
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
        sent_user_map = publish_notification_to_user(self.test_user_id, msg)

        with self.assertRaises(ItemNotFoundError):
            # this user doesn't have this notification!
            mark_notification_read(100, sent_user_map.msg.id)
