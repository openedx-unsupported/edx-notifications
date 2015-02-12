"""
Django management command to raise a 'fire_background_notification_check' signal to all
application-level listeners
"""

import logging

from django.core.management.base import BaseCommand

from edx_notifications.background import fire_background_notification_check

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):
    """
    Django Management command to force a background check of all possible notifications
    """

    def handle(self, *args, **options):
        """
        Management command entry point, simply call into the signal firiing
        """

        logger.info("Running management command to fire notifications asynchronously...")
        fire_background_notification_check()
