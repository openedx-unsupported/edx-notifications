"""
Django management command to raise a 'fire_background_notification_check' signal to all
application-level listeners
"""

import logging

from django.core.management.base import BaseCommand

from edx_notifications.background import fire_background_notification_check

log = logging.getLogger(__file__)


class Command(BaseCommand):
    """
    Django Management command to force a background check of all possible notifications
    """

    def handle(self, *args, **options):
        """
        Management command entry point, simply call into the signal firiing
        """

        log.info("Running management command to fire notifications asynchronously...")
        print "Running background_notification_check..."

        fire_background_notification_check()

        log.info("Completed background_notification_check.")
        print "Completed background_notification_check."
