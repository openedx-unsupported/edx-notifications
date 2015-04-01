"""
Create and register a new NotificationCallbackTimerHandler
"""
import datetime
from django.dispatch import receiver
import pytz
from edx_notifications.data import NotificationCallbackTimer
from edx_notifications.signals import perform_timer_registrations
from edx_notifications.stores.store import notification_store
from edx_notifications.exceptions import ItemNotFoundError

DAILY_DIGEST_TIMER_NAME = 'daily-digest-timer'
MINUTES_IN_A_DAY = 24 * 60
WEEKLY_DIGEST_TIMER_NAME = 'weekly-digest-timer'
MINUTES_IN_A_WEEK = 7 * 24 * 60



@receiver(perform_timer_registrations)
def register_digest_timers(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Register NotificationCallbackTimerHandler.
    This will be called automatically on the Notification subsystem startup (because we are
    receiving the 'perform_timer_registrations' signal)
    """
    store = notification_store()

    try:
        store.get_notification_timer(DAILY_DIGEST_TIMER_NAME)
    except ItemNotFoundError:
        daily_digest_timer = NotificationCallbackTimer(
            name=DAILY_DIGEST_TIMER_NAME,
            callback_at=datetime.datetime.now(pytz.UTC),
            class_name='edx_notifications.callbacks.NotificationDigestMessageCallback',
            is_active=True,
            periodicity_min=MINUTES_IN_A_DAY
        )
        store.save_notification_timer(daily_digest_timer)

    try:
        store.get_notification_timer(WEEKLY_DIGEST_TIMER_NAME)
    except ItemNotFoundError:
        weekly_digest_timer = NotificationCallbackTimer(
            name=WEEKLY_DIGEST_TIMER_NAME,
            callback_at=datetime.datetime.now(pytz.UTC),
            class_name='edx_notifications.callbacks.NotificationDigestMessageCallback',
            is_active=True,
            periodicity_min=MINUTES_IN_A_WEEK
        )
        store.save_notification_timer(weekly_digest_timer)
