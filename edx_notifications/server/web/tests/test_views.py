"""
All tests for the views.py
"""

from django.test import TestCase


class ViewTests(TestCase):
    """
    All tests for the views.py
    """

    def test_homepage(self):
        """
        Can we access the root
        """

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello')
