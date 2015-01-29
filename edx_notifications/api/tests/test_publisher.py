"""
Tests for the publisher.py file
"""

from django.test import TestCase

from edx_notifications.api.publisher import (
    publish_notification_to_user,
    register_notification_type
)

from edx_notifications.data import (
    NotificationMessage,
    NotificationType
)


class TestPublisherLibrary(TestCase):
    """
    Go through exposed endpoints in the publisher library
    """

    def setUp(self):
        """
        Initialize some data
        """

        self.user_id = 1001  # some bogus user identifier
        self.msg_type = NotificationType(
            name='open-edx.edx_notifications.api.tests.test_publisher'
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
        with self.assertRaises(TypeError):
            publish_notification_to_user('bad-id', msg)

        # now do happy path
        publish_notification_to_user(self.user_id, msg)
