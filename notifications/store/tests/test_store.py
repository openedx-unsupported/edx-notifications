"""
Exercises tests on the base_store_provider file
"""

from django.test import TestCase

from notifications.store.store import BaseNotificationStoreProvider


class TestBaseNotificationDataProvider(TestCase):
    """
    Cover the NotificationDataProviderBase class
    """

    def test_cannot_create_instance(self):
        """
        NotificationDataProviderBase is an abstract class and we should not be able
        to create an instance of it
        """

        with self.assertRaises(TypeError):
            BaseNotificationStoreProvider()
