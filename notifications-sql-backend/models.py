"""
Django ORM models to support the Notification Store SQL backend
"""

from django.db import models


class NotificationMessage(models.Model):

    class Meta:
        db_table = 'notifications_store_notificationmessage'
