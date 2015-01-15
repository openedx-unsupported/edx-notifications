"""
Django ORM models to support the Notification Store SQL backend
"""

from django.db import models


class NotificationMessage(models.Model):
    """
    Model for a notification message
    """

    class Meta:
        """
        ORM metadata about this class
        """
        app_label = 'notifications'
