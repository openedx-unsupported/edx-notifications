from bok_choy.page_object import PageObject
from logged_in_home_page import LoggedInHomePage
from . import default_timeout


class LoginPage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        Return True if login button is present on page
        :return:
        """
        return self.q(css='input[value="Login"]').present

    def login_to_application(self, username, password):
        """
        Get username, password as parameters and provide these in relevant input boxes
        Click the submit button and check if there is any error return message
        otherwise go to logged in page
        :param username:
        :param password:
        """
        self.q(css='#id_username').fill(username)
        self.q(css='#id_password').fill(password)
        self.q(css='input[value="Login"]').click()
        self.wait_for_element_visibility('html>body>p', 'text not found', timeout=default_timeout)
        if "username and password didn't match" in self.q(css='html>body>p').text[0]:
            return "User not registered"
        else:
            LoggedInHomePage(self.browser).wait_for_page()