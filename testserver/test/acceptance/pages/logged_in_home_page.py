from bok_choy.page_object import PageObject


class LoggedInHomePage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        :return: True if welcome message is displayed at top
        """
        return 'Welcome' in self.q(css='html>body>p').text[0]

    def add_notification(self):
        """
        Add notification
        """
        self.wait_for_element_visibility('input[value="add a notification"]', 'wait for add notification button')