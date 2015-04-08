"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/api_manager/management/commands/tests/test_migrate_orgdata.py]
"""
from freezegun import freeze_time

import pytz
from datetime import datetime, timedelta

from django.test import TestCase
from django.dispatch import receiver

from edx_notifications.management.commands import background_notification_check, force_purge
from edx_notifications.stores.sql.store_provider import SQLNotificationStoreProvider

from edx_notifications.stores.store import notification_store
from edx_notifications.background import (
    perform_notification_scan,
)
from edx_notifications.data import (
    NotificationCallbackTimer,
    NotificationType, NotificationMessage, UserNotification)


_SIGNAL_RAISED = False


@receiver(perform_notification_scan)
def verify_signal_receiver(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Simple handler
    """
    global _SIGNAL_RAISED  # pylint: disable=global-statement
    _SIGNAL_RAISED = True


class BackgroundCheckTest(TestCase):
    """
    Test suite for the management command
    """

    def test_background_check(self):
        """
        Invoke the Management Command
        """

        background_notification_check.Command().handle()

        self.assertTrue(_SIGNAL_RAISED)

    def test_timer_execution(self):
        """
        Make sure that Django management command runs through the timers
        """

        timer = NotificationCallbackTimer(
            name='foo',
            class_name='edx_notifications.tests.test_timer.NullNotificationCallbackTimerHandler',
            callback_at=datetime.now(pytz.UTC) - timedelta(days=1),
            context={},
            is_active=True,
        )

        notification_store().save_notification_timer(timer)

        background_notification_check.Command().handle()

        readback_timer = notification_store().get_notification_timer(timer.name)

        self.assertIsNotNone(readback_timer.executed_at)
        self.assertIsNone(readback_timer.err_msg)


class PurgeNotificationsCommandTest(TestCase):
    """
    Test suite for the management command
    """

    def setUp(self):
        """
        Setup the tests values.
        """
        self.provider = SQLNotificationStoreProvider()
        self.test_user_id = 1
        self.notification_type = NotificationType(
            name='foo.bar.baz',
            renderer='foo.renderer',
            renderer_context={
                'param1': 'value1'
            },
        )

    def test_purge_command_check(self):
        """
        Invoke the Management Command
        """
        msg_type = self.provider.save_notification_type(self.notification_type)
        msg1 = self.provider.save_notification_message(NotificationMessage(
            namespace='namespace1',
            msg_type=msg_type,
            payload={
                'foo': 'bar'
            }
        ))

        msg2 = self.provider.save_notification_message(NotificationMessage(
            namespace='namespace1',
            msg_type=msg_type,
            payload={
                'test': 'test'
            }
        ))

        # now reset the time to 66 days ago
        # in order to save the user notification message in the past.
        reset_time = datetime.now(pytz.UTC) - timedelta(days=66)
        with freeze_time(reset_time):
            self.provider.save_user_notification(UserNotification(
                user_id=self.test_user_id,
                msg=msg1
            ))

            self.provider.save_user_notification(UserNotification(
                user_id=self.test_user_id,
                msg=msg2
            ))

        # user notifications count
        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1'
                }
            ),
            2
        )
        # run the management command for purging notifications.
        force_purge.Command().handle()

        # now get the user notification count.
        # count should be 0 at that moment. because
        # all the notifications have been deleted.
        self.assertEqual(
            self.provider.get_num_notifications_for_user(
                self.test_user_id,
                filters={
                    'namespace': 'namespace1'
                }
            ),
            0
        )
