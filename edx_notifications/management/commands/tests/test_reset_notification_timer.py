"""
Tests for the Django management command reset_notification_timer
"""

import pytz
from datetime import datetime, timedelta

from django.test import TestCase

from edx_notifications.management.commands import reset_notification_timer
from edx_notifications.stores.store import notification_store
from edx_notifications.data import NotificationCallbackTimer
from edx_notifications import const


class ResetTimerTest(TestCase):
    """
    Test suite for the management command
    """

    def setUp(self):
        """
        Setup the tests values.
        """

        self.store = notification_store()
        self.timer1 = self.register_timer('foo')
        self.timer2 = self.register_timer(const.DAILY_DIGEST_TIMER_NAME, const.MINUTES_IN_A_DAY)
        self.timer3 = self.register_timer(const.WEEKLY_DIGEST_TIMER_NAME, const.MINUTES_IN_A_WEEK)

    def register_timer(self, timer_name, periodicity_min=60):
        timer = NotificationCallbackTimer(
            name=timer_name,
            class_name='edx_notifications.tests.test_timer.NullNotificationCallbackTimerHandler',
            callback_at=datetime.now(pytz.UTC) - timedelta(days=1),
            context={
                'foo': 'bar'
            },
            is_active=True,
            periodicity_min=periodicity_min,
        )

        return self.store.save_notification_timer(timer)

    def test_timer_execution(self):
        """
        Make sure that Django management command runs through the timers
        """

        reset_notification_timer.Command().handle()

        readback_timer = self.store.get_notification_timer(self.timer1.name)

        self.assertIsNone(readback_timer.executed_at)
        self.assertFalse(readback_timer.is_active)
        self.assertIsNone(readback_timer.err_msg)

        daily_digest_timer = self.store.get_notification_timer(self.timer2.name)
        reset_time = datetime.now(pytz.UTC) + timedelta(minutes=daily_digest_timer.periodicity_min)

        self.assertIn('last_ran', daily_digest_timer.context)
        self.assertTrue(isinstance(daily_digest_timer.context['last_ran'], datetime))
        self.assertTrue(daily_digest_timer.context['last_ran'] < reset_time)
        self.assertIsNone(daily_digest_timer.executed_at)
        self.assertTrue(daily_digest_timer.callback_at > datetime.now(pytz.UTC))

        weekly_digest_timer = self.store.get_notification_timer(self.timer3.name)
        reset_time = datetime.now(pytz.UTC) + timedelta(days=6)

        self.assertIsNone(weekly_digest_timer.executed_at)
        self.assertTrue(weekly_digest_timer.is_active)
        self.assertIn('last_ran', weekly_digest_timer.context)
        self.assertTrue(weekly_digest_timer.callback_at > reset_time)
