"""
Unit tests for utils.py
"""

from django.test import TestCase

from edx_notifications.server.web.utils import get_notifications_widget_context


class TestUtils(TestCase):
    """
    Unit tests for the utils.py file
    """

    def test_get_widget_context(self):
        """
        Make sure we get the render context that we expect
        """

        render_context = get_notifications_widget_context()

        self.assertIn('endpoints', render_context)

        endpoints = render_context['endpoints']
        self.assertIn('unread_notification_count', endpoints)
        self.assertIn('user_notifications', endpoints)
        self.assertIn('renderer_templates_urls', endpoints)

        self.assertIn('view_templates', render_context)
        view_templates = render_context['view_templates']

        self.assertIn('notification_icon', view_templates)
        self.assertIn('notification_pane', view_templates)
