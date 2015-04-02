"""
Create and register a new NotificationCallbackTimerHandler
"""
import datetime
from django.dispatch import receiver
import pytz
from edx_notifications.data import NotificationCallbackTimer, NotificationPreference
from edx_notifications.signals import perform_timer_registrations
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider
from edx_notifications.stores.store import notification_store
from edx_notifications.exceptions import ItemNotFoundError
from django.utils.translation import ugettext as _


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


def create_default_notification_preferences():
    """
    This function installs two default system-defined Notification Preferences
    for daily and weekly Digests.
    """
    store_provider = SQLNotificationStoreProvider()

    daily_digest_preference = NotificationPreference(
        name='daily-notification-digest',
        display_name=_('Daily Notification Digest'),
        display_description=_('This setting will cause a daily digest of all notifications to be sent to your registered email address'),
        default_value='false'
    )

    store_provider.save_notification_preference(daily_digest_preference)

    weekly_digest_preference = NotificationPreference(
        name='weekly-notification-digest',
        display_name=_('Weekly Notification Digest'),
        display_description=_('This setting will cause a weekly digest of all notifications to be sent to your registered email address'),
        default_value='false'
    )

    store_provider.save_notification_preference(weekly_digest_preference)
