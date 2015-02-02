"""
All tests for the test_consumer.py
"""

import json

from django.test.client import Client
from django.core.urlresolvers import reverse

from edx_notifications.server.web.tests.utils import (
    LoggedInTestCase,
)


class ConsumerAPITests(LoggedInTestCase):
    """
    All tests for the views.py
    """

    def test_no_anonymous_access(self):
        """
        Make sure we cannot access API methods without being logged in
        """

        self.client = Client()
        response = self.client.get(reverse('consumer.notifications.count'))
        self.assertEqual(response.status_code, 403)

    def test_empty_notification_count(self):
        """
        Simple test to make sure that a new user does not have
        any notifications
        """

        response = self.client.get(reverse('consumer.notifications.count'))
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 0)
