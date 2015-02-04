# pylint: disable=invalid-name
#
# We like descriptive test names, pylint is too strict with method name lengths

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

from edx_notifications.lib.consumer import (
    mark_notification_read,
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
        response = self.client.get(reverse('edx_notifications.consumer.notifications.count'))
        self.assertEqual(response.status_code, 403)

    def test_empty_notification_count(self):
        """
        Simple test to make sure that a new user does not have
        any notifications
        """

        response = self.client.get(reverse('edx_notifications.consumer.notifications.count'))
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

        url = reverse('edx_notifications.consumer.notifications.count')

        # now query API
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 1)

        # query just the unread
        response = self.client.get(url, {'read': False, 'unread': True})
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 1)

        # query just the read, which should be 0
        response = self.client.get(url, {'read': True, 'unread': False})
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 0)

        # now mark the message as read
        mark_notification_read(self.user.id, user_msg.msg.id)

        # query just the unread, should be 0
        response = self.client.get(url, {'read': False, 'unread': True})
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 0)

        # query just the read, which should be 1
        response = self.client.get(url, {'read': True, 'unread': False})
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 1)

    def test_get_counts_bad_request(self):
        """
        Test Case for retrieving multiple notifications
        """

        response = self.client.get(
            reverse('edx_notifications.consumer.notifications.count'),
            {
                'read': 'yes-please'
            }
        )
        self.assertEqual(response.status_code, 400)

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
        response = self.client.get(reverse('edx_notifications.consumer.notifications.count'))
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 0)

    def test_get_single_notification(self):
        """
        Tests reading of a notification
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

        response = self.client.get(reverse(
            'edx_notifications.consumer.notifications.detail',
            args=[user_msg.msg.id]
        ))
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)

        self.assertEqual(results['user_id'], self.user.id)
        self.assertIsNone(results['read_at'])
        self.assertEqual(results['msg']['namespace'], 'test-runner')
        self.assertEqual(results['msg']['msg_type']['name'], 'open-edx.edx_notifications.lib.tests.test_publisher')

    def test_get_notification_not_found(self):
        """
        Test case where a notification cannot be found
        """

        response = self.client.get(reverse(
            'edx_notifications.consumer.notifications.detail',
            args=[0]
        ))
        self.assertEqual(response.status_code, 404)

    def _compare_user_msg_to_result(self, original, api_result):
        """
        Helper to compare a notification with the data that was returned
        """

        self.assertEqual(api_result['user_id'], original.user_id)
        self.assertIsNone(api_result['read_at'])
        self.assertEqual(api_result['msg']['namespace'], original.msg.namespace)
        self.assertEqual(api_result['msg']['msg_type']['name'], original.msg.msg_type.name)
        self.assertEqual(api_result['msg']['payload'], original.msg.payload)

    def test_multiple_notifications(self):
        """
        Test Case for retrieving multiple notifications
        """

        msg1 = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'foo': 'bar'
            }
        )

        msg2 = NotificationMessage(
            namespace='test-runner',
            msg_type=self.msg_type,
            payload={
                'second': 'one'
            }
        )

        # publish
        user_msg1 = publish_notification_to_user(self.user.id, msg1)
        user_msg2 = publish_notification_to_user(self.user.id, msg2)

        response = self.client.get(reverse('edx_notifications.consumer.notifications'))
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertEqual(len(results), 2)

        # the last one written should be the first one read
        self._compare_user_msg_to_result(user_msg2, results[0])
        # the first one written should be second one received
        self._compare_user_msg_to_result(user_msg1, results[1])

        # now do query with a namespace filter
        response = self.client.get(
            reverse('edx_notifications.consumer.notifications'),
            {
                'namespace': 'test-runner'
            }
        )
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertEqual(len(results), 2)  # did we get two back?

        self._compare_user_msg_to_result(user_msg2, results[0])
        self._compare_user_msg_to_result(user_msg1, results[1])

    def test_get_notifications_bad_request(self):
        """
        Test Case for retrieving multiple notifications
        """

        response = self.client.get(
            reverse('edx_notifications.consumer.notifications'),
            {
                'read': 'yes-please'
            }
        )
        self.assertEqual(response.status_code, 400)
