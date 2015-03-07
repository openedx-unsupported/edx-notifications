"""
Unit tests to exercise code implemented in data.py
"""

from django.test import TestCase

from django.core.exceptions import ValidationError

from edx_notifications.data import (
    NotificationMessage,
)


class DataTests(TestCase):
    """
    Go through data.py and exercise some tests
    """

    def test_message_validation(self):
        """
        Make sure validation of NotificationMessage is correct
        """

        msg = NotificationMessage()  # intentionally blank

        with self.assertRaises(ValidationError):
            msg.validate()

    def test_cloning(self):
        """
        Make sure cloning works
        """

        msg = NotificationMessage(
            payload={'foo': 'bar'}
        )

        clone = NotificationMessage.clone(msg)

        self.assertEqual(msg, clone)

        # now change the cloned payload and assert that the original one
        # did not change

        clone.payload['foo'] = 'changed'
        self.assertEqual(msg.payload['foo'], 'bar')
        self.assertEqual(clone.payload['foo'], 'changed')
