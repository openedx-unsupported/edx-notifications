"""
Django ORM models to support the Notification Store SQL backend
"""

from django.db import models
from model_utils.models import TimeStampedModel

from notifications.base_data import DictField

from notifications.data import (
    NotificationMessage,
    NotificationType,
    NotificationUserMap,
)


class SQLNotificationMessage(TimeStampedModel):
    """
    Model for a notification message
    """

    payload = models.TextField()

    # a notification namespace is an optional scoping
    # field. This could be used to indicate - for instance - a course_id
    namespace = models.CharField(max_length=128, db_index=True, null=True)

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationmessage'
        ordering = ['-created']  # default order is last one first

    @classmethod
    def from_data_object(cls, obj):
        """
        Copy all of the values from passed in NotificationMessage data object
        """

        return SQLNotificationMessage(
            id=obj.id,
            namespace=obj.namespace,
            payload=DictField.to_json(obj.payload)
        )

    def to_data_object(self):
        """
        Return a Notification Message data object
        """

        msg = NotificationMessage(
            id=self.id,
            namespace=self.namespace,
            payload=DictField.from_json(self.payload),  # special case, dict<-->JSON string
        )

        return msg


class SQLNotificationUserMap(models.Model):
    """
    Information about how a Notification is tied to a targeted user, and related state (e.g. read/unread)
    """

    user_id = models.IntegerField(db_index=True)

    msg = models.ForeignKey(SQLNotificationMessage, db_index=True)

    read_at = models.DateTimeField(null=True, db_index=True)

    user_context = models.TextField(null=True)

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory
        db_table = 'notifications_notificationusermap'
        unique_together = (('user_id', 'msg'),)  # same user should get the same notification twice

    def to_data_object(self):
        """
        Generate a NotificationType data object
        """

        return NotificationUserMap(
            user_id=self.user_id,
            msg=self.msg.to_data_object(),  # pylint: disable=no-member
            read_at=self.read_at,
            user_context=DictField.from_json(self.user_context)
        )

    @classmethod
    def from_data_object(cls, notification_type):
        """
        create and a MySQL model objects from a NotificationType
        """

        return SQLNotificationUserMap(
            user_id=notification_type.user_id,
            msg=SQLNotificationMessage.from_data_object(notification_type.msg),
            read_at=notification_type.read_at,
            user_context=DictField.to_json(notification_type.user_context)
        )


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

    def to_data_object(self):
        """
        Generate a NotificationType data object
        """

        return NotificationType(
            name=self.name
        )

    @classmethod
    def from_data_object(cls, notification_type):
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
