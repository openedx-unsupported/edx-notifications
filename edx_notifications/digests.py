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
from edx_notifications.renderers.renderer import get_renderer_for_type
from django.utils.translation import ugettext as _
from edx_notifications.lib.consumer import (
    get_user_preference_by_name,
    get_notification_preference,
    get_notifications_for_user
)
from edx_notifications.callbacks import NotificationCallbackTimerHandler

log = logging.getLogger(__name__)

DAILY_DIGEST_TIMER_NAME = 'daily-digest-timer'
WEEKLY_DIGEST_TIMER_NAME = 'weekly-digest-timer'


class NotificationDigestMessageCallback(NotificationCallbackTimerHandler):
    """
        This is called by the NotificationTimer for triggering sending out
        daily and weekly digest of notification emails.
        The timer.periodicity_min can be used to differentiate between the
        daily (where the periodicity_min will be equal to MINUTES_IN_A_DAY) and
        weekly (where the periodicity_min will be equal to MINUTES_IN_A_WEEK)
        digest timers.

        The return dictionary must contain the key 'reschedule_in_mins' with
        the value timer.periodicity_min in order to re-arm the callback to
        trigger again after the specified interval.
    """

    def notification_timer_callback(self, timer):
        is_daily_digest = True
        if timer.context:
            is_daily_digest = timer.context.get('is_daily_digest')

        # figure out what the preference name should be that controlls
        # the distribution of the digest
        preference_name = const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME
        if timer.context:
            preference_name = timer.context.get(
                'preference_name',
                const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME
            )

        # record a 'to_timestamp'
        to_timestamp = datetime.datetime.now(pytz.UTC)

        # get the last time we ran this timer, this should be the "from_timestamp"
        if timer.context and 'last_ran' in timer.context:
            from_timestamp = timer.context['last_ran']
        else:
            tdelta = datetime.timedelta(days=1) if is_daily_digest else datetime.timedelta(days=7)
            from_timestamp = to_timestamp - tdelta

        # call into the main entry point
        # for generating digests
        send_unread_notifications_digest(
            from_timestamp,
            to_timestamp,
            preference_name
        )

        result = {
            'errors': [],
            'reschedule_in_mins': timer.periodicity_min,
            # be sure to update the timer context, to record when we
            # last ran this digest
            'context_update': {
                'last_ran': to_timestamp,
            }
        }
        return result


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

    daily_digest_timer = NotificationCallbackTimer(
        name=DAILY_DIGEST_TIMER_NAME,
        callback_at=first_execution_at,
        class_name='edx_notifications.digests.NotificationDigestMessageCallback',
        is_active=True,
        periodicity_min=const.MINUTES_IN_A_DAY,
        context={
            'is_daily_digest': True,
            'preference_name': const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME,
        }
    )
    store.save_notification_timer(daily_digest_timer)

    weekly_digest_timer = NotificationCallbackTimer(
        name=WEEKLY_DIGEST_TIMER_NAME,
        callback_at=first_execution_at,
        class_name='edx_notifications.digests.NotificationDigestMessageCallback',
        is_active=True,
        periodicity_min=const.MINUTES_IN_A_WEEK,
        context={
            'is_daily_digest': False,
            'preference_name': const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME,
        }
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


def send_unread_notifications_digest(from_timestamp, to_timestamp, preference_name):
    """
    This will generate and send a digest of all notifications over all namespaces to all
    resolvable users subscribing to digests for that namespace
    """

    digests_sent = 0

    # Get a collection of all namespaces
    namespaces = notification_store().get_all_namespaces()

    # Loop over all namespaces
    for namespace in namespaces:
        digests_sent = digests_sent + send_unread_notifications_namespace_digest(
            namespace,
            from_timestamp,
            to_timestamp,
            preference_name
        )

    return digests_sent


def send_unread_notifications_namespace_digest(namespace, from_timestamp, to_timestamp, preference_name):
    """
    For a particular namespace, send a notification digest, if so configured
    """

    log.info(
        'Inspecting digest for namespace "{namespace}". time ranges '
        '{from_timestamp} to {to_timestamp} preference_name='
        '{preference_name}'.format(
            namespace=namespace,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            preference_name=preference_name
        )
    )

    # Resolve the namespace to get information about it
    namespace_info = resolve_namespace(namespace)
    if not namespace_info:
        log.info(
            'Could not resolve namespace "{namespace}". Skipping...'.format(namespace=namespace)
        )
        return 0

    # see if digests are enabled for this namespace
    if not namespace_info['features'].get('digests'):
        log.info(
            'Namespace "{namespace}" does not have the digests feature enabled. '
            'Skipping...'.format(namespace=namespace)
        )
        return 0

    # make sure we can resolve the users in the namespace
    resolver = namespace_info['default_user_resolver']
    if not resolver:
        log.info(
            'Namespace "{namespace}" does not have a default_user_resolver defined. '
            'Skipping...'.format(namespace=namespace)
        )
        return 0

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
        },
        None
    )

    digests_sent = 0

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
            digests_sent = digests_sent + _send_user_unread_digest(
                namespace_info,
                from_timestamp,
                to_timestamp,
                user_id,
                email,
                first_name,
                last_name
            )

    return digests_sent


def _send_user_unread_digest(namespace_info, from_timestamp, to_timestamp, user_id, email, first_name, last_name):  # pylint: disable=unused-argument
    """
    This will send a digest of unread notifications to a given user. Note, it is assumed here
    that the user's preference has already been checked. namespace_info will contain
    a 'display_name' entry which will be a human readable string that can be put
    in the digest email
    """

    # query all unread notifications for this user since the timestamp
    notifications = get_notifications_for_user(
        user_id,
        filters={
            'read': False,
            'unread': True,
            'start_date': from_timestamp,
            'end_timestamp': to_timestamp,
        },
        options={
            'select_related': True,  # make sure we do JOINs on the initial query
        }
    )

    # keep a counter of the number of unread notifications
    # note: we can't call len() on the cursor
    notifications_count = 0

    #
    # This is just sample code on how to render the notification items
    # on the server side. This needs to be augmented by:
    #    - grouping together similar types (much like unread pane in Backbone app)
    #    - within the groups, sort by date descending (most recent first)
    #
    for notification in notifications:
        notifications_count = notifications_count + 1
        renderer = get_renderer_for_type(notification.msg.msg_type)
        if renderer and renderer.can_render_format(const.RENDER_FORMAT_HTML):
            notification_html = renderer.render(  # pylint: disable=unused-variable
                notification.msg,
                const.RENDER_FORMAT_HTML,
                None
            )
        else:
            log.info(
                'Missing renderer for HTML format on '
                'msg_type "{}". Skipping....'.format(notification.msg.msg_type.name)
            )

    if not notifications_count:
        return 0

    return 1
