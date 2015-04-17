"""
Tests for the Django management command force_send_digest
"""
import datetime
from django.core.management import CommandError

from django.test import TestCase
import pytz
from edx_notifications import const
from edx_notifications.data import NotificationPreference, NotificationType, NotificationMessage
from edx_notifications.lib.consumer import set_user_notification_preference
from edx_notifications.lib.publisher import publish_notification_to_user
from edx_notifications.management.commands import force_send_digest
from edx_notifications.namespaces import NotificationNamespaceResolver, register_namespace_resolver
from edx_notifications.scopes import NotificationUserScopeResolver
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider
from edx_notifications.stores.store import notification_store
from django.utils.translation import ugettext as _


class TestUserResolver(NotificationUserScopeResolver):
    """
    UserResolver for test purposes
    """
    def resolve(self, scope_name, scope_context, instance_context):
        """
        Implementation of interface method
        """
        return [
            {
                'id': 1001,
                'email': 'dummy@dummy.com',
                'first_name': 'Joe',
                'last_name': 'Smith'
            }
        ]


class TestNamespaceResolver(NotificationNamespaceResolver):
    """
    Namespace resolver for demo purposes
    """
    def resolve(self, namespace, instance_context):
        """
        Implementation of interface method
        """
        return {
            'namespace': namespace,
            'display_name': 'A Test Namespace',
            'features': {
                'digests': True,
            },
            'default_user_resolver': TestUserResolver()
        }


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


class ForceSendDigestCommandTest(TestCase):

    def setUp(self):
        """
        Initialize tests, by creating users and populating some
        unread notifications
        """
        create_default_notification_preferences()
        self.store = notification_store()
        self.test_user_id = 1001
        self.from_timestamp = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=1)
        self.weekly_from_timestamp = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=7)
        self.to_timestamp = datetime.datetime.now(pytz.UTC)

        self.msg_type = self.store.save_notification_type(
            NotificationType(
                name='foo.bar',
                renderer='edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
            )
        )

        self.msg_type_no_renderer = self.store.save_notification_type(
            NotificationType(
                name='foo.baz',
                renderer='foo',
            )
        )

        # create two notifications
        msg = self.store.save_notification_message(
            NotificationMessage(
                msg_type=self.msg_type,
                namespace='foo',
                payload={'subject': 'foo', 'body': 'bar'},
            )
        )
        self.notification1 = publish_notification_to_user(self.test_user_id, msg)

        msg = self.store.save_notification_message(
            NotificationMessage(
                msg_type=self.msg_type_no_renderer,
                namespace='bar',
                payload={'subject': 'foo', 'body': 'bar'},
            )
        )
        self.notification2 = publish_notification_to_user(self.test_user_id, msg)

        register_namespace_resolver(TestNamespaceResolver())

        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME, 'false')
        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME, 'false')

    def test_sends_both_digests_if_preferences_set(self):
        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME, 'true')
        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME, 'true')

        sent_digests_count = force_send_digest.Command().handle(
            **{'send_daily_digest': True, 'send_weekly_digest': True, 'namespace': 'All'}
        )
        self.assertEqual(sent_digests_count, 4)

    def test_sends_daily_digest_if_preference_set(self):

        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME, 'true')

        sent_digests_count = force_send_digest.Command().handle(
            **{'send_daily_digest': True, 'send_weekly_digest': False, 'namespace': 'All'}
        )
        self.assertEqual(sent_digests_count, 2)

    def test_doesnt_send_daily_digest_if_preference_unset(self):

        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME, 'false')

        sent_digests_count = force_send_digest.Command().handle(
            **{'send_daily_digest': True, 'send_weekly_digest': False, 'namespace': 'All'}
        )
        self.assertEqual(sent_digests_count, 0)

    def test_doesnt_send_both_digests_if_preferences_unset(self):
        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_DAILY_DIGEST_PREFERENCE_NAME, 'false')
        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME, 'false')

        sent_digests_count = force_send_digest.Command().handle(
            **{'send_daily_digest': True, 'send_weekly_digest': True, 'namespace': 'ABC'}
        )
        self.assertEqual(sent_digests_count, 0)

    def test_sends_weekly_digest_if_preference_set(self):

        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME, 'true')

        sent_digests_count = force_send_digest.Command().handle(
            **{'send_daily_digest': False, 'send_weekly_digest': True, 'namespace': 'All'}
        )
        self.assertEqual(sent_digests_count, 2)

    def test_doesnt_send_weekly_digest_if_preference_unset(self):

        set_user_notification_preference(self.test_user_id, const.NOTIFICATION_WEEKLY_DIGEST_PREFERENCE_NAME, 'false')

        sent_digests_count = force_send_digest.Command().handle(
            **{'send_daily_digest': False, 'send_weekly_digest': True, 'namespace': 'All'}
        )
        self.assertEqual(sent_digests_count, 0)

    def test_not_providing_correct_arguments_causes_error(self):
        self.assertRaises(CommandError, lambda: force_send_digest.Command().handle(
            **{'send_daily_digest': False, 'send_weekly_digest': False, 'namespace': 'ABC'})
        )
