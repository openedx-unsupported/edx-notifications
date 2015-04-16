"""
Create and register a new NotificationCallbackTimerHandler
"""
import datetime
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itertools import groupby
import logging
from django.contrib.staticfiles import finders
import uuid
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import pynliner
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

        subject = timer.context['subject']
        from_email = timer.context['from_email']
        unread_only = timer.context['unread_only']

        # call into the main entry point
        # for generating digests
        send_notifications_digest(
            from_timestamp,
            to_timestamp,
            preference_name,
            subject,
            from_email,
            unread_only=unread_only
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
            'subject': const.NOTIFICATION_DAILY_DIGEST_SUBJECT,
            'from_email': const.NOTIFICATION_DIGEST_FROM_ADDRESS,
            'unread_only': const.NOTIFICATION_DIGEST_UNREAD_ONLY,
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
            'subject': const.NOTIFICATION_DAILY_DIGEST_SUBJECT,
            'from_email': const.NOTIFICATION_DIGEST_FROM_ADDRESS,
            'unread_only': const.NOTIFICATION_DIGEST_UNREAD_ONLY,
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


def send_notifications_digest(from_timestamp, to_timestamp, preference_name, subject,
                              from_email, unread_only=True):
    """
    This will generate and send a digest of all notifications over all namespaces to all
    resolvable users subscribing to digests for that namespace
    """

    digests_sent = 0

    # Get a collection of all namespaces
    namespaces = notification_store().get_all_namespaces()

    # Loop over all namespaces
    for namespace in namespaces:
        digests_sent += send_notifications_namespace_digest(
            namespace,
            from_timestamp,
            to_timestamp,
            preference_name,
            subject,
            from_email,
            unread_only=unread_only
        )

    return digests_sent


def send_notifications_namespace_digest(namespace, from_timestamp, to_timestamp,
                                        preference_name, subject, from_email, unread_only=True):
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
            digests_sent += _send_user_digest(
                namespace_info,
                from_timestamp,
                to_timestamp,
                user_id,
                email,
                first_name,
                last_name,
                subject,
                from_email,
                unread_only=unread_only
            )

    return digests_sent


def with_inline_css(html_without_css):
    """
    returns html with inline css if css file path exists
    else returns html with out the inline css.
    """
    css_filepath = finders.find(const.NOTIFICATION_DIGEST_EMAIL_CSS)

    if css_filepath:
        with open(css_filepath, "r") as _file:
            css_content = _file.read()

        # insert style tag in the html and run pyliner.
        html_with_inline_css = pynliner.fromString('<style>' + css_content + '</style>' + html_without_css)
        return html_with_inline_css

    return html_without_css


def _send_user_digest(namespace_info, from_timestamp, to_timestamp, user_id,
                      email, first_name, last_name, subject, from_email, unread_only=True):
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
            'read': not unread_only,
            'unread': True,
            'start_date': from_timestamp,
            'end_timestamp': to_timestamp,
        },
        options={
            'select_related': True,  # make sure we do JOINs on the initial query
        }
    )

    notification_groups = render_notifications_by_type(notifications)

    # As an option, don't send an email at all if there are no
    # unread notifications
    if not notification_groups and const.NOTIFICATION_DONT_SEND_EMPTY_DIGEST:
        log.debug('Digest email for {email} is empty. Not sending...'.format(email=email))
        return 0

    context = {
        'namespace_display_name': namespace_info['display_name'],
        'grouped_user_notifications': notification_groups
    }

    # render the notifications html template
    notifications_html = render_to_string("django/digests/unread_notifications_inner.html", context)

    # create the image dictionary to store the
    # img_path, unique id and title for the image.
    branded_logo = dict(title='Logo', path=const.NOTIFICATION_BRANDED_DEFAULT_LOGO, cid=str(uuid.uuid4()))

    context = {
        'branded_logo': branded_logo['cid'],
        'user_first_name': first_name,
        'user_last_name': last_name,
        'namespace': namespace_info['display_name'],
        'count': len(notifications),
        'rendered_notifications': notifications_html
    }
    # render the mail digest template.
    email_body = with_inline_css(
        render_to_string("django/digests/branded_notifications_outer.html", context)
    )

    html_part = MIMEMultipart(_subtype='related')
    html_part.attach(MIMEText(email_body, _subtype='html'))
    logo_image = attach_image(branded_logo, 'Header Logo')
    if logo_image:
        html_part.attach(logo_image)

    log.info('Sending Notification Digest email to {email}'.format(email=email))

    msg = EmailMessage(subject, None, from_email, [email])
    msg.attach(html_part)
    msg.send()

    return 1


