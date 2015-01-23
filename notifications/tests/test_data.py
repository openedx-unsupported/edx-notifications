"""
Unit tests to exercise code implemented in data.py
"""

from django.test import TestCase

from notifications.data import (
    BaseDataObject
)


class TestUtils(TestCase):
    """
    Go through data.py and exercise some tests
    """

    def test_base_data_object(self):
        """
        Assert proper behavior with BaseDataObject
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

        # make sure we are not allowed to add on new
        # attributes after initialization
        obj = TestObject(test_variable='foo')
        with self.assertRaises(ValueError):
            obj.blow_up_now = True  # pylint: disable=attribute-defined-outside-init
