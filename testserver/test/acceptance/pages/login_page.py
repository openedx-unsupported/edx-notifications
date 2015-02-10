from bok_choy.page_object import PageObject
from logged_in_home_page import LoggedInHomePage


class LoginPage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        :return: True if login button is present on page
        """
        return self.q(css='input[value="Login"]').present


    def provide_credentials(self, username, password):
        """
        Provide username, password
        :param username:
        :param password:
        """
        self.q(css='#id_username').fill(username)
        self.q(css='#id_password').fill(password)

    def submit_incorrect_credentials(self):
        """
        Submit incorrect answer and check for error message
        :return: text of error message
        """
        self.q(css='input[value="Login"]').click()
        return self.q(css='html>body>p').text[0]

    def submit_correct_credentials(self):
        """
        Submit answer and login
        """
        self.q(css='input[value="Login"]').click()
        LoggedInHomePage(self.browser).wait_for_page()
