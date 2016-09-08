"""
Django management command to raise a 'fire_background_notification_check' signal to all
application-level listeners
"""

import logging
import logging.config
import sys

# Have all logging go to stdout with management commands
# this must be up at the top otherwise the
# configuration does not appear to take affect
from edx_notifications.stores.store import notification_store
from django.core.management.base import BaseCommand

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}
logging.config.dictConfig(LOGGING)

log = logging.getLogger(__file__)


class Command(BaseCommand):
    """
    Django Management command to
    """

    def handle(self, *args, **options):
        """
        Management command entry point, simply call into the
        """

        log.info("Running management command to create indexes in a mongodb")

        # try:
        mongodb_store = notification_store()
        try:
            mongodb_store.create_mongodb_indexes()
        except Exception as ex:  # pylint: disable=broad-except
            log.error(str(ex.message))

        log.info("Completed creating mongodb indexes.")
