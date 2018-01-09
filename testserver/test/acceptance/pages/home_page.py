from bok_choy.page_object import PageObject
from registration_page import RegistrationPage
from login_page import LoginPage
from . import base_url, default_timeout


class HomePage(PageObject):

    url = base_url

    def is_browser_on_page(self):
        """
        Return True if word login is found in driver title
        :return:
        """
        return "login" in self.browser.title.lower()

    def go_to_registration_page(self):
        """
        Click on the registration link to go to registration page
        """
        self.wait_for_element_presence('a[href="/register"]', 'Registration link not found', timeout=default_timeout)
        self.q(css='a[href="/register"]').click()
        RegistrationPage(self.browser).wait_for_page()

    def go_to_login_page(self):
        """
        Click on the login button to go to login page
        """
        self.wait_for_element_presence('input[value="Login"]', 'Login button not found', timeout=default_timeout)
        LoginPage(self.browser).wait_for_page()
