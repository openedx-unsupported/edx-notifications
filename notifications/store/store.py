"""
Defines abstract class for the Notification Store data tier
"""

import abc


class BaseNotificationStoreProvider(object):
    """
    The base abstract class for all notifications data providers, such as MySQL/Django-ORM backed
    """

    # don't allow instantiation of this class, it must be subclassed
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_notification_message_by_id(self, msg_id):
        """
        Returns the notitication message (of NotificationMessage type) by primary key

        ARGS:
            - msg_id: the primary key of the NotificationMessage

        RETURNS: type NotificationMessage
        """

    @abc.abstractmethod
    def save_notification_message(self, msg):
        """
        Save (create or update) a notification message (of NotificationMessage type)

        ARGS:
            - msg: an instance of NotificationMessage. If the 'id' field is
                   set by the caller, then it is assumed to be an update
                   operation

        RETURNS: type NotificationMessage
        """

    @abc.abstractmethod
    def get_notifications_for_user(self, user_id, read=True, unread=True):
        """
        Returns a (unsorted) collection (list) of notifications for the user.

        NOTE: We will have to add paging (with sorting/filtering) in the future

        ARGS:
            - user_id: The id of the user
            - read: Whether to return read notifications (default True)
            - unread: Whether to return unread notifications (default True)

        RETURNS: type list   i.e. []
        """
