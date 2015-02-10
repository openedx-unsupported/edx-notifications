import unittest
from bok_choy.web_app_test import WebAppTest
from pages import user_email, password
from pages.home_page import HomePage
from pages.registration_page import RegistrationPage, RegistrationSuccess
from pages.login_page import LoginPage
from pages.logged_in_home_page import LoggedInHomePage
import uuid


class TestLoginSuccess(WebAppTest):


    def setUp(self):
        super(TestLoginSuccess, self).setUp()
        self.browser.maximize_window()
        self.home_page = HomePage(self.browser)
        self.registration_page = RegistrationPage(self.browser)
        self.registration_success = RegistrationSuccess(self.browser)
        self.login_page = LoginPage(self.browser)
        self.logged_in_home_page = LoggedInHomePage(self.browser)


    def test_00_login(self):
        """
        Login success Test
        """
        user_name = str(uuid.uuid4())[:8]
        print(user_name)
        self.home_page.visit()
        self.home_page.go_to_registration_page()
        self.registration_page.register(user_name, user_email, password)
        self.registration_success.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.logged_in_home_page.add_notification()


if __name__ == '__main__':
    unittest.main()

