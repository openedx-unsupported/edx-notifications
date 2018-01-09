from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise
from . import user_name, default_timeout
from notification_target_page import NotificationTargetPage
from logout_page import LoggedOut
from selenium.webdriver import ActionChains


class LoggedInHomePage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        Return True if welcome message is displayed at top
        :return:
        """
        welcome_message = "Welcome " + user_name + " !!!"
        self.wait_for_element_visibility('html>body>p', 'Para not found', timeout=default_timeout)
        return welcome_message in self.q(css='html>body>p').text[0]

    def select_notification_type(self, notification_type):
        """
        Gets notification type as parameter and select this notification type from drop down.
        Also checks if the correct notification type is selected successfully
        :param notification_type:
        """
        self.wait_for_element_visibility(
            'select[name="notification_type"]',
            'Notification type drop down not found',
            timeout=default_timeout
        )
        self.q(css='select[name="notification_type"] option[value="{}"]'.format(notification_type)).first.click()
        EmptyPromise(
            lambda:
            self.q(css='select[name="notification_type"] option[value="{}"]'.format(notification_type)).selected,
            "selected notification type is not correct",
            timeout=default_timeout
        ).fulfill()

    def add_notification(self):
        """
        Clicks on add notification button
        """
        initial_count = self.get_notifications_count()
        self.wait_for_element_visibility(
            'input[name="add_notifications"]',
            'Add notification button not found',
            timeout=default_timeout
        )
        self.q(css='input[name="add_notifications"]').click()
        self.wait_for_element_visibility('.xns-counter', 'Notification count not found', timeout=default_timeout)
        final_count = str(initial_count + 1)
        EmptyPromise(
            lambda: self.q(css='.xns-counter').text[0] == final_count,
            'wait for count to increase',
            timeout=default_timeout
        ).fulfill()

    def get_notifications_count(self):
        """
        Return notification count
        :return:
        """
        self.wait_for_element_visibility('.xns-counter', 'Notification count not found', timeout=default_timeout)
        count_text = self.q(css='.xns-counter').text[0]
        return int(count_text if count_text else 0)

    def verify_notifications_container_is_invisible(self):
        """
        Verify that notification container is not visible
        """
        self.wait_for_element_invisibility('.xns-pane', 'Notification container is visible', timeout=default_timeout)

    def show_notifications_container(self):
        """
        Clicks on notification icon to display notification container
        """
        self.wait_for_element_visibility('.xns-icon', 'Notification icon not found', timeout=default_timeout)
        self.q(css='.xns-icon[src="/static/edx_notifications/img/notification_icon.jpg"]').click()
        self.wait_for_ajax()

    def hide_notification_container(self):
        """
        Clicks on notification icon again to hide notification container
        """
        self.wait_for_element_visibility('.xns-icon', 'Notification icon not found', timeout=default_timeout)
        self.q(css='.xns-icon[src="/static/edx_notifications/img/notification_icon.jpg"]').click()

    def hide_notification_container_using_hide_link(self):
        """
        Clicks on hide link to hide notification container
        """
        self.wait_for_element_visibility('.xns-hide-pane>a', 'Hide link not found', timeout=default_timeout)
        self.q(css='.xns-hide-pane>a').click()

    def verify_notifications_container_is_visible(self):
        """
        Verify that notification container is visible
        """
        self.wait_for_element_visibility(
            '.xns-pane',
            'Notification container is not visible',
            timeout=default_timeout
        )

    def return_notifications_container_tabs(self):
        """
        :return: The text of all notification tabs
        """
        return self.q(css='.xns-container .xns-tab-list>li>a').text

    def select_view_all_tab(self):
        """
        Click on view all tab
        """
        self.q(css='.xns-content .xns-all-action>a').click()
        self.wait_for_element_visibility(
            '.xns-content .xns-all-action.active',
            'wait for tab to get selected'
        )

    def return_selected_tab(self):
        return self.q(css='.xns-actions>.xns-tab-list>li[class*="active"]>a').text[0]

    def return_unread_notifications_count(self):
        """
        Return the number of items in unread notification tab
        If number of items is 1, check whether it is a message of empty list, if so return o
        :return:
        """
        self.wait_for_element_visibility('.xns-items', 'list not found', timeout=default_timeout)
        unread_notifications_count = len(self.q(css='.xns-item-body'))
        return unread_notifications_count

    def return_view_all_notifications_count(self):
        """
        Return the number of items in view all tab
        If number of items is 1, check whether it is a message of empty list, if so return o
        :return:
        """
        self.wait_for_element_visibility('.xns-items', 'list not found', timeout=default_timeout)
        notifications_count = len(self.q(css='.xns-item-body'))
        return notifications_count

    def return_notifications_list(self, key):
        """
        :return:List of all unread notifications
        """
        group = ''
        if 'announcements' in key:
            group = 'announcements'
        elif 'group-project' in key:
            group = 'group_work'
        elif 'discussions' in key:
            if 'discussions.cohorted' in key:
                group = 'group_work'
            else:
                group = 'discussions'
        elif 'leaderboard' in key:
            group = 'leaderboards'
        self.wait_for_element_visibility('.xns-items', 'list not found', timeout=default_timeout)
        return self.q(css='.xns-items .xns-item .xns-item-body>span[class="xns-' + group + '"]').text

    def mark_as_read(self):
        """
        Click on mark as read link to mark all unread notifications as read
        """
        self.q(css='.xns-mark-read-action>a').click()
        self.wait_for_ajax()
        self.wait_for_element_visibility(
            '.xns-content',
            'Notification messages list not found',
            timeout=default_timeout
        )
        return self.q(css='.xns-content').text

    def click_on_notification(self):
        """
        Click on individual notification, if it contains a valid url, go to this
        site and return url otherwise just return text "No target link"
        :return:
        """
        self.wait_for_element_visibility('.xns-items', 'list not found', timeout=default_timeout)
        notification_link = self.q(css='.xns-items .xns-item-body>span').first.attrs('data-click-link')
        self.q(css='.xns-items .xns-item-body>span').first.click()
        if notification_link[0] != "":
            NotificationTargetPage(self.browser).wait_for_page()
            return notification_link[0]
        else:
            self.wait_for_ajax()
            return "No target link"

    def log_out(self):
        """
        Click on the logout link
        """
        self.wait_for_element_visibility('a[href="/logout/"]', 'logout link not found', timeout=default_timeout)
        self.q(css='a[href="/logout/"]').click()
        LoggedOut(self.browser).wait_for_page()

    def set_namespace(self, namespace):
        """
        Select value of namespace from drop down and set the selected namespace,
        check if it is set or not
        :param namespace:
        """
        self.wait_for_element_visibility(
            'select[name="namespace"]',
            'Notification type drop down not found',
            timeout=20
        )
        self.q(css='select[name="namespace"] option[value="{}"]'.format(namespace)).first.click()
        EmptyPromise(
            lambda: self.q(css='select[name="namespace"] option[value="{}"]'.format(namespace)).selected,
            "selected notification type is not correct",
            timeout=20
        ).fulfill()
        self.wait_for_element_visibility(
            'input[name="change_namespace"]',
            'button not found',
            timeout=default_timeout
        )
        self.q(css='input[name="change_namespace"]').click()
        self.wait_for_ajax()
        EmptyPromise(
            lambda: namespace in self.q(css='html>body>h2:nth-of-type(1)').text[0],
            "name space is not changed",
            timeout=default_timeout
        ).fulfill()

    def close_notification(self):
        action = ActionChains(self.browser)
        self.wait_for_element_presence(
            '.xns-content.xns-pane-unread .xns-close-item',
            'close icon not found',
            timeout=default_timeout
        )
        notification = self.browser.find_element_by_css_selector('.xns-items .xns-item-body')
        icon = self.browser.find_element_by_css_selector(".xns-items .xns-close-item-x")
        action.move_to_element(notification).move_to_element(icon).click().perform()
        self.wait_for_element_presence(
            '.xns-content.xns-pane-unread .xns-empty-list',
            'List is not empty yet',
            timeout=default_timeout
        )
