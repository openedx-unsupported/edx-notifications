from bok_choy.page_object import PageObject


class LoggedOut(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        True if login button is present on page
        """
        self.wait_for_element_visibility('input[value="Login"]', 'Login button not found', timeout=20)
        return True
