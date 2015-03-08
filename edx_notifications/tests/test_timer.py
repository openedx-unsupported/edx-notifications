"""
Tests for the timer.py
"""

import pytz
from datetime import datetime, timedelta
from django.test import TestCase

from edx_notifications.stores.store import notification_store
from edx_notifications.callbacks import NotificationCallbackTimerHandler
from edx_notifications.data import (
    NotificationMessage,
    NotificationType,
    NotificationCallbackTimer
)
from edx_notifications.tests.test_scopes import TestListScopeResolver
from edx_notifications.scopes import register_user_scope_resolver
from edx_notifications.lib.publisher import publish_timed_notification
from edx_notifications.timer import poll_and_execute_timers


class BadNotificationCallbackTimerHandler(NotificationCallbackTimerHandler):
    """
    Does bad things!
    """

    def notification_timer_callback(self, timer):
        """
        Does nothing
        """
        super(BadNotificationCallbackTimerHandler, self).notification_timer_callback(timer)


class NullNotificationCallbackTimerHandler(NotificationCallbackTimerHandler):
    """
    Does nothing
    """

    def notification_timer_callback(self, timer):
        """
        do nothing
        """
        return {}


class TimerTests(TestCase):
    """
    Test cases for timer.py
    """

    def setUp(self):
        """
        Test setup
        """
        self.store = notification_store()

    def test_cant_instantiate_base(self):
        """
        Asserts that we cannot create an instance of NotificationCallbackTimerHandler
        """

        with self.assertRaises(TypeError):
            NotificationCallbackTimerHandler()

    def test_must_implement_method(self):
        """
        Asserts that a derived class of NotificationCallbackTimerHandler shouldn't
        call into the base class
        """

        with self.assertRaises(NotImplementedError):
            BadNotificationCallbackTimerHandler().notification_timer_callback(None)

    def test_recurring_timer(self):
        """
        Make sure recurring timers work
        """

        timer = NotificationCallbackTimer(
            name='foo',
            class_name='edx_notifications.tests.test_timer.NullNotificationCallbackTimerHandler',
            callback_at=datetime.now(pytz.UTC) - timedelta(days=1),
            context={},
            is_active=True,
            periodicity_min=1
        )

        self.store.save_notification_timer(timer)

        poll_and_execute_timers()

        timer1 = self.store.get_notification_timer(timer.name)
        self.assertIsNone(timer1.executed_at)  # should be marked as still to execute
        self.assertIsNone(timer1.err_msg)
        self.assertNotEqual(timer.callback_at, timer1.callback_at)  # verify the callback time is incremented

        poll_and_execute_timers()

        timer2 = self.store.get_notification_timer(timer.name)
        self.assertIsNone(timer2.executed_at)  # should be marked as still to execute
        self.assertIsNone(timer2.err_msg)
        self.assertNotEqual(timer1.callback_at, timer2.callback_at)

        poll_and_execute_timers()

        timer3 = self.store.get_notification_timer(timer.name)
        self.assertIsNone(timer3.executed_at)  # should be marked as still to execute
        self.assertIsNone(timer3.err_msg)
        self.assertNotEqual(timer2.callback_at, timer3.callback_at)  # verify the callback time is incremented

    def test_bad_handler(self):
        """
        Make sure that a timer with a bad class_name doesn't operate
        """

        timer = NotificationCallbackTimer(
            name='foo',
            class_name='edx_notifications.badmodule.BadHandler',
            callback_at=datetime.now(pytz.UTC) - timedelta(days=1),
            context={},
            is_active=True
        )

        self.store.save_notification_timer(timer)

        poll_and_execute_timers()

        updated_timer = self.store.get_notification_timer(timer.name)

        self.assertIsNotNone(updated_timer.executed_at)
        self.assertIsNotNone(updated_timer.err_msg)


class TimedNotificationsTests(TestCase):
    """
    Tests the creating of timed notifications
    """

    def setUp(self):
        """
        start up stuff
        """

        register_user_scope_resolver('list_scope', TestListScopeResolver())

        self.store = notification_store()
        self.msg_type = self.store.save_notification_type(
            NotificationType(
                name='foo.bar',
                renderer='foo',
            )
        )

        self.msg = self.store.save_notification_message(
            NotificationMessage(
                msg_type=self.msg_type,
                payload={'foo': 'bar'},
            )
        )

    def test_timed_notifications(self):
        """
        Tests that we can create a timed notification and make sure it gets
        executed with the timer polling
        """

        # assert we start have with no notifications
        self.assertEquals(self.store.get_num_notifications_for_user(1), 0)

        # set up a timer that is due in the past
        timer = publish_timed_notification(
            msg=self.msg,
            send_at=datetime.now(pytz.UTC) - timedelta(seconds=1),
            scope_name='user',
            scope_context={'user_id': 1}
        )

        poll_and_execute_timers()

        # fetch the timer from the DB as it should be updated
        updated_timer = self.store.get_notification_timer(timer.name)

        self.assertIsNotNone(updated_timer.executed_at)
        self.assertIsNone(updated_timer.err_msg)

        # assert we now have a notification due to the timer executing
        self.assertEquals(self.store.get_num_notifications_for_user(1), 1)

    def test_timed_broadcast(self):
        """
        Tests that we can create a timed notification and make sure it gets
        executed with the timer polling
        """

        # set up a timer that is due in the past
        timer = publish_timed_notification(
            msg=self.msg,
            send_at=datetime.now(pytz.UTC) - timedelta(seconds=1),
            scope_name='list_scope',
            scope_context={'range': 5}
        )

        # assert we start have with no notifications
        for user_id in range(timer.context['distribution_scope']['scope_context']['range']):
            self.assertEquals(self.store.get_num_notifications_for_user(user_id), 0)

        poll_and_execute_timers()

        # fetch the timer from the DB as it should be updated
        updated_timer = self.store.get_notification_timer(timer.name)

        self.assertIsNotNone(updated_timer.executed_at)
        self.assertIsNone(updated_timer.err_msg)

        # assert we now have a notification
        for user_id in range(timer.context['distribution_scope']['scope_context']['range']):
            self.assertEquals(self.store.get_num_notifications_for_user(user_id), 1)

    def test_wait_for_correct_time(self):
        """
        Make sure timers don't fire too early and they can be rescheduled
        """

        # set up a timer that is due in the future
        timer = publish_timed_notification(
            msg=self.msg,
            send_at=datetime.now(pytz.UTC) + timedelta(days=1),
            scope_name='user',
            scope_context={'range': 1}
        )

        poll_and_execute_timers()

        # fetch the timer again from DB
        updated_timer = self.store.get_notification_timer(timer.name)

        # should not have executed
        self.assertIsNone(updated_timer.executed_at)

        timer = publish_timed_notification(
            msg=self.msg,
            send_at=datetime.now(pytz.UTC) - timedelta(days=1),
            scope_name='user',
            scope_context={'user_id': 1},
            timer_name=timer.name
        )

        poll_and_execute_timers()

        # fetch the timer from the DB as it should be updated
        updated_timer = self.store.get_notification_timer(timer.name)

        self.assertIsNotNone(updated_timer.executed_at)
        self.assertIsNone(updated_timer.err_msg)

        # assert we now have a notification due to the timer executing
        self.assertEquals(self.store.get_num_notifications_for_user(1), 1)
