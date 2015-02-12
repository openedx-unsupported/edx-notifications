"""
Run these tests @ Devstack:
    rake fasttest_lms[common/djangoapps/api_manager/management/commands/tests/test_migrate_orgdata.py]
"""

from django.test import TestCase

from django.dispatch import receiver

from edx_notifications.management.commands import background_check

from edx_notifications.background import (
    perform_notification_scan,
)

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

        background_check.Command().handle()

        self.assertTrue(_SIGNAL_RAISED)
