"""
Create and register a new NotificationCallbackTimerHandler
"""
import datetime
import logging
from edx_notifications import const
from django.dispatch import receiver
import pytz
from edx_notifications.data import NotificationCallbackTimer, NotificationPreference
from edx_notifications.signals import perform_timer_registrations
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider
from edx_notifications.stores.store import notification_store
from edx_notifications.exceptions import ItemNotFoundError
from edx_notifications.namespaces import resolve_namespace
from django.utils.translation import ugettext as _
from edx_notifications.lib.consumer import get_user_preference_by_name, get_notification_preference

log = logging.getLogger(__name__)

DAILY_DIGEST_TIMER_NAME = 'daily-digest-timer'
WEEKLY_DIGEST_TIMER_NAME = 'weekly-digest-timer'


@receiver(perform_timer_registrations)
def register_digest_timers(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Register NotificationCallbackTimerHandler.
    This will be called automatically on the Notification subsystem startup (because we are
    receiving the 'perform_timer_registrations' signal)
    """
    store = notification_store()

    # Set first execution time as upcoming midnight after the server is run for the first time.
    first_execution_at = datetime.datetime.now(pytz.UTC) + datetime.timedelta(days=1)
    first_execution_at = first_execution_at.replace(hour=0, minute=0, second=0, microsecond=0)

    try:
        store.get_notification_timer(DAILY_DIGEST_TIMER_NAME)
    except ItemNotFoundError:
        daily_digest_timer = NotificationCallbackTimer(
            name=DAILY_DIGEST_TIMER_NAME,
            callback_at=first_execution_at,
            class_name='edx_notifications.callbacks.NotificationDigestMessageCallback',
            is_active=True,
            periodicity_min=const.MINUTES_IN_A_DAY
        )
        store.save_notification_timer(daily_digest_timer)

    try:
        store.get_notification_timer(WEEKLY_DIGEST_TIMER_NAME)
    except ItemNotFoundError:
        weekly_digest_timer = NotificationCallbackTimer(
            name=WEEKLY_DIGEST_TIMER_NAME,
            callback_at=first_execution_at,
            class_name='edx_notifications.callbacks.NotificationDigestMessageCallback',
            is_active=True,
            periodicity_min=const.MINUTES_IN_A_WEEK
        )
        store.save_notification_timer(weekly_digest_timer)


def create_default_notification_preferences():
    """
    This function installs two default system-defined Notification Preferences
    for daily and weekly Digests.
    """
    store_provider = SQLNotificationStoreProvider()

    daily_digest_preference = NotificationPreference(
        name=const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME,
        display_name=_('Daily Notification Digest'),
        display_description=_('This setting will cause a daily digest of all notifications to be sent to your'
                              ' registered email address'),
        default_value=const.NOTIFICATIONS_PREFERENCE_DAILYDIGEST_DEFAULT
    )

    store_provider.save_notification_preference(daily_digest_preference)

    weekly_digest_preference = NotificationPreference(
        name=const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME,
        display_name=_('Weekly Notification Digest'),
        display_description=_('This setting will cause a weekly digest of all notifications to be sent to your'
                              ' registered email address'),
        default_value=const.NOTIFICATIONS_PREFERENCE_WEEKLYDIGEST_DEFAULT
    )

    store_provider.save_notification_preference(weekly_digest_preference)


def send_unread_notifications_digest(is_daily_digest=True):
    """
    This will generate and send a digest of all notifications over all namespaces to all
    resolvable users subscribing to digests for that namespace
    """

    preference_name = const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME \
        if is_daily_digest else const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME

    # Get a collection of all namespaces
    namespaces = notification_store().get_all_namespaces()

    # Loop over all namespaces
    for namespace in namespaces:
        log.info(
            'Inspecting digest for namespace "{namespace}". is_daily_digest = {is_daily_digest} '
            '{timestamp}'.format(namespace=namespace, is_daily_digest=is_daily_digest)
        )

        # Resolve the namespace to get information about it
        namespace_info = resolve_namespace(namespace)
        if not namespace_info:
            log.info(
                'Could not resolve namespace "{namespace}". Skipping...'.format(namespace=namespace)
            )
            continue

        # see if digests are enabled for this namespace
        if not namespace_info['features'].get('digests'):
            log.info(
                'Namespace "{namespace}" does not have the digests feature enabled. '
                'Skipping...'.format(namespace=namespace)
            )
            continue

        # make sure we can resolve the users in the namespace
        resolver = namespace_info['default_user_resolver']
        if not resolver:
            log.info(
                'Namespace "{namespace}" does not have a default_user_resolver defined. '
                'Skipping...'.format(namespace=namespace)
            )
            continue

        # see what the default preference is
        notification_preference = get_notification_preference(preference_name)
        default_wants_digest = notification_preference.default_value.lower() == 'true'

        # Get a collection (cursor) of users within this namespace scope
        users = resolver.resolve(
            const.NOTIFICATION_NAMESPACE_USER_SCOPE_NAME,
            {
                'namespace': namespace,
                'fields': {
                    'id': True,
                    'email': True,
                    'first_name': True,
                    'last_name': True
                }
            }
        )

        # Loop over all users that are within the scope of the namespace
        # and specify that we want id, email, first_name, and last_name fields
        for user in users:
            user_id = user['id']
            email = user['email']
            first_name = user['first_name']
            last_name = user['last_name']

            # check preferences for user to get a digest
            user_wants_digest = default_wants_digest
            try:
                user_preference = get_user_preference_by_name(user_id, preference_name)
                user_wants_digest = user_preference.value.lower() == 'true'
            except ItemNotFoundError:
                # use the default
                pass

            if user_wants_digest:
                log.debug(
                    'Sending digest email from namespace "{namespace}" '
                    'to user_id = {user_id} at email '
                    '{email}...'.format(namespace=namespace, user_id=user_id, email=email)
                )
                _send_user_unread_digest(namespace_info, is_daily_digest, user_id, email, first_name, last_name)

    return


def _send_user_unread_digest(namespace_info, is_daily_digest, user_id, email, first_name, last_name):
    """
    This will send a digest of unread notifications to a given user. Note, it is assumed here
    that the user's preference has already been checked. namespace_info will contain
    a 'display_name' entry which will be a human readable string that can be put
    in the digest email
    """

    return
