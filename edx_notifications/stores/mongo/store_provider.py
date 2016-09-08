"""
Concrete MongoDB implementation of the of the data provider abstract base class (interface)
"""
import copy
import datetime
from pymongo import MongoClient
import pymongo
import pytz
from edx_notifications import const
from edx_notifications.exceptions import BulkOperationTooLarge
from edx_notifications.stores.mongo.mongo_models import MongoUserNotification
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider


class MongoNotificationStoreProvider(SQLNotificationStoreProvider):
    """
    Concrete MongoDB implementation of the of the data provider abstract base class (interface)
    """

    def __init__(self, **kwargs):
        super(MongoNotificationStoreProvider, self).__init__(**kwargs)
        self.client = MongoClient(kwargs.get('host'), kwargs.get('port'))
        self.db_instance = self.client[kwargs.get('database_name')]
        self.collection = self.db_instance.user_notification

    def create_mongodb_indexes(self):
        """
        Ensure that all appropriate indexes are created that are needed by Notifications, or raise
        an exception if unable to.

        This method is intended for use by tests and administrative commands, and not
        to be run during server startup.
        """

        self.collection.ensure_index([("user_id", pymongo.ASCENDING)], name='user_id index')
        self.collection.ensure_index([("user_notification.msg_id", pymongo.ASCENDING)], name='user msg id index')
        self.collection.ensure_index([("user_notification.read_at", pymongo.ASCENDING)], name='user msg read_at index')
        self.collection.ensure_index(
            [("user_notification.msg_id", pymongo.ASCENDING), ("user_notification.read_at", pymongo.ASCENDING)],
            name='user msg msg_id->read_at compound_index')

    def _get_prepaged_notifications(self, user_id, filters=None, options=None):
        """
        Helper to set up the notifications query before paging
        is applied. WARNING: This should be used with care and to not
        iterate over this returned results set. Typically this
        will just be used to get a count()
        """

        _filters = filters if filters else {}

        namespace = _filters.get('namespace')
        read = _filters.get('read', True)
        unread = _filters.get('unread', True)
        type_name = _filters.get('type_name')
        created_after = _filters.get('created_after')
        created_before = _filters.get('created_before')
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

        if created_after:
            query_object.update({'user_notification.created': {"$gte": created_after}})

        if created_before:
            if 'user_notification.created' in query_object.keys():
                query_object['user_notification.created'].update({"$lte": created_before})
            else:
                query_object.update({'user_notification.created': {"$lte": created_before}})

        collection = self.collection.aggregate([
            {
                '$match': {'user_id': user_id}
            },
            {
                '$unwind': "$user_notification"
            },
            {
                '$match': query_object
            },
            {
                '$group': {'_id': "$user_id", 'user_notification': {'$addToSet': "$user_notification"}}
            }
        ])

        return list(collection['result'])

    def get_notifications_for_user(self, user_id, filters=None, options=None):
        """

        :param user_id
        :param filters:
        :param options:
        :return:
        """
        _options = options if options else {}

        limit = _options.get('limit', const.NOTIFICATION_MAX_LIST_SIZE)
        offset = _options.get('offset', 0)

        # make sure passed in limit is allowed
        # as we don't want to blow up the query too large here
        if limit > const.NOTIFICATION_MAX_LIST_SIZE:
            raise ValueError('Max limit is {limit}'.format(limit=limit))

        user_notification_result = self._get_prepaged_notifications(user_id, filters, options)
        user_notifications = []
        if len(user_notification_result) > 0:
            user_notifications = self._get_prepaged_notifications(user_id, filters, options)[0]

            user_notifications = user_notifications['user_notification'][offset: offset + limit]

        result_set = [MongoUserNotification.to_data_object(item, user_id) for item in user_notifications]
        return result_set

    def mark_user_notifications_read(self, user_id, filters=None):
        """
        Marks all the unread notifications as read.
        """
        _filters = copy.copy(filters) if filters else {}
        _filters.update({
            'read': False,
            'unread': True,
        })
        user_notification_result = self._get_prepaged_notifications(user_id, _filters)
        if len(user_notification_result) > 0:
            notifications = user_notification_result[0]['user_notification']
            self.collection.update({'user_id': user_id}, {'$pullAll': {'user_notification': notifications}})
            for notification in notifications:
                notification['read_at'] = datetime.datetime.now(pytz.UTC)
            self.collection.update({'user_id': user_id}, {'$pushAll': {'user_notification': notifications}})

    def get_num_notifications_for_user(self, user_id, filters=None):
        """
        Returns the count of a user's notifications after applying filters.
        """
        user_notifications_result = self._get_prepaged_notifications(user_id, filters)
        if len(user_notifications_result) > 0:
            return len(user_notifications_result[0]['user_notification'])
        else:
            return 0

    def purge_expired_notifications(self, purge_read_messages_older_than=None, purge_unread_messages_older_than=None):  # pylint: disable=invalid-name
        """
        Purges read and unread notifications older than specified dates.
        """
        if purge_read_messages_older_than is not None:
            self.collection.update(
                {},
                {
                    '$pull': {
                        'user_notification': {
                            'read_at': {"$ne": None},
                            'created': {"$lte": purge_read_messages_older_than}
                        }
                    }
                },
                multi=True
            )

        if purge_unread_messages_older_than is not None:
            self.collection.update(
                {},
                {
                    '$pull': {
                        'user_notification': {
                            'read_at': None,
                            'created': {"$lte": purge_unread_messages_older_than}
                        }
                    }
                },
                multi=True
            )

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

        for user_msg in user_msgs:
            self._create_new_user_notification(user_msg)

    def get_notification_for_user(self, user_id, msg_id):
        collection = self.collection.find({'user_id': user_id},
                                          {"user_notification": {"$elemMatch": {"msg_id": msg_id}}})
        user_notification = list(collection)[0]['user_notification'][0]
        result_set = MongoUserNotification.to_data_object(user_notification, user_id)
        return result_set

    def save_user_notification(self, user_msg):
        """
        Create or Update the mapping of a user to a notification.
        saves the user notifications in the following format in mongodb collection.
        {
            'user_id': user_id,
            'user_notification': [
                {
                    'msg_id': msg_id,
                    'msg_type_name': msg_type_name,
                    'namespace': namespace,
                    'created': created,
                    'modified': modified,
                    'user_context': user_context,
                    'read_at': read_at,
                },
                {
                    'msg_id': msg_id,
                    'msg_type_name': msg_type_name,
                    'namespace': namespace,
                    'created': created,
                    'modified': modified,
                    'user_context': user_context,
                    'read_at': read_at,
                },
                {......},
                {......},
            ]
        }
        """
        updated_user_notification = self._update_user_notification(user_msg)
        user_notification = []
        if updated_user_notification is None:
            user_notification = self._create_new_user_notification(user_msg)
        return list(user_notification)

    def _create_new_user_notification(self, user_msg):
        """
        This method creates a new document for a user id, or inserts a UserNotification in the array of that document.
        """
        user_notification = self.collection.update(
            {
                'user_id': user_msg.user_id,
            },
            {
                '$set': {
                    'user_id': user_msg.user_id
                },
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
                        }],
                        '$position': 0
                    }
                }
            },
            upsert=True
        )

        return user_notification

    def _update_user_notification(self, user_msg):
        """
        Finds and modifies the user_notification. e.g. when marking the notifications as read.
        """
        updated_user_notification = self.collection.find_and_modify(
            query={
                'user_id': user_msg.user_id,
                'user_notification': {'$elemMatch': {'msg_id': user_msg.msg.id}}
            },
            update={
                '$set': {
                    'user_id': user_msg.user_id,
                    'user_notification.$': {
                        'msg_id': user_msg.msg.id,
                        'msg_type_name': user_msg.msg.msg_type.name,
                        'namespace': user_msg.msg.namespace,
                        'created': user_msg.created,
                        'modified': datetime.datetime.now(pytz.UTC),
                        'user_context': user_msg.user_context if user_msg.user_context else None,
                        'read_at': user_msg.read_at
                    }
                }
            }
        )
        return updated_user_notification
