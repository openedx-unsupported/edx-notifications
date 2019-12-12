"""
Tests for the administration endpoints
"""
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from edx_notifications.server.api.tests.utils import TestClient


class AdminAPITests(TestCase):
    """
    Tests for the admin.py
    """

    def setUp(self):
        """
        Create clients
        """

        self.admin_client = TestClient()
        self.admin_user = User(username='admin', is_staff=True)
        self.admin_user.save()
        self.admin_client.login_user(self.admin_user)

        self.client = TestClient()
        self.user = User(username='user', is_staff=False)
        self.user.save()
        self.client.login_user(self.user)

    def test_purge_user_data(self):
        """
        Make sure purging user data works
        """

        response = self.admin_client.post(
            reverse('edx_notifications.admin.delete_users_data'),
            {'user_ids': [self.admin_user.id]}
        )
        self.assertEqual(response.status_code, 204)

    def test_admin_required_to_purge(self):
        """
        Make sure purging is only available to staff users
        """

        response = self.client.post(
            reverse('edx_notifications.admin.delete_users_data'),
            {'user_ids': [self.admin_user.id]}
        )
        self.assertEqual(response.status_code, 403)
