from bok_choy.page_object import PageObject
from login_page import LoginPage


class RegistrationPage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        Return True if register button is present on page
        :return:
        """
        return self.q(css='input[value="Register"]').present

    def register(self, username, email, password):
        """
        Gets username, email, password as parameters and fill the registration form using these
        Clicks on the register button to complete registration
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
        Return True if registration success message is present on page
        :return:
        """
        if not self.q(css='html>body>h1').text:
            return False
        return 'Registration Completed Successfully' in self.q(css='html>body>h1').text[0]

    def go_to_login_page(self):
        """
        Click on the login link to go to login page
        """
        self.q(css='html>body>a').click()
        LoginPage(self.browser).wait_for_page()



