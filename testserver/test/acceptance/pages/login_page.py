from bok_choy.page_object import PageObject
from logged_in_home_page import LoggedInHomePage


class LoginPage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        Return True if login button is present on page
        :return:
        """
        return self.q(css='input[value="Login"]').present

    def provide_credentials(self, username, password):
        """
        Get username, password as parameters and provide these in relevant input boxes
        :param username:
        :param password:
        """
        self.q(css='#id_username').fill(username)
        self.q(css='#id_password').fill(password)

    def submit_incorrect_credentials(self):
        """
        Check for error message after incorrect credentials have been provided
        Return the error message text
        :return:
        """
        self.q(css='input[value="Login"]').click()
        return self.q(css='html>body>p').text[0]

    def submit_correct_credentials(self):
        """
        go to logged in home page after clicking login button
        """
        self.q(css='input[value="Login"]').click()
        LoggedInHomePage(self.browser).wait_for_page()
