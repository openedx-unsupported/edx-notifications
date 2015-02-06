"""
Exercises tests on the base_store_provider file
"""

from django.test import TestCase
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured

from edx_notifications.stores.store import (
    BaseNotificationStoreProvider,
    notification_store,
    reset_notification_store
)
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider


TEST_NOTIFICATION_STORE_PROVIDER = {
    "class": "edx_notifications.stores.sql.store_provider.SQLNotificationStoreProvider",
    "options": {
    }
}


class BadImplementationStoreProvider(BaseNotificationStoreProvider):
    """
    Test implementation of StoreProvider to assert that non-implementations of methods
    raises the correct methods
    """

    def get_notification_message_by_id(self, msg_id, options=None):
        """
        Fake implementation of method which calls base class, which should throw NotImplementedError
        """
        super(BadImplementationStoreProvider, self).get_notification_message_by_id(msg_id, options=options)

    def save_notification_message(self, msg):
        """
        Fake implementation of method which calls base class, which should throw NotImplementedError
        """
        super(BadImplementationStoreProvider, self).save_notification_message(msg)

    def save_user_notification(self, user_map):
        """
        Fake implementation of method which calls base class, which should throw NotImplementedError
        """
        super(BadImplementationStoreProvider, self).save_user_notification(user_map)

    def get_notification_type(self, name):
        """
        Fake implementation of method which calls base class, which should throw NotImplementedError
        """
        super(BadImplementationStoreProvider, self).get_notification_type(name)

    def save_notification_type(self, msg_type):
        """
        Saves a new notification type, note that we do not support updates
        """
        super(BadImplementationStoreProvider, self).save_notification_type(msg_type)

    def get_num_notifications_for_user(self, user_id, filters=None):
        """
        Saves a new notification type, note that we do not support updates
        """
        super(BadImplementationStoreProvider, self).get_num_notifications_for_user(user_id, filters=filters)

    def get_notifications_for_user(self, user_id, filters=None, options=None):
        """
        Saves a new notification type, note that we do not support updates
        """
        super(BadImplementationStoreProvider, self).get_notifications_for_user(
            user_id,
            filters=filters,
            options=options
        )


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

    def test_base_methods_exceptions(self):
        """
        Asserts that all base-methods on the StoreProvider interface will throw
        an NotImplementedError
        """

        bad_provider = BadImplementationStoreProvider()

        with self.assertRaises(NotImplementedError):
            bad_provider.get_notification_message_by_id(None)

        with self.assertRaises(NotImplementedError):
            bad_provider.save_notification_message(None)

        with self.assertRaises(NotImplementedError):
            bad_provider.save_user_notification(None)

        with self.assertRaises(NotImplementedError):
            bad_provider.get_notification_type(None)

        with self.assertRaises(NotImplementedError):
            bad_provider.save_notification_type(None)

        with self.assertRaises(NotImplementedError):
            bad_provider.get_num_notifications_for_user(None)

        with self.assertRaises(NotImplementedError):
            bad_provider.get_notifications_for_user(None)
