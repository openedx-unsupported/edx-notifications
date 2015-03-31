from bok_choy.page_object import PageObject
from login_page import LoginPage
from . import default_timeout

class RegistrationSuccess(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        Return True if registration success message is present on page
        :return:
        """
        self.wait_for_element_visibility('html>body>h1', 'Heading not found', timeout=default_timeout)
        return 'Registration Completed Successfully' in self.q(css='html>body>h1').text[0]

    def go_to_login_page(self):
        """
        Click on the login link to go to login page
        """
        self.q(css='a[href="/"]').filter(lambda el: el.text == 'Login').click()
        LoginPage(self.browser).wait_for_page()
