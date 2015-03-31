from bok_choy.page_object import PageObject
from registration_success_page import RegistrationSuccess


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