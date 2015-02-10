from bok_choy.page_object import PageObject
from registration_page import RegistrationPage
from login_page import LoginPage
from . import base_url


class HomePage(PageObject):

    url = base_url

    def is_browser_on_page(self):
        """
        :return: True if login is found in driver title
        """
        return "login" in self.browser.title.lower()

    def go_to_registration_page(self):
        self.wait_for_element_presence('a[href="/register"]', 'wait for registration link')
        self.q(css='a[href="/register"]').click()
        RegistrationPage(self.browser).wait_for_page()

    def go_to_login_page(self):
        self.wait_for_element_presence('input[value="Login"]', 'wait for login button')
        LoginPage(self.browser).wait_for_page()
