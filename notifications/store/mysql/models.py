"""
Django ORM models to support the Notification Store SQL backend
"""

from django.db import models


class NotificationMessage(models.Model):

    class Meta:
        app_label = 'notifications'
