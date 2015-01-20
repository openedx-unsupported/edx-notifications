"""
Django ORM models to support the Notification Store SQL backend
"""

from django.db import models
from model_utils.models import TimeStampedModel


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


class SQLNotificationRendering(models.Model):
    """
    Describes a rendering of a Notification, e.g. JSON payload, HTML, etc.
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory


class SQLNotificationUserMap(models.Model):
    """
    Information about how a Notification is tied to a targeted user, and related state (e.g. read/unread)
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory

    # NOTE: Be sure to add any user (the target) context we might need here
    # including email, First/Last name (to support any personalization)


class SQLNotificationType(models.Model):
    """
    Notification Type information
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory


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


class SQLNotificationTypeRenderingProvided(models.Model):
    """
    Describes which rendering types this notification type supports, e.g. 'json', 'text', 'short-html', 'long-html'
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory


class SQLNotificationUserTypeChannelMap(models.Model):
    """
    User specific mappings of Notifications to Channel, to reflect user preferences
    """

    class Meta(object):
        """
        ORM metadata about this class
        """
        app_label = 'notifications'  # since we have this models.py file not in the root app directory


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
        unique_together = (('string_name', 'lang'),)
