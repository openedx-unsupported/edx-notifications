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
)
from edx_notifications.channels.urban_airship import UrbanAirshipNotificationChannelProvider
from testserver.views import CANNED_TEST_PAYLOAD

TEST_TAG = 'cs50'
TEST_DATE = 20100101
TEST_USER = 123


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

    def test_bulk_publish_notification(self):
        """
        Test publish notification to a tag group
        :return:
        """
        self.msg.payload['announcement_date'] = TEST_DATE
        self.msg.payload['group'] = 'enrollments'
        self.msg.namespace = TEST_TAG
        obj = UrbanAirshipNotificationChannelProvider\
            .bulk_create_payload(self.msg)

        self.assertTrue(obj)
        self.assertTrue(obj['notification'])
        self.assertTrue(obj['notification']['alert'])
        self.assertTrue(obj['device_types'])
        self.assertTrue(obj['audience'])

    def test_publish_notification_user(self):
        """
        Test publish notification to a single user
        :return:
        """
        obj = UrbanAirshipNotificationChannelProvider.create_payload(
            self.msg, TEST_USER)
        self.assertTrue(obj)
        self.assertTrue(obj['notification'])
        self.assertTrue(obj['notification']['alert'])
        self.assertTrue(obj['device_types'])
        self.assertTrue(obj['audience'])
