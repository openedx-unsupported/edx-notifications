"""
Unit tests to exercise code implemented in data.py
"""

from django.test import TestCase

from django.core.exceptions import ValidationError

from edx_notifications.data import (  # pylint: disable=unused-import
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
