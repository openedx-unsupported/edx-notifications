import datetime
import pymongo
from pymongo import MongoClient
import pytz
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider


class MongoNotificationStoreProvider(SQLNotificationStoreProvider):
    """

    """

    def __init__(self, **kwargs):
        super(MongoNotificationStoreProvider, self).__init__(**kwargs)
        self.client = MongoClient(kwargs.get('host'), kwargs.get('port'))
        self.db = self.client[kwargs.get('database_name')]
        self.collection = self.db.user_notification

    def _get_prepaged_notifications(self, user_id, filters=None, options=None):
        """
        Helper to set up the notifications query before paging
        is applied. WARNING: This should be used with care and to not
        iterate over this returned results set. Typically this
        will just be used to get a count()
        """

        _filters = filters if filters else {}
        _options = options if options else {}

        query_object = {'user_id': user_id}
        namespace = _filters.get('namespace')
        read = _filters.get('read', True)
        unread = _filters.get('unread', True)
        type_name = _filters.get('type_name')
        start_date = _filters.get('start_date')
        end_date = _filters.get('end_date')
        query_object = [{'user_id': user_id}]
        if not read and not unread:
            raise ValueError('Bad arg combination either read or unread must be set to True')

        if namespace:
            pass
            # query_object.append({'namespace': namespace})

        if not (read and unread):
            if read:
                query_object.append({'read_at': {"$ne": None}})

            if unread:
                query_object.append({'user_notification.read_at': None})

        if type_name:
            pass
            # query_object.append({'msg.msg_type': 'null'})
            # collection = collection.filter(msg__msg_type=type_name)

        if start_date:
            query_object.append({'created': {"gte": start_date}})

        if end_date:
            query_object.append({'created': {"lte": end_date}})

        collection = self.collection.find(*query_object)
        return list(collection)

    def get_notifications_for_user(self, user_id, filters=None, options=None):
        """

        :param user_id:
        :param filters:
        :param options:
        :return:
        """
        self._get_prepaged_notifications(user_id, filters, options)

    def mark_user_notifications_read(self, user_id, filters=None):
        pass

    def get_num_notifications_for_user(self, user_id, filters=None):
        pass

    def purge_expired_notifications(self, purge_read_messages_older_than, purge_unread_messages_older_than):
        pass

    def bulk_create_user_notification(self, user_msgs):
        pass

    def get_notification_for_user(self, user_id, msg_id):
        pass

    def save_user_notification(self, user_msg):
        """
        Create or Update the mapping of a user to a notification.
        """

        super(MongoNotificationStoreProvider, self).save_notification_message(user_msg.msg)

        user_notification = self.collection.find({'user_id': user_msg.user_id})
        if user_notification.count() == 0:
            user_notification = self.collection.insert(
                {
                    'user_id': user_msg.user_id,
                    'user_notification': [{
                        'msg_id': user_msg.msg.id,
                        'created': user_msg.created if user_msg.created else datetime.datetime.now(pytz.UTC),
                        'modified': datetime.datetime.now(pytz.UTC),
                        'user_context': user_msg.user_context if user_msg.user_context else None,
                        'read_at': user_msg.read_at if user_msg.read_at else None
                    }]
                }
            )
        else:
            user_notification = self.collection.update(
                {'user_id': user_msg.user_id},
                {'$push': {
                    'user_notification':
                        {
                            'msg_id': user_msg.msg.id,
                            'created': datetime.datetime.now(pytz.UTC),
                            'modified': datetime.datetime.now(pytz.UTC),
                            'user_context': user_msg.user_context if user_msg.user_context else None,
                            'read_at': user_msg.read_at if user_msg.read_at else None
                        }
                }}
            )
        # user_notification.to_data_object()
        # if user_msg.id:
        #     try:
        #         obj = SQLUserNotification.objects.get(id=user_msg.id)
        #         obj.load_from_data_object(user_msg)
        #     except ObjectDoesNotExist:
        #         msg = "Could not find SQLUserNotification with ID {_id}".format(_id=user_msg.id)
        #         raise ItemNotFoundError(msg)
        # else:
        #     obj = SQLUserNotification.from_data_object(user_msg)
        #
        # obj.save()
        #
        # return obj.to_data_object()

