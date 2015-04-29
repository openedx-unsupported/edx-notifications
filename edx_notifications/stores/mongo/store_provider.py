import datetime
import pymongo
from pymongo import MongoClient
import pytz
from edx_notifications import const
from edx_notifications.exceptions import BulkOperationTooLarge
from edx_notifications.stores.mongo.mongo_models import MongoUserNotification
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider


class MongoNotificationStoreProvider(SQLNotificationStoreProvider):
    """

    """

    def __init__(self, **kwargs):
        super(MongoNotificationStoreProvider, self).__init__(**kwargs)
        self.client = MongoClient(kwargs.get('host'), kwargs.get('port'))
        self.db = self.client[kwargs.get('database_name')]
        self.collection = self.db.user_notification
        # self.bulk = self.collection.initializeUnorderedBulkOp()

    def _get_prepaged_notifications(self, user_id, filters=None, options=None):
        """
        Helper to set up the notifications query before paging
        is applied. WARNING: This should be used with care and to not
        iterate over this returned results set. Typically this
        will just be used to get a count()
        """

        _filters = filters if filters else {}
        _options = options if options else {}

        namespace = _filters.get('namespace')
        read = _filters.get('read', True)
        unread = _filters.get('unread', True)
        type_name = _filters.get('type_name')
        start_date = _filters.get('start_date')
        end_date = _filters.get('end_date')
        query_object = {'user_id': user_id}
        if not read and not unread:
            raise ValueError('Bad arg combination either read or unread must be set to True')

        if namespace:
            query_object.update({'user_notification.namespace': namespace})

        if not (read and unread):
            if read:
                query_object.update({'user_notification.read_at': {"$ne": None}})

            if unread:
                query_object.update({'user_notification.read_at': None})

        if type_name:
            query_object.update({'user_notification.msg_type_name': type_name})

        if start_date:
            query_object.update({'created': {"gte": start_date}})

        if end_date:
            query_object.update({'created': {"lte": end_date}})

        collection = self.collection.find(query_object)
        return list(collection)

    def get_notifications_for_user(self, user_id, filters=None, options=None):
        """

        :param user_id:
        :param filters:
        :param options:
        :return:
        """
        user_notifications = self._get_prepaged_notifications(user_id, filters, options)[0]

        result_set = [MongoUserNotification.to_data_object(item, user_id) for item in user_notifications['user_notification']]

        return result_set

    def mark_user_notifications_read(self, user_id, filters=None):
        pass

    def get_num_notifications_for_user(self, user_id, filters=None):
        return len(self._get_prepaged_notifications(user_id, filters)[0]['user_notification'])

    def purge_expired_notifications(self, purge_read_messages_older_than, purge_unread_messages_older_than):
        pass

    def bulk_create_user_notification(self, user_msgs):
        """
        This is an optimization for bulk creating *new* UserNotification
        objects in the mongodb . Since we want to support fan-outs of messages,
        we may need to insert 10,000's (or 100,000's) of objects as optimized
        as possible.

        NOTE: This method cannot update existing UserNotifications, only create them.
        NOTE: It is assumed that user_msgs is already chunked in an appropriate size.
        """
        if len(user_msgs) > const.NOTIFICATION_BULK_PUBLISH_CHUNK_SIZE:
            msg = (
                'You have passed in a user_msgs list of size {length} but the size '
                'limit is {max}.'.format(length=len(user_msgs), max=const.NOTIFICATION_BULK_PUBLISH_CHUNK_SIZE)
            )
            raise BulkOperationTooLarge(msg)

    def get_notification_for_user(self, user_id, msg_id):
        collection = self.collection.find({
            'user_id': user_id,
            'user_notification.msg_id': msg_id
        })
        return list(collection)

    def save_user_notification(self, user_msg):
        """
        Create or Update the mapping of a user to a notification.
        """

        user_notification = self.collection.update(
            {
                'user_id': user_msg.user_id,
            },
            {
                '$set': {'user_id': user_msg.user_id},
                '$push': {
                    'user_notification': {
                        '$each':
                        [{
                            'msg_id': user_msg.msg.id,
                            'msg_type_name': user_msg.msg.msg_type.name,
                            'namespace': user_msg.msg.namespace,
                            'created': datetime.datetime.now(pytz.UTC),
                            'modified': datetime.datetime.now(pytz.UTC),
                            'user_context': user_msg.user_context if user_msg.user_context else None,
                            'read_at': user_msg.read_at if user_msg.read_at else None
                        }]
                    }
                }
            },
            upsert=True
        )
        return list(user_notification)
