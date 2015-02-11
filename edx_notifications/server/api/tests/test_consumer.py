# pylint: disable=invalid-name
#
# We like descriptive test names, pylint is too strict with method name lengths

"""
All tests for the test_consumer.py
"""

import json

from django.test.client import Client
from django.core.urlresolvers import reverse, NoReverseMatch

from .utils import (
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

from edx_notifications.renderers.basic import (
    BasicSubjectBodyRenderer
)

from edx_notifications.server.api.urls import urlpatterns


class ConsumerAPITests(LoggedInTestCase):
    """
    All tests for the views.py
    """

    def setUp(self):
        """
        Build out test harnessing
        """

        self.msg_type = NotificationType(
            name='open-edx.edx_notifications.lib.tests.test_publisher',
            renderer='edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
        )
        register_notification_type(self.msg_type)

        super(ConsumerAPITests, self).setUp()

    def test_no_anonymous_access(self):
        """
        Make sure we cannot access any API methods without being logged in
        """

        self.client = Client()  # use AnonymousUser on the API calls

        for urlpattern in urlpatterns:
            if hasattr(urlpattern, 'name'):
                try:
                    response = self.client.get(reverse(urlpattern.name))
                except NoReverseMatch:
                    # some of our URL mappings may require a argument substitution
                    response = self.client.get(reverse(urlpattern.name, args=[0]))

                self.assertEqual(response.status_code, 403)

    def test_get_renderer_templates(self):
        """
        Make sure we can get URLs to the Underscore templates for the
        renderer that we registered for our MessageType
        """

        response = self.client.get(
            reverse('edx_notifications.consumer.renderers.templates')
        )
        self.assertEqual(response.status_code, 200)

        result_dict = json.loads(response.content)
        self.assertEqual(len(result_dict), 1)
        self.assertIn(
            'edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
            result_dict
        )
        self.assertEqual(
            result_dict['edx_notifications.renderers.basic.BasicSubjectBodyRenderer'],
            BasicSubjectBodyRenderer().underscore_template_path
        )

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

        # publish to some other user_id
        user_msg = publish_notification_to_user(99999, msg)
        self.assertIsNotNone(user_msg)

        # now query API
        response = self.client.get(reverse('edx_notifications.consumer.notifications.count'))
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)
        self.assertIn('count', results)
        self.assertEqual(results['count'], 0)

    def _publish_test_notification(self):
        """
        Helper method to set up a notification to test against
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

        return user_msg

    def test_get_single_notification(self):
        """
        Tests reading of a notification
        """

        user_msg = self._publish_test_notification()

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
            args=[99999999]
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

    def _mark_notification_as_read(self, user_msg, read=True):
        """
        Helper method to call API to mark user msg as read or unread
        """

        response = self.client.post(
            reverse(
                'edx_notifications.consumer.notifications.detail',
                args=[user_msg.msg.id]
            ),
            {
                'mark_as': 'read' if read else 'unread',
            }
        )
        self.assertEqual(response.status_code, 200)

    def _assert_expected_counts(self, expected_cnt, read_filter=True):
        """
        Helper method to query counts (with appropriate filter) and
        then assert count returned by API
        """
        # now do query with a 'read' filter
        response = self.client.get(
            reverse('edx_notifications.consumer.notifications'),
            {
                'read': read_filter,
                'unread': not read_filter,
            }
        )
        self.assertEqual(response.status_code, 200)

        results = json.loads(response.content)

        # did we get back what we expected?
        self.assertEqual(len(results), expected_cnt)

    def test_mark_notification_as_read(self):
        """
        Create a test notification and mark it as read and then
        verify results
        """

        user_msg = self._publish_test_notification()

        self._mark_notification_as_read(user_msg)

        self._assert_expected_counts(1, read_filter=True)
        self._assert_expected_counts(0, read_filter=False)

    def test_toggle_read_unread(self):
        """
        Create a test notification and toggle it as read and then back to unread
        """

        user_msg = self._publish_test_notification()

        self._mark_notification_as_read(user_msg)

        self._assert_expected_counts(1, read_filter=True)
        self._assert_expected_counts(0, read_filter=False)

        # toggle back to unread
        self._mark_notification_as_read(user_msg, read=False)

        self._assert_expected_counts(0, read_filter=True)
        self._assert_expected_counts(1, read_filter=False)

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

    def test_bad_user_msg_update(self):
        """
        Pass in an invalid data parameter to the notification update endpoing and
        make sure we get back a 400 error
        """

        user_msg = self._publish_test_notification()

        response = self.client.post(
            reverse(
                'edx_notifications.consumer.notifications.detail',
                args=[user_msg.msg.id]
            ),
            {
                'bad': 'value',
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_update_missing_user_msg(self):
        """
        Try to update a user msg which does not exist
        """

        response = self.client.post(
            reverse(
                'edx_notifications.consumer.notifications.detail',
                args=[9999999999]
            ),
            {
                'mark_as': 'read',
            }
        )
        self.assertEqual(response.status_code, 404)
