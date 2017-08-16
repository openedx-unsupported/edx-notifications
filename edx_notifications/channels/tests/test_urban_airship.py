"""
Test cases for UA API
"""
from django.test import TestCase

from edx_notifications import startup
from edx_notifications.data import (
    NotificationMessage,
    NotificationType,
)
from edx_notifications.lib.publisher import (
    register_notification_type,
    bulk_publish_notification_to_users)
from testserver.views import CANNED_TEST_PAYLOAD

TEST_TAG = 'cs50'
TEST_DATE = 20100101


class UrbanAirTestCases(TestCase):
    """
    Test cases for urban airship channel
    """
    def setUp(self):
        """
        Sets up test environments
        :return:
        """
        startup.initialize(register_system_types=False)
        self.msg_type = NotificationType(
            name='open-edx.studio.announcements.new-announcement',
            renderer='edx_notifications.openedx.course_announcements.NewCourseAnnouncementRenderer'
        )
        register_notification_type(self.msg_type)
        self.msg = NotificationMessage(
            namespace='foo/bar/baz',
            msg_type=self.msg_type,
            payload=CANNED_TEST_PAYLOAD['open-edx.studio.announcements.new-announcement']
        )

    def test_publish_notification_tag(self):
        """
        Test publish notification to a tag group
        :return:
        """
        self.msg.payload['announcement_date'] = TEST_DATE
        channel_context = {'group': 'enrollments', 'tag': TEST_TAG}
        resp = bulk_publish_notification_to_users([], self.msg,
                                                  channel_context=channel_context)
        self.assertTrue(resp)
        self.assertTrue(resp['ok'])
