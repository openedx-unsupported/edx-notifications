from bok_choy.web_app_test import WebAppTest
from pages import user_name, user_email, password
from pages.home_page import HomePage
from pages.registration_page import RegistrationPage, RegistrationSuccess
from pages.login_page import LoginPage
from pages.logged_in_home_page import LoggedInHomePage


class TestAddNotifications(WebAppTest):

    notification_dict = {
        'open-edx.lms.discussions.reply-to-thread': 'testuser has replied to a discussion posting ',
        'open-edx.lms.discussions.thread-followed': 'testuser is now following your discussion thread',
        'open-edx.lms.discussions.post-upvoted': 'testuser has upvoted your discussion thread',
        'testserver.type1': 'Here is test notification that has a simple subject and body'
    }

    notifications_container_tabs = ['View unread', 'View all', 'Mark as read', 'Hide']

    def setUp(self):
        """
        Initialize all page objects
        """
        super(TestAddNotifications, self).setUp()
        self.browser.maximize_window()
        self.home_page = HomePage(self.browser)
        self.registration_page = RegistrationPage(self.browser)
        self.registration_success = RegistrationSuccess(self.browser)
        self.login_page = LoginPage(self.browser)
        self.logged_in_home_page = LoggedInHomePage(self.browser)

    def test_00_register(self):
        """
        Scenario: User is able to register with the application
        Given that I am on the registration page
        When I provide valid values in registration form
        Then I should be shown a registration success message
        """
        self.home_page.visit()
        self.home_page.go_to_registration_page()
        self.registration_page.register(user_name, user_email, password)
        self.assertTrue(self.registration_success.is_browser_on_page())

    def test_01_login_failure(self):
        """
        Scenario: User is not able to login using invalid credentials
        Given that I am on the login page
        When I provide invalid credentials
        Then I should be shown an error message
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials('abc', '123')
        error_msg = self.login_page.submit_incorrect_credentials()
        self.assertIn('match', error_msg)

    def test_02_login_success(self):
        """
        Scenario: User is able to login using valid credentials
        Given that I am on the login page
        When I provide valid credentials
        Then I should be logged in successfully
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.assertTrue(self.logged_in_home_page.is_browser_on_page())

    def test_03_show_notifications_container(self):
        """
        Scenario: User is able to show the notification container
        Given that I am on the notification home page
        And notifications container is hidden
        When I click the notification icon
        Then I should see the notification container
        When I click on the hide link
        Then notification container becomes invisible again
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.verify_notifications_container_is_invisible()

    def test_04_hide_notifications_container_by_clicking_hide_tab(self):
        """
        Scenario: User is able to hide the notification container
        Given that I am on the notification home page
        And notifications container is visible
        When I click on the hide tab
        Then notification container should hide
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.verify_notifications_container_is_invisible()

    def test_05_hide_notifications_container_by_clicking_notification_icon_again(self):
        """
        Scenario: User is able to hide the notification container
        Given that I am on the notification home page
        And notifications container is visible
        When I click on the notification icon again
        Then notification container should hide
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.click_notification_icon_again()
        self.logged_in_home_page.verify_notifications_container_is_invisible()

    def test_06_verify_tabs_in_notifications_container(self):
        """
        Scenario: User is able to view 4 tabs namely view unread, view all, Mark as read and hide
        in notification container
        Given that I am on the notification home page
        And notifications container is hidden
        When I click the notification icon
        Then I should see the notification container
        And notification container should display 4 tabs(unread, view all, Mark as read, Hide)
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        fetched_notifications_container_tabs = self.logged_in_home_page.return_notifications_container_tabs()
        self.assertEqual(fetched_notifications_container_tabs, self.notifications_container_tabs)

    def test_07_verify_default_tab_selection(self):
        """
        Scenario: When notification container becomes visible, by default the View Unread tab is selected
        Given that I am on the notification home page
        And notifications container is hidden
        When I click the notification icon
        Then I should see the notification container
        And by default the View Unread tab should be selected
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        fetched_selected_tab = self.logged_in_home_page.return_selected_tab()
        self.assertEqual(fetched_selected_tab, self.notifications_container_tabs[0])

    def test_08_verify_unread_notifications_count(self):
        """
        Scenario: Clicking on the add notification button after selecting a notification type increases the
        unread notification count by 1.
        Given that I am on the notification home page
        When I click the notification icon after adding a notification
        Then I should see the increase in unread notification count by 1
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        for key, value in self.notification_dict.iteritems():
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            initial_unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertTrue(self.logged_in_home_page.select_notification_type(key))
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            final_unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertEqual(final_unread_notification_count, initial_unread_notification_count + 1)

    def test_09_verify_notifications_count_from_view_all_tab(self):
        """
        Scenario: Clicking on the add notification button after selecting a notification type increases the
        notification count in view all tab by 1.
        Given that I am on the notification home page
        When I click the notification icon after adding a notification
        Then I should see the increase in notification count by 1 in view all tab
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        for key, value in self.notification_dict.iteritems():
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.select_view_all_tab()
            initial_notification_count = self.logged_in_home_page.return_view_all_notifications_count()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertTrue(self.logged_in_home_page.select_notification_type(key))
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.select_view_all_tab()
            final_notification_count = self.logged_in_home_page.return_view_all_notifications_count()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertEqual(final_notification_count, initial_notification_count + 1)

    def test_10_verify_unread_notifications_text(self):
        """
        Scenario: When user adds a new notification type, the relevant message for this notification type
        appears in unread notifications tab
        Given that I am on the notification home page
        And notifications container is hidden
        When I add a specific notification type
        And click the notification icon
        Then I should see the unread notifications
        And a relevant message for the added notification type should be visible in unread notification tab
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        for key, value in self.notification_dict.iteritems():
            self.assertTrue(self.logged_in_home_page.select_notification_type(key))
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            unread_notification_list = self.logged_in_home_page.return_unread_notifications_list()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertIn(value, unread_notification_list[0])

    def test_11_verify_view_all_notifications_text(self):
        """
        Scenario: When user adds a new notification type, the relevant message for this notification type
        appears in view all notifications tab
        Given that I am on the notification home page
        And notifications container is hidden
        When I add a specific notification type
        And click the notification icon
        Then I should see the unread notifications
        And a relevant message for the added notification type should be visible in view all notification tab
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        for key, value in self.notification_dict.iteritems():
            self.assertTrue(self.logged_in_home_page.select_notification_type(key))
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.select_view_all_tab()
            notification_list = self.logged_in_home_page.return_view_all_notifications_list()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertIn(value, notification_list[0])

    def test_12_verify_mark_as_read_functionality(self):
        """
        Scenario: When user clicks on mark as read tab, notifications disappear from unread notifications
        tab
        Given that I am on the notification home page
        And there are some notifications present in unread notification tab
        When I click on mark as read link
        Then all notifications should disappear from unread notifications tab
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        for key, value in self.notification_dict.iteritems():
            self.assertTrue(self.logged_in_home_page.select_notification_type(key))
            self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.assertTrue(unread_notification_count > 1)
        self.logged_in_home_page.mark_as_read()
        unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.assertTrue(unread_notification_count == 0)