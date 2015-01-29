"""
Exercises tests on the base_store_provider file
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured

from edx_notifications.store.store import (
    BaseNotificationStoreProvider,
    notification_store,
    reset_notification_store
)
from edx_notifications.store.sql.store_provider import SQLNotificationStoreProvider


TEST_NOTIFICATION_STORE_PROVIDER = {
    "class": "edx_notifications.store.sql.store_provider.SQLNotificationStoreProvider",
    "options": {
    }
}


class TestBaseNotificationDataProvider(TestCase):
    """
    Cover the NotificationDataProviderBase class
    """

    def setUp(self):
        """
        Harnessing
        """
        reset_notification_store()

    def test_cannot_create_instance(self):
        """
        NotificationDataProviderBase is an abstract class and we should not be able
        to create an instance of it
        """

        with self.assertRaises(TypeError):
            BaseNotificationStoreProvider()  # pylint: disable=abstract-class-instantiated

    @override_settings(NOTIFICATION_STORE_PROVIDER=TEST_NOTIFICATION_STORE_PROVIDER)
    def test_get_provider(self):
        """
        Makes sure we get an instance of the registered store provider
        """

        provider = notification_store()

        self.assertIsNotNone(provider)
        self.assertTrue(isinstance(provider, SQLNotificationStoreProvider))

    @override_settings(NOTIFICATION_STORE_PROVIDER=None)
    def test_missing_provider_config(self):
        """
        Make sure we are throwing exceptions on poor configuration
        """

        with self.assertRaises(ImproperlyConfigured):
            notification_store()

    @override_settings(NOTIFICATION_STORE_PROVIDER={"class": "foo"})
    def test_bad_provider_config(self):
        """
        Make sure we are throwing exceptions on poor configuration
        """

        with self.assertRaises(ImproperlyConfigured):
            notification_store()
