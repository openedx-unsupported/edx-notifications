__author__ = 'kashif'

import unittest

from bok_choy.web_app_test import WebAppTest
from pages.login_page import LoginPage


class TestLogin(WebAppTest):


    def setUp(self):
        super(TestLogin, self).setUp()
        self.browser.maximize_window()
        self.login_page = LoginPage(self.browser)

    def test_00_login(self):
        # from nose.tools import set_trace; set_trace()
        self.login_page.visit()
        self.login_page.is_browser_on_page()
        self.login_page.login('kashif', '786open')
        error_msg =self.login_page.perform_validation()
        self.assertIn('match', error_msg)

if __name__ == '__main__':
    unittest.main()
