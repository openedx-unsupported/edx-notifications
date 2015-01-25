"""
Django ORM models to support the Notification Store SQL backend
"""

from django.db import models
from model_utils.models import TimeStampedModel

from notifications.base_data import DictField

from notifications.data import (
    NotificationMessage,
    NotificationType,
)


class SQLNotificationMessage(TimeStampedModel):
    """
    Model for a notification message
    """

    payload = models.TextField()

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationmessage'

    def from_notification_message(self, obj):
        """
        Copy all of the values from passed in NotificationMessage data object
        """

        # special case when working with the ID's, assert the ID's
        # match
        if obj.id and self.id:  # pylint: disable=access-member-before-definition
            if obj.id != self.id:  # pylint: disable=access-member-before-definition
                msg = (
                    "Attempting to copy over NotificationMessage into SQLNotificationMessage "
                    "but they both have IDs set which do not match! For data integrity reasons "
                    "this is not allowed!"
                )
                raise ValueError(msg)

        if obj.id and not self.id:  # pylint: disable=access-member-before-definition
            self.id = obj.id  # pylint: disable=invalid-name,attribute-defined-outside-init

        self.payload = DictField.to_json(obj.payload)  # special case, dict<-->JSON string

    def to_notification_message(self):
        """
        Return a Notification Message data object
        """

        msg = NotificationMessage(
            id=self.id,
            payload=DictField.from_json(self.payload),  # special case, dict<-->JSON string
        )

        return msg


class SQLNotificationUserMap(models.Model):
    """
    Information about how a Notification is tied to a targeted user, and related state (e.g. read/unread)
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationusermap'

    # NOTE: Be sure to add any user (the target) context we might need here
    # including email, First/Last name (to support any personalization)


class SQLNotificationType(models.Model):
    """
    Notification Type information
    """

    # the internal name is the primary key
    name = models.CharField(primary_key=True, max_length=256)

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationtype'

    def to_notification_type(self):
        """
        Generate a NotificationType data object
        """

        return NotificationType(
            name=self.name
        )

    @classmethod
    def from_notification_type(cls, notification_type):
        """
        create and a MySQL model objects from a NotificationType
        """

        return SQLNotificationType(
            name=notification_type.name
        )


class SQLNotificationChannel(models.Model):
    """
    Information about how notifications are delivered, e.g. web, triggered email,
    SMS, iOS Push Notifications, etc.
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationchannel'


class SQLNotificationTypeRenderingProvided(models.Model):
    """
    Describes which rendering types this notification type supports, e.g. 'json', 'text', 'short-html', 'long-html'
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationtyperenderingprovided'


class SQLNotificationUserTypeChannelMap(models.Model):
    """
    User specific mappings of Notifications to Channel, to reflect user preferences
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationusertypechannelmap'


class SQLDisplayString(models.Model):
    """
    NOTE: These can be cached completely in memory
    """

    string_name = models.CharField(max_length=255, db_index=True)
    lang = models.CharField(max_length=16, db_index=True)
    string_value = models.TextField()

    class Meta(object):

        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_displaystring'
        unique_together = (('string_name', 'lang'),)
