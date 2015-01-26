"""
Concrete MySQL implementation of the data provider interface
"""

from pylru import lrudecorator

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from notifications.store.store import BaseNotificationStoreProvider
from notifications.exceptions import (
    ItemNotFoundError,
    ItemConflictError
)

from notifications.store.mysql.models import (
    SQLNotificationMessage,
    SQLNotificationType,
    SQLNotificationUserMap
)


class MySQLNotificationStoreProvider(BaseNotificationStoreProvider):
    """
    Concrete MySQL implementation of the abstract base class (interface)
    """

    def get_notification_message_by_id(self, msg_id):
        """
        For the given message id return the corresponding NotificationMessage data object
        """

        try:
            obj = SQLNotificationMessage.objects.get(id=msg_id)
        except ObjectDoesNotExist:
            raise ItemNotFoundError()

        return obj.to_data_object()

    def save_notification_message(self, msg):
        """
        Saves a passed in NotificationMsg data object. If 'id' is set by the caller
        it will try to update the object. If it does not exist it will throw an
        exception.

        If it is created, then the id property will be set on the NotificationMsg and returned
        """

        if msg.id:
            if not SQLNotificationMessage.objects.filter(id=msg.id).exists():
                raise ItemNotFoundError()

        # copy over all of the fields from the data object into the
        # ORM object
        obj = SQLNotificationMessage.from_data_object(msg)
        obj.save()
        return obj.to_data_object()

    @lrudecorator(1024)
    def get_notification_type(self, name):  # pylint: disable=no-self-use
        """
        This returns a NotificationType object.
        NOTE: NotificationTypes are supposed to be immutable during the
        process lifetime. New Types can be added, but not updated.
        Therefore we can memoize this function
        """

        try:
            obj = SQLNotificationType.objects.get(name=name)
        except ObjectDoesNotExist:
            raise ItemNotFoundError()

        return obj.to_data_object()

    def save_notification_type(self, msg_type):
        """
        Saves a new notification type, note that we do not support updates
        """

        try:
            existing = None

            # see if this name already exists
            if SQLNotificationType.objects.filter(name=msg_type.name).exists():
                existing = self.get_notification_type(msg_type.name)
                # if the objects are the same, then that is OK
                # just return immediately
                if existing == msg_type:
                    return msg_type
                else:
                    raise ItemConflictError()

            obj = SQLNotificationType.from_data_object(msg_type)
            obj.save()
        except IntegrityError:
            # This should get caught up above in the existence detection
            # but theoretically, we could have a timing issue
            # in a multi-process scenario
            raise ItemConflictError()

        return msg_type

    def _get_notifications_for_user(self, user_id, read, unread):
        """
        Helper method to set up the query to get notifications for a user
        """

        query = SQLNotificationUserMap.objects.filter(user_id=user_id)
        if read:
            query = query.filter(read_at__isnull=False)

        if unread:
            query = query.filter(read_at__isnull=True)

        return query

    def get_num_notifications_for_user(self, user_id, read=True, unread=True):
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

        return self._get_notifications_for_user(user_id, read, unread).count()

    def get_notifications_for_user(self, user_id, read=True, unread=True):
        """
        Returns a (unsorted) collection (list) of notifications for the user.

        NOTE: We will have to add paging (with sorting/filtering) in the future

        ARGS:
            - user_id: The id of the user
            - read: Whether to return read notifications (default True)
            - unread: Whether to return unread notifications (default True)

        RETURNS: list   i.e. []
        """

        query = self._get_notifications_for_user(user_id, read, unread)

        # sort?
        result_set = []
        for item in query:
            result_set.append(item.to_data_object())

        return result_set

    def save_notification_user_map(self, user_map):
        """
        Update the mapping of a user to a notification
        """

        if user_map.id:
            if not SQLNotificationUserMap.objects.filter(id=user_map.id).exists():
                raise ItemNotFoundError()

        # copy over all of the fields from the data object into the
        # ORM object
        obj = SQLNotificationUserMap.from_data_object(user_map)
        return obj.to_data_object()
