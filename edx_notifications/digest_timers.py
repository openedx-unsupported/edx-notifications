from contracts import contract
import datetime
from django.dispatch import receiver
from edx_notifications.data import NotificationMessage, NotificationCallbackTimer
from edx_notifications.signals import perform_timer_registrations
from edx_notifications.stores.store import notification_store

DAILY_DIGEST_TIMER_NAME = 'daily-digest-timer'
WEEKLY_DIGEST_TIMER_NAME = 'weekly-digest-timer'


@receiver(perform_timer_registrations)
def register_digest_timers():
    store = notification_store()

    weekly_digest_timer = NotificationCallbackTimer(
        name=WEEKLY_DIGEST_TIMER_NAME,
        callback_at=datetime.datetime.now(),
        class_name='edx_notifications.callbacks.NotificationDigestMessageCallback',
        is_active=True,
        periodicity_min=7*24*60
    )

    saved_weekly_digest_timer = store.save_notification_timer(weekly_digest_timer)

    daily_digest_timer = NotificationCallbackTimer(
        name=DAILY_DIGEST_TIMER_NAME,
        callback_at=datetime.datetime.now(),
        class_name='edx_notifications.callbacks.NotificationDigestMessageCallback',
        is_active=True,
        periodicity_min=24*60
    )

    saved_daily_digest_timer = store.save_notification_timer(daily_digest_timer)

