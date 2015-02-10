from bok_choy.page_object import PageObject
from . import base_url


class LoginPage(PageObject):

    url = base_url

    def is_browser_on_page(self):
        """
        :return: True if login is found in driver title
        """
        return "login" in self.browser.title.lower()

    def login(self, username, password):
        """
        Provide username, password and click on submit button
        :param username:
        :param password:
        """
        self.q(css='#id_username').fill(username)
        self.q(css='#id_password').fill(password)
        self.q(css='input[value="Login"]').click()

    def perform_validation(self):
        """
        :return: text of error message
        """
        return self.q(css='html>body>p').text[0]

