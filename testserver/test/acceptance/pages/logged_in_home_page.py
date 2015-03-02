from bok_choy.page_object import PageObject
from . import user_name


class LoggedInHomePage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        Return True if welcome message is displayed at top
        :return:
        """
        welcome_message = "Welcome " + user_name + " !!!"
        self.wait_for_element_visibility('html>body>p', 'Para not found')
        return welcome_message in self.q(css='html>body>p').text[0]

    def select_notification_type(self, notification_type):
        """
        Gets notification type as parameter and select this notification type from drop down.
        Returns true if the correct notification type is selected successfully
        :param notification_type:
        :return:
        """
        self.wait_for_element_visibility('select[name="notification_type"]', 'Notification type drop down not found')
        self.q(css='select[name="notification_type"] option[value="{}"]'.format(notification_type)).first.click()
        return self.q(css='select[name="notification_type"] option[value="{}"]'.format(notification_type)).selected

    def add_notification(self):
        """
        Clicks on add notification button
        """
        self.wait_for_element_visibility('input[name="add_notifications"]', 'Add notification button not found')
        self.q(css='input[name="add_notifications"]').click()

    def get_notifications_count(self):
        """
        Return notification count
        :return:
        """
        self.wait_for_element_visibility('.edx-notifications-count-number', 'Notification count not found')
        text = self.q(css='.edx-notifications-count-number').text[0]
        # We don't display a 0 count, but it is left blank when there are no unread notifications
        return int(text) if text else 0

    def get_notification_messages(self):
        """
        Clicks on notification icon to display list of notification messages
        Return all these messages as a list
        :return:
        """
        self.wait_for_element_visibility('.edx-notifications-icon', 'Notification icon not found')
        self.q(css='.edx-notifications-icon[src="/static/edx_notifications/img/notification_icon.jpg"]').click()
        self.wait_for_ajax()
        self.wait_for_element_visibility('.edx-notifications-list', 'Notification messages list not found')
        return self.q(css='.edx-notifications-list').text
