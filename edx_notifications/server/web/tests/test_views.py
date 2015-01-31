"""
All tests for the views.py
"""

from django.test import TestCase
from django.contrib.auth.models import User

from .utils import TestClient


class ViewTests(TestCase):
    """
    All tests for the views.py
    """

    def setUp(self):
        """
        Setup for tests
        """

        self.client = TestClient()
        user = User(username='tester')
        user.save()
        self.client.login_user(user)

    def test_homepage(self):
        """
        Can we access the root
        """

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello')
