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
        'open-edx.studio.announcements.new_announcement': 'There is a new Course Update available',
        'testserver.type1': 'Here is test notification that has a simple subject and body'
    }

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

    def test_03_add_notifications(self):
        """
        Scenario: Clicking on the add notification button after selecting a notification type increases the
        notification count by 1 and add a relevant message.
        Given that I am on the notification home page
        When I click the add notification button after selecting a notification type
        Then I should see the notification count increase by 1
        When I click the notification icon
        Then I see the specific message relevant to notification type added as a last ember of list
        And I am able to repeat the whole process for all notification types
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        for key, value in self.notification_dict.iteritems():
            initial_notification_count = self.logged_in_home_page.get_notifications_count()
            self.assertTrue(self.logged_in_home_page.select_notification_type(key))
            self.logged_in_home_page.add_notification()
            final_notification_count = self.logged_in_home_page.get_notifications_count()
            self.assertEqual(final_notification_count, initial_notification_count + 1)
            notification_message = self.logged_in_home_page.get_notification_messages()
            self.assertIn(value, notification_message[-1])