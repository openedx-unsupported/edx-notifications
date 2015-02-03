"""
All tests for the test_consumer.py
"""

import json

from django.test.client import Client
from django.core.urlresolvers import reverse

from edx_notifications.server.web.tests.utils import (
    LoggedInTestCase,
)

from edx_notifications.lib.publisher import (
    register_notification_type,
    publish_notification_to_user,
)

from edx_notifications.data import (
    NotificationType,
    NotificationMessage,
)


class ConsumerAPITests(LoggedInTestCase):
    """
    All tests for the views.py
    """

    def setUp(self):
        """
        Build out test harnessing
        """

        self.msg_type = NotificationType(
            name='open-edx.edx_notifications.lib.tests.test_publisher'
        )
        register_notification_type(self.msg_type)

        super(ConsumerAPITests, self).setUp()

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

    def test_notification_count(self):
        """
        Simple test to make sure that we get the right count back after
        publishing a notification to this test user
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        # publish
        user_msg = publish_notification_to_user(self.user.id, msg)
        self.assertIsNotNone(user_msg)

        # now query API
        response = self.client.get(reverse('consumer.notifications.count'))
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 1)

    def test_someone_elses_notification(self):
        """
        Simple test to make sure that we can get counts for someone elses
        notification
        """

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        # publish
        user_msg = publish_notification_to_user(0, msg)
        self.assertIsNotNone(user_msg)

        # now query API
        response = self.client.get(reverse('consumer.notifications.count'))
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 0)