def attach_image(img_dict, filename):
    """
    attach images in the email headers
    """
    img_path = finders.find(img_dict['path'])
    if img_path:
        with open(img_path, 'rb') as img:
            msg_image = MIMEImage(img.read(), name=os.path.basename(img_path))
            msg_image.add_header('Content-ID', '<{}>'.format(img_dict['cid']))
            msg_image.add_header("Content-Disposition", "inline", filename=filename)
        return msg_image


def get_group_name_for_msg_type(msg_type):
    """
    Returns the particular group_name for the msg_type
    else return None if no group_name is found.
    """
    config = const.NOTIFICATION_DIGEST_GROUP_CONFIG

    if msg_type in config['type_mapping']:
        group_name = config['type_mapping'][msg_type]
        if group_name in config['groups']:
            return group_name

    # no exact match so lets look upwards for wildcards
    search_type = msg_type
    # returns -1 if '.' is not in search_type
    dot_index = search_type.rfind('.')
    while dot_index != -1 and search_type != '*':
        search_type = search_type[0: dot_index]
        key = search_type + '.*'

        if key in config['type_mapping']:
            group_name = config['type_mapping'][key]
            if group_name in config['groups']:
                return group_name

        # returns -1 if '.' is not in search_type
        dot_index = search_type.rfind('.')

    # look for global wildcard
    if '*' in config['type_mapping']:
        key = '*'
        group_name = config['type_mapping'][key]
        if group_name in config['groups']:
            return group_name

    # this really shouldn't happen. This means misconfiguration
    return None


def get_group_rendering(group_data):
    """
    returns the list of the sorted user notifications renderings.
    """
    notification_renderings = []

    group_data = sorted(group_data, key=lambda k: k.msg.created)

    for user_msg in group_data:
        notification_html = ''
        renderer = get_renderer_for_type(user_msg.msg.msg_type)
        if renderer and renderer.can_render_format(const.RENDER_FORMAT_HTML):
            notification_html = renderer.render(  # pylint: disable=unused-variable
                user_msg.msg,
                const.RENDER_FORMAT_HTML,
                None
            )
        else:
            log.info(
                'Missing renderer for HTML format on '
                'msg_type "{}". Skipping....'.format(user_msg.msg.msg_type.name)
            )
        notification_renderings.append(
            {
                'user_msg': user_msg,
                'msg': user_msg.msg,
                # render the particular NotificationMessage
                'html': notification_html,
                'group_name': get_group_name_for_msg_type(user_msg.msg.msg_type.name)
            }
        )

    return notification_renderings


def render_notifications_by_type(user_notifications):
    """
    apply groupings as needed (by type)
    and sort all the notifications by date most recent first

    :return the sorted and grouped notifications.
    """
    grouped_user_notifications = {}
    notification_groups = []

    # group the user notifications by message type name.
    for key, group in groupby(user_notifications, lambda x: get_group_name_for_msg_type(x.msg.msg_type.name)):
        for thing in group:
            if key in grouped_user_notifications:
                grouped_user_notifications[key].append(thing)
            else:
                grouped_user_notifications[key] = [thing]

    # then we want to order the groups according to the grouping_config
    # so we can specify which groups go up at the top
    config = const.NOTIFICATION_DIGEST_GROUP_CONFIG
    group_orderings = sorted(config['groups'].items(), key=lambda t: t[1]['group_order'])

    for group_key, _ in group_orderings:
        if group_key in grouped_user_notifications:
            notification_groups.append(
                {
                    'group_title': config['groups'][group_key]['display_name'],
                    'messages': get_group_rendering(grouped_user_notifications[group_key])
                }
            )

    return notification_groups
