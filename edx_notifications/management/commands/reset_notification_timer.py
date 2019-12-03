"""
Django management command to fetch records from SQLNotificationCallbackTimer with name
'daily-digest-timer' and 'weekly-digest-timer' and reset their 'callback_at' and 'last_ran' values
 to avoid sending old notification digest emails to users.
"""

import logging.config
import sys
import pytz

from datetime import datetime, timedelta
from django.core.management.base import BaseCommand

from edx_notifications.exceptions import ItemNotFoundError
from edx_notifications.stores.store import notification_store
from edx_notifications.timer import PURGE_NOTIFICATIONS_TIMER_NAME
from edx_notifications import const

# Have all logging go to stdout with management commands
# this must be up at the top otherwise the
# configuration does not appear to take affect
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
    Django management command to fetch records from SQLNotificationCallbackTimer with name
    'daily-digest-timer' and 'weekly-digest-timer' and reset their 'callback_at' and 'last_ran'
    values to avoid sending old notification digest emails to users
    """

    help = 'Command to reset notification digest emails timer'
    INCLUDED_TIMERS = [
        const.DAILY_DIGEST_TIMER_NAME,
        const.WEEKLY_DIGEST_TIMER_NAME,
        PURGE_NOTIFICATIONS_TIMER_NAME,
    ]
    store = notification_store()

    def cancel_old_notification_timers(self):
        """
        Get all the old timers, other than daily/weekly digests timers, that are not executed and
        cancel them as executing them will generate a lot of notifications.
        """
        timers_not_executed = self.store.get_all_active_timers()

        for timer in timers_not_executed:
            if timer.name not in self.INCLUDED_TIMERS:
                log.info(
                    'Cancelling timed Notification named {timer}...'.format(timer=str(timer.name)))

                timer.is_active = False
                self.store.save_notification_timer(timer)

    def reset_digest_notification_timer(self):
        """
        Gets old timers of daily and weekly digests and update callback_at value with current
        UTC datetime and add timedelta and last_ran value with current UTC datetime to avoid
        sending old notification digest emails to users.
        """
        context = {
            'last_ran': datetime.now(pytz.UTC),
        }

        try:
            digest_timer = self.store.get_notification_timer(const.DAILY_DIGEST_TIMER_NAME)
            if digest_timer:
                log.info("Resetting notification digest timer for daily digests.")

                rerun_delta = (digest_timer.periodicity_min
                               if digest_timer.periodicity_min
                               else const.MINUTES_IN_A_DAY)
                digest_timer.callback_at = datetime.now(pytz.UTC) + timedelta(minutes=rerun_delta)
                digest_timer.callback_at = digest_timer.callback_at.replace(hour=0, minute=0,
                                                                            second=0, microsecond=0)
                digest_timer.context.update(context)

                self.store.save_notification_timer(digest_timer)
        except ItemNotFoundError:
            log.info("Daily digests timer not found.")

        try:
            digest_timer = self.store.get_notification_timer(const.WEEKLY_DIGEST_TIMER_NAME)
            if digest_timer:
                log.info("Resetting notification digest timer for weekly digests.")

                rerun_delta = (digest_timer.periodicity_min
                               if digest_timer.periodicity_min
                               else const.MINUTES_IN_A_WEEK)
                digest_timer.callback_at = datetime.now(pytz.UTC) + timedelta(minutes=rerun_delta)
                digest_timer.callback_at = digest_timer.callback_at.replace(hour=0, minute=0,
                                                                            second=0, microsecond=0)
                digest_timer.context.update(context)

                self.store.save_notification_timer(digest_timer)
        except ItemNotFoundError:
            log.info("Weekly digests timer not found.")

    def handle(self, *args, **options):
        """
        Management command entry point, simply calls:
        1. cancel_old_notification_timers to cancel all old notification timers other than
           digest timers
        2. store provider's get_notification_timer to update the callback_at and last_ran values.
        """

        log.info("Running management command to reset notification digest timer.")

        self.cancel_old_notification_timers()
        self.reset_digest_notification_timer()

        log.info("Completed reset_notification_timer.")
