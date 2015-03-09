from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise
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
        :param notification_type:
        :return:True if the correct notification type is selected successfully
        """
        self.wait_for_element_visibility('select[name="notification_type"]', 'Notification type drop down not found')
        self.q(css='select[name="notification_type"] option[value="{}"]'.format(notification_type)).first.click()
        return self.q(css='select[name="notification_type"] option[value="{}"]'.format(notification_type)).selected

    def add_notification(self):
        """
        Clicks on add notification button
        """
        initial_count = self.get_notifications_count()
        self.wait_for_element_visibility('input[name="add_notifications"]', 'Add notification button not found')
        self.q(css='input[name="add_notifications"]').click()
        self.wait_for_element_visibility('.edx-notifications-count-number', 'Notification count not found')
        EmptyPromise(
            lambda: int(self.q(css='.edx-notifications-count-number').text[0]) == initial_count + 1,
            'wait for count to increase'
        ).fulfill()

    def get_notifications_count(self):
        """
        Return notification count
        :return:
        """
        self.wait_for_element_visibility('.edx-notifications-count-number', 'Notification count not found')
        count_text = self.q(css='.edx-notifications-count-number').text[0]
        # HTML will not contain a 0 if there are no unread messages
        return int(count_text if count_text else 0)

    def verify_notifications_container_is_invisible(self):
        """
        Verify that notification container is not visible
        """
        self.wait_for_element_invisibility('.edx-notifications-container', 'Notification container is visible')

    def show_notifications_container(self):
        """
        Clicks on notification icon to display notification container
        """
        self.wait_for_element_visibility('.edx-notifications-icon', 'Notification icon not found')
        self.q(css='.edx-notifications-icon[src="/static/edx_notifications/img/notification_icon.jpg"]').click()
        self.wait_for_ajax()

    def click_notification_icon_again(self):
        """
        Clicks on notification icon again to hide notification container
        """
        self.wait_for_element_visibility('.edx-notifications-icon', 'Notification icon not found')
        self.q(css='.edx-notifications-icon[src="/static/edx_notifications/img/notification_icon.jpg"]').click()

    def verify_notifications_container_is_visible(self):
        """
        Verify that notification container is visible
        """
        self.wait_for_element_visibility('.edx-notifications-container', 'Notification container is not visible')

    def hide_notification_container(self):
        """
        Click the Hide tab to hide the notification container
        """
        self.q(css='.edx-notifications-container .edx-notifications-icon').click()

    def return_notifications_container_tabs(self):
        """
        :return: The text of all notification tabs
        """
        return self.q(css='.edx-notifications-container .notifications_list_tab>li>a').text

    def select_view_all_tab(self):
        """
        Click on view all tab
        """
        self.q(css='.edx-notifications-content .user_notifications_all>a').click()
        self.wait_for_element_visibility(
            '.edx-notifications-content .user_notifications_all.active',
            'wait for tab to get selected'
        )

    def return_selected_tab(self):
        return self.q(css='.actions>.notifications_list_tab>li[class*="active"]>a').text[0]

    def return_unread_notifications_count(self):
        """
        Return the number of items in unread notification tab
        If number of items is 1, check whether it is a message of empty list, if so return o
        :return:
        """
        self.wait_for_element_visibility('.edx-notifications-content>ul>li>p', 'list not found')
        unread_notifications_count = len(self.q(css='.edx-notifications-content>ul>li>p'))
        if unread_notifications_count == 1:
            check_text = self.q(css='.edx-notifications-content>ul>li>p').text[0]
            if 'no unread notifications' in check_text:
                return 0
        return unread_notifications_count

    def return_view_all_notifications_count(self):
        """
        Return the number of items in view all tab
        If number of items is 1, check whether it is a message of empty list, if so return o
        :return:
        """
        self.wait_for_element_visibility('.edx-notifications-content>ul>li>p', 'list not found')
        notifications_count = len(self.q(css='.edx-notifications-content>ul>li>p'))
        if notifications_count == 1:
            check_text = self.q(css='.edx-notifications-content>ul>li>p').text[0]
            if 'no unread notifications' in check_text:
                return 0
        return notifications_count

    def return_unread_notifications_list(self):
        """
        :return:List of all unread notifications
        """
        self.wait_for_element_visibility('.edx-notifications-content>ul>li>p', 'list not found')
        return self.q(css='.edx-notifications-content>ul>li>p').text

    def return_view_all_notifications_list(self):
        """
        :return:List of all notifications in view all tab
        """
        self.wait_for_element_visibility('.edx-notifications-content>ul>li>p', 'list not found')
        return self.q(css='.edx-notifications-content>ul>li>p').text

    def mark_as_read(self):
        """
        Click on mark as read link to mark all unread notifications as read
        """
        self.q(css='.edx-notifications-container .mark_notifications_read>a').click()
        self.wait_for_ajax()
        self.wait_for_element_visibility('.edx-notifications-content', 'Notification messages list not found')
        return self.q(css='.edx-notifications-content').text
