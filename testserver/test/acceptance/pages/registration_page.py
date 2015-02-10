from bok_choy.page_object import PageObject
from login_page import LoginPage
from . import base_url


class RegistrationPage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        :return: True if register button is present on page
        """
        return self.q(css='input[value="Register"]').present

    def register(self, username, email, password):
        """
        Provide username, email, password and click on register button
        :param username:
        :param email:
        :param password:
        """
        self.q(css='#id_username').fill(username)
        self.q(css='#id_email').fill(email)
        self.q(css='#id_password1').fill(password)
        self.q(css='#id_password2').fill(password)
        self.q(css='input[value="Register"]').click()
        RegistrationSuccess(self.browser).wait_for_page()


class RegistrationSuccess(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        :return: True if registration success message is present on page
        """
        return 'Registration Completed Successfully' in self.q(css='html>body>h1').text[0]


    def go_to_login_page(self):
        self.q(css='html>body>a').click()
        LoginPage(self.browser).wait_for_page()



