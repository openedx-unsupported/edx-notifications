"""
Concrete MySQL implementation of the data provider interface
"""

import copy
import pylru

from django.core.exceptions import ObjectDoesNotExist

from edx_notifications.stores.store import BaseNotificationStoreProvider
from edx_notifications.exceptions import (
    ItemNotFoundError,
    ItemIntegrityError
)
from edx_notifications import const
from edx_notifications.stores.sql.models import (
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
        _options = options if options else {}
        select_related = _options.get('select_related', True)

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
        _filters = filters if filters else {}
        _options = options if options else {}

        msg_id = _filters.get('msg_id')
        namespace = _filters.get('namespace')
        read = _filters.get('read', True)
        unread = _filters.get('unread', True)
        type_name = _filters.get('type_name')

        select_related = _options.get('select_related', False)
        limit = _options.get('limit', const.MAX_NOTIFICATION_LIST_SIZE)
        offset = _options.get('offset', 0)

        # make sure passed in limit is allowed
        # as we don't want to blow up the query too large here
        if limit > const.MAX_NOTIFICATION_LIST_SIZE:
            raise ValueError('Max limit is {limit}'.format(limit=limit))

        if not read and not unread:
            raise ValueError('Bad arg combination either read or unread must be set to True')

        query = SQLNotificationUserMap.objects.filter(user_id=user_id)

        if select_related:
            query = query.select_related()

        if msg_id:
            query = query.filter(msg__id=msg_id)

        if namespace:
            query = query.filter(msg__namespace=namespace)

        if not (read and unread):
            if read:
                query = query.filter(read_at__isnull=False)

            if unread:
                query = query.filter(read_at__isnull=True)

        if type_name:
            query = query.filter(msg__msg_type=type_name)

        return query[offset:offset + limit]

    def get_num_notifications_for_user(self, user_id, filters=None):
        """
        Returns an integer count of edx_notifications. It is presumed
        that store provider implementations can make this an optimized
        query

        ARGS:
            - user_id: The id of the user
            - filters: a dict containing
                - namespace: what namespace to search (defuault None)
                - read: Whether to return read notifications (default True)
                - unread: Whether to return unread notifications (default True)
                - type_name: which type to return

        RETURNS: integer

        NOTE: You cannot pass in a filter of 'msg_id'
        """

        if filters and 'msg_id' in filters:
            raise ValueError(
                'It is non-sensical to pass in a msg_id '
                'filter parameter into an aggregate counting method!'
            )

        return self._get_notifications_for_user(
            user_id,
            filters=filters,
        ).count()

    def get_notifications_for_user(self, user_id, filters=None, options=None):
        """
        Returns a (unsorted) collection (list) of notifications for the user.

        NOTE: We will have to add paging (with sorting/filtering) in the future

        ARGS:
            - user_id: The id of the user
            - filters: a dict containing
                - msg_id: a particular notification id to retrieve
                    ( if this is used in conjuction with other filters, it may
                      result in an empty set being returned )
                - namespace: what namespace to search (defuault None)
                - read: Whether to return read notifications (default True)
                - unread: Whether to return unread notifications (default True)
                - type_name: which type to return
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

        if filters and 'msg_id' in filters:
            # if we are querying a single specific item, then do
            # some examination of the results

            # and if we don't find a match then raise an exception
            if not result_set:
                err_msg = (
                    'Could not find notification msg_id {msg_id} for {user_id}'
                ).format(msg_id=filters['msg_id'], user_id=user_id)
                raise ItemNotFoundError(err_msg)

            if len(result_set) > 1:
                # There should be at most one match, else raise an exception
                # this really shouldn't happen because there is a database constraint with
                # SQL backends
                err_msg = (
                    'There should be at most 1 NotificationUserMap items found for '
                    'msg_id {msg_id} and user_id {user_id}. {cnt} were found!'
                ).format(msg_id=filters['msg_id'], user_id=user_id, cnt=len(result_set))
                raise ItemIntegrityError(err_msg)

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
