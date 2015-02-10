import unittest
from bok_choy.web_app_test import WebAppTest
from pages.home_page import HomePage
from pages.login_page import LoginPage


class TestLoginFailure(WebAppTest):


    def setUp(self):
        super(TestLoginFailure, self).setUp()
        self.browser.maximize_window()
        self.home_page = HomePage(self.browser)
        self.login_page = LoginPage(self.browser)

    def test_00_unsuccessful_login(self):
        """
        Login failure Test
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials('abc', '123')
        error_msg =self.login_page.submit_incorrect_credentials()
        self.assertIn('match', error_msg)

if __name__ == '__main__':
    unittest.main()
