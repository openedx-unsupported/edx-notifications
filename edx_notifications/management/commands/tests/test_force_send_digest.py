"""
Tests for the Django management command force_send_digest
"""

from django.test import TestCase
from edx_notifications.management.commands import force_send_digest


class ForceSendDigestCommandTest(TestCase):
    def test_command_check(self):
        # run the management command for purging notifications.
        force_send_digest.Command().handle(**{'send_daily_digest': True, 'send_weekly_digest': True, 'namespace': 'All'})
        force_send_digest.Command().handle(**{'send_daily_digest': True, 'send_weekly_digest': True, 'namespace': 'ABC'})
        # force_send_digest.Command().handle(**{'send_daily_digest': False, 'send_weekly_digest': False, 'namespace': 'ABC'})
