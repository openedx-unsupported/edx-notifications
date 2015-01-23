"""
Unit tests to exercise code implemented in utils.py
"""

from django.test import TestCase

from notifications.data import (
    BaseDataObject
)


class TestUtils(TestCase):
    """
    Go through utils.py and exercise some tests
    """

    def test_base_data_object(self):
        """
        Make sure we can initialize a new class using kwargs
        """

        class TestObject(BaseDataObject):
            """
            test class
            """

            test_variable = None

        test_class = TestObject(test_variable='foo')
        self.assertEquals(test_class.test_variable, 'foo')

        with self.assertRaises(ValueError):
            TestObject(doesnt_exist='bar')
