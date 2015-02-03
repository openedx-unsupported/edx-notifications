"""
All tests for the views.py
"""

from .utils import LoggedInTestCase

from django.test.client import Client
from django.core.urlresolvers import reverse


class ViewTests(LoggedInTestCase):
    """
    All tests for the views.py
    """

    def test_unauthenticated_access(self):
        """
        Assert that we cannot access the endpoints without being logged in
        """

        self.client = Client()
        response = self.client.get(reverse('web.notifications.count'))

        self.assertEquals(response.status_code, 403)

    def test_notification_count(self):
        """
        Asserts that a new user has no notifications
        """

        response = self.client.get(reverse('web.notifications.count'))

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Notifications (0)')
