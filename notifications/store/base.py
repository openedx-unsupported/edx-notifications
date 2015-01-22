"""
Defines abstract class for the Notification Store data tier
"""

import abc


class NotificationDataProviderBase(object):
    """
    The base abstract class for all notifications data providers, such as MySQL/Django-ORM backed
    """

    @abc.abstractmethod
    def get_notification_message_by_id(self, msg_id):
        """
        Returns the notitication message (of NotificationMessage type) by primary key
        """

    @abc.abstractmethod
    def save_notification_message(self, msg):
        """
        Save (create or update) a notification message (of NotificationMessage type)
        """
