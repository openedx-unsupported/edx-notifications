"""
Test for Mongdodb indexes.
"""

from django.test import TestCase
from pymongo import MongoClient
from mock import patch
import edx_notifications


from edx_notifications.management.commands import create_mongodb_indexes

TEST_NOTIFICATION_STORE_PROVIDER = {
    "class": "edx_notifications.stores.mongo.store_provider.MongoNotificationStoreProvider",
    "options": {
        'host': 'localhost',
        'port': 27017,
        'database_name': 'test_notifications'
    }
}


class MongoDbIndexesTests(TestCase):
    """
    Test suite for the management command
    """

    # @override_settings(NOTIFICATION_STORE_PROVIDER=TEST_NOTIFICATION_STORE_PROVIDER)
    # def setUp(self):
    #     super(MongoDbIndexesTests, self).setUp()

    def test_create_indexes(self):
        """
        Invoke the Management Command
        """

        collection = MongoClient("localhost", 27017)["test_notifications"].user_notification

        collection.drop_indexes()

        created_index_names = str(collection.index_information().keys())
        self.assertNotIn('user msg id index', created_index_names)
        self.assertNotIn('user msg read_at index', created_index_names)
        self.assertNotIn('user_id index', created_index_names)
        self.assertNotIn('user msg msg_id->read_at compound_index', created_index_names)

        with patch('django.conf.settings.NOTIFICATION_STORE_PROVIDER', TEST_NOTIFICATION_STORE_PROVIDER):
            edx_notifications.stores.store._STORE_PROVIDER = None
            create_mongodb_indexes.Command().handle()
            edx_notifications.stores.store._STORE_PROVIDER = None

        created_index_names = str(collection.index_information().keys())
        self.assertIn('user msg id index', created_index_names)
        self.assertIn('user msg read_at index', created_index_names)
        self.assertIn('user_id index', created_index_names)
        self.assertIn('user msg msg_id->read_at compound_index', created_index_names)

    def test_create_indexes_with_out_mongodb_store_provider(self):
        """
        Invoke the Management Command
        """

        collection = MongoClient("localhost", 27017)["test_notifications"].user_notification

        collection.drop_indexes()

        created_index_names = str(collection.index_information().keys())
        self.assertNotIn('user msg id index', created_index_names)
        self.assertNotIn('user msg read_at index', created_index_names)
        self.assertNotIn('user_id index', created_index_names)
        self.assertNotIn('user msg msg_id->read_at compound_index', created_index_names)

        create_mongodb_indexes.Command().handle()

        created_index_names = str(collection.index_information().keys())
        self.assertNotIn('user msg id index', created_index_names)
        self.assertNotIn('user msg read_at index', created_index_names)
        self.assertNotIn('user_id index', created_index_names)
