"""
Concrete MySQL implementation of the data provider interface
"""

import copy
import pylru

from django.core.exceptions import ObjectDoesNotExist

from notifications.store.store import BaseNotificationStoreProvider
from notifications.exceptions import (
    ItemNotFoundError
)
from notifications import const
from notifications.store.sql.models import (
    SQLNotificationMessage,
    SQLNotificationType,
    SQLNotificationUserMap
)


class SQLNotificationStoreProvider(BaseNotificationStoreProvider):
    """
    Concrete MySQL implementation of the abstract base class (interface)
    """

    def __init__(self, **kwargs):
        """
        Initializer
        """

        _msg_type_cache_size = kwargs.get('MAX_MSG_TYPE_CACHE_SIZE', 1024)
        self._msg_type_cache = pylru.lrucache(_msg_type_cache_size)

    def _get_notification_by_id(self, msg_id, options=None):
        """
        Helper method to get Notification Message by id
        """

        # pylint/pep8 seem to complain if defaults are set to empty dicts
        options = options if options else {}
        select_related = options.get('select_related', True)

        try:
            if select_related:
                obj = SQLNotificationMessage.objects.select_related().get(id=msg_id)
            else:
                obj = SQLNotificationMessage.objects.get(id=msg_id)
        except ObjectDoesNotExist:
            raise ItemNotFoundError()

        return obj.to_data_object(options=options)

    def get_notification_message_by_id(self, msg_id, options=None):
        """
        For the given message id return the corresponding NotificationMessage data object
        """

        return self._get_notification_by_id(msg_id, options=options)

    def save_notification_message(self, msg):
        """
        Saves a passed in NotificationMsg data object. If 'id' is set by the caller
        it will try to update the object. If it does not exist it will throw an
        exception.

        If it is created, then the id property will be set on the NotificationMsg and returned
        """

        if msg.id:
            try:
                obj = SQLNotificationMessage.objects.get(id=msg.id)
                obj.load_from_data_object(msg)
            except ObjectDoesNotExist:
                msg = "Could not SQLNotificationMessage with ID {_id}".format(_id=msg.id)
                raise ItemNotFoundError()
        else:
            obj = SQLNotificationMessage.from_data_object(msg)

        obj.save()
        return obj.to_data_object()

    def get_notification_type(self, name):  # pylint: disable=no-self-use
        """
        This returns a NotificationType object.
        NOTE: NotificationTypes are supposed to be immutable during the
        process lifetime. New Types can be added, but not updated.
        Therefore we can memoize this function
        """

        data_object = None
        # pull from the cache, if we have it
        if name in self._msg_type_cache:
            data_object = self._msg_type_cache[name]
            return data_object

        try:
            obj = SQLNotificationType.objects.get(name=name)
        except ObjectDoesNotExist:
            raise ItemNotFoundError()

        data_object = obj.to_data_object()

        # refresh the cache
        self._msg_type_cache[name] = data_object
        return data_object

    def save_notification_type(self, msg_type):
        """
        Create or update a notification type
        """

        try:
            obj = SQLNotificationType.objects.get(name=msg_type.name)
            obj.load_from_data_object(msg_type)
        except ObjectDoesNotExist:
            obj = SQLNotificationType.from_data_object(msg_type)

        obj.save()

        # remove cached entry
        if msg_type.name in self._msg_type_cache:
            del self._msg_type_cache[msg_type.name]
        return msg_type

    def _get_notifications_for_user(self, user_id, filters=None, options=None):
        """
        Helper method to set up the query to get notifications for a user
        """

        # pylint/pep8 seem to complain if defaults are set to empty dicts
        filters = filters if filters else {}
        options = options if options else {}

        namespace = filters.get('namespace')
        read = filters.get('read', True)
        unread = filters.get('unread', True)
        select_related = options.get('select_related', False)
        limit = options.get('limit', const.MAX_NOTIFICATION_LIST_SIZE)
        offset = options.get('offset', 0)

        # make sure passed in limit is allowed
        # as we don't want to blow up the query too large here
        if limit > const.MAX_NOTIFICATION_LIST_SIZE:
            raise ValueError('Max limit is {limit}'.format(limit=limit))

        if not read and not unread:
            raise ValueError('Bad arg combination either read or unread must be set to True')

        query = SQLNotificationUserMap.objects.filter(user_id=user_id)

        if select_related:
            query = query.select_related()

        if namespace:
            query = query.filter(msg__namespace=namespace)

        if not (read and unread):
            if read:
                query = query.filter(read_at__isnull=False)

            if unread:
                query = query.filter(read_at__isnull=True)

        return query[offset:offset + limit]

    def get_num_notifications_for_user(self, user_id, filters=None):
        """
        Returns an integer count of notifications. It is presumed
        that store provider implementations can make this an optimized
        query

        ARGS:
            - user_id: The id of the user
            - read: Whether to return read notifications (default True)
            - unread: Whether to return unread notifications (default True)

        RETURNS: type list   i.e. []
        """

        return self._get_notifications_for_user(
            user_id,
            filters,
        ).count()

    def get_notifications_for_user(self, user_id, filters=None, options=None):
        """
        Returns a (unsorted) collection (list) of notifications for the user.

        NOTE: We will have to add paging (with sorting/filtering) in the future

        ARGS:
            - user_id: The id of the user
            - filters: a dict containing
                - namespace: what namespace to search (defuault None)
                - read: Whether to return read notifications (default True)
                - unread: Whether to return unread notifications (default True)
            - options: a dict containing some optional parameters
                - limit: max number to return (up to some system defined max)
                - offset: offset into the list, to implement paging

        RETURNS: list   i.e. []
        """

        _options = copy.deepcopy(options) if options else {}
        _options['select_related'] = True

        query = self._get_notifications_for_user(
            user_id,
            filters=filters,
            options=_options
        )

        result_set = []
        for item in query:
            result_set.append(item.to_data_object())

        return result_set

    def save_notification_user_map(self, user_map):
        """
        Create or Update the mapping of a user to a notification.
        """

        if user_map.id:
            try:
                obj = SQLNotificationUserMap.objects.get(id=user_map.id)
                obj.load_from_data_object(user_map)
            except ObjectDoesNotExist:
                msg = "Could not find SQLNotificationUserMap with ID {_id}".format(_id=user_map.id)
                raise ItemNotFoundError(msg)
        else:
            obj = SQLNotificationUserMap.from_data_object(user_map)

        obj.save()

        return obj.to_data_object()
