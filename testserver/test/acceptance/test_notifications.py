from bok_choy.web_app_test import WebAppTest
from testserver.bokchoy_settings import HIDE_LINK_IS_VISIBLE
from pages import user_name, user_email, password
from pages.home_page import HomePage
from pages.registration_page import RegistrationPage, RegistrationSuccess
from pages.login_page import LoginPage
from pages.logged_in_home_page import LoggedInHomePage
from pages.notification_target_page import NotificationTargetPage
from unittest import skipUnless


class TestAddNotifications(WebAppTest):

    notification_dict = {
        'open-edx.studio.announcements.new-announcement': 'There is a new Course Update available',
        'open-edx.lms.discussions.reply-to-thread': 'testuser has replied to a discussion posting ',
        'open-edx.lms.discussions.thread-followed': 'testuser is now following your discussion thread',
        'open-edx.lms.discussions.post-upvoted': 'testuser has upvoted your discussion thread',
        'open-edx.lms.discussions.cohorted-thread-added': 'testuser has added to a new posting to a private discussion',
        'open-edx.lms.discussions.cohorted-comment-added': 'testuser has added to a new comment',
        'open-edx.lms.discussions.comment-upvoted': 'testuser has upvoted your comment',
        'open-edx.lms.leaderboard.progress.rank-changed': 'You are now #2 in Progress in the cohort!',
        'open-edx.lms.leaderboard.gradebook.rank-changed': 'You are now #3 for Proficiency in the cohort!',
        'open-edx.xblock.group-project.file-uploaded': 'First Activity: testuser uploaded a file',
        'open-edx.xblock.group-project.uploads-open': 'First Activity: Uploads are open',
        'open-edx.xblock.group-project.uploads-due': 'First Activity: Uploads are due',
        'open-edx.xblock.group-project.reviews-open': 'First Activity: Review(s) are open',
        'open-edx.xblock.group-project.reviews-due': 'First Activity: Review(s) due',
        'open-edx.xblock.group-project.grades-posted': 'First Activity: Grade(s) are posted',
    }

    if HIDE_LINK_IS_VISIBLE:
        notifications_container_tabs = ['View unread', 'View all', 'Mark as read', 'Hide']
    else:
        notifications_container_tabs = ['View unread', 'View all', 'Mark as read']

    namespaces = ['foo/bar/baz', 'test/test/test']

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
        self.notification_target_page = NotificationTargetPage(self.browser)

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

    def test_01_show_notifications_container(self):
        """
        Scenario: User is able to show the notification container
        Given that I am on the notification home page
        And notifications container is hidden
        When I click the notification icon
        Then I should see the notification container
        When I click on the hide link
        Then notification container becomes invisible again
        """
        self.login()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.verify_notifications_container_is_invisible()

    def test_02_hide_notifications_container(self):
        """
        Scenario: User is able to hide the notification container
        Given that I am on the notification home page
        And notifications container is visible
        When I click on the notification icon again
        Then notification container should hide
        """
        self.login()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.verify_notifications_container_is_invisible()

    @skipUnless(HIDE_LINK_IS_VISIBLE, "Test only runs if Hide link is visible")
    def test_03_hide_notifications_container_using_hide_tab_link(self):
        """
        Scenario: User is able to hide the notification container
        Given that I am on the notification home page
        And notifications container is visible
        When I click on the notification icon again
        Then notification container should hide
        """
        self.login()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.hide_notification_container_using_hide_link()
        self.logged_in_home_page.verify_notifications_container_is_invisible()

    def test_04_verify_tabs_in_notifications_container(self):
        """
        Scenario: User is able to view 4 tabs namely view unread, view all, Mark as read and hide
        in notification container
        Given that I am on the notification home page
        And notifications container is hidden
        When I click the notification icon
        Then I should see the notification container
        And notification container should display 4 tabs(unread, view all, Mark as read, Hide)
        """
        self.login()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        fetched_notifications_container_tabs = self.logged_in_home_page.return_notifications_container_tabs()
        self.assertEqual(fetched_notifications_container_tabs, self.notifications_container_tabs)

    def test_05_verify_default_tab_selection(self):
        """
        Scenario: When notification container becomes visible, by default the View Unread tab is selected
        Given that I am on the notification home page
        And notifications container is hidden
        When I click the notification icon
        Then I should see the notification container
        And by default the View Unread tab should be selected
        """
        self.login()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        fetched_selected_tab = self.logged_in_home_page.return_selected_tab()
        self.assertEqual(fetched_selected_tab, self.notifications_container_tabs[0])

    def test_06_verify_unread_notifications_count(self):
        """
        Scenario: Clicking on the add notification button after selecting a notification type increases the
        unread notification count by 1.
        Given that I am on the notification home page
        When I click the notification icon after adding a notification
        Then I should see the increase in unread notification count by 1
        """
        self.login()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        initial_unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        for key in self.notification_dict:
            self.logged_in_home_page.select_notification_type(key)
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            final_unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertEqual(final_unread_notification_count, initial_unread_notification_count + 1)
            initial_unread_notification_count = final_unread_notification_count

    def test_07_verify_notifications_count_from_view_all_tab(self):
        """
        Scenario: Clicking on the add notification button after selecting a notification type increases the
        notification count in view all tab by 1.
        Given that I am on the notification home page
        When I click the notification icon after adding a notification
        Then I should see the increase in notification count by 1 in view all tab
        """
        self.login()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.select_view_all_tab()
        initial_notification_count = self.logged_in_home_page.return_view_all_notifications_count()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        for key in self.notification_dict:
            self.logged_in_home_page.select_notification_type(key)
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.select_view_all_tab()
            final_notification_count = self.logged_in_home_page.return_view_all_notifications_count()
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertEqual(final_notification_count, initial_notification_count + 1)
            initial_notification_count = final_notification_count

    def test_08_verify_unread_notifications_text(self):
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
        self.login()
        for key, value in self.notification_dict.iteritems():
            self.logged_in_home_page.select_notification_type(key)
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            unread_notification_list = self.logged_in_home_page.return_notifications_list(key)
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertIn(value, unread_notification_list[0])

    def test_09_verify_view_all_notifications_text(self):
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
        self.login()
        for key, value in self.notification_dict.iteritems():
            self.logged_in_home_page.select_notification_type(key)
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.select_view_all_tab()
            notification_list = self.logged_in_home_page.return_notifications_list(key)
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertIn(value, notification_list[0])

    def test_10_verify_mark_as_read_functionality(self):
        """
        Scenario: When user clicks on mark as read tab, notifications disappear from unread notifications
        tab
        Given that I am on the notification home page
        And there are some notifications present in unread notification tab
        When I click on mark as read link
        Then all notifications should disappear from unread notifications tab
        And notification count on panel should also become 0
        """
        self.login()
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.assertTrue(unread_notification_count > 0)
        self.logged_in_home_page.mark_as_read()
        unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.assertTrue(unread_notification_count == 0)
        display_notification_count = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(display_notification_count == 0)

    def test_11_verify_page_redirect_on_clicking_notifications(self):
        """
        Scenario: When user clicks on any notification, it should redirect user to a specific page
        Given that I am on the notification home page
        And there are some notifications present
        When I click on any notification
        Then it should redirect me to a specific page
        And the resulting page url should be same as click link
        """
        for key in self.notification_dict:
            if key != 'testserver.type1':
                self.login()
                self.logged_in_home_page.select_notification_type(key)
                self.logged_in_home_page.add_notification()
                self.logged_in_home_page.show_notifications_container()
                self.logged_in_home_page.verify_notifications_container_is_visible()
                notification_link = self.logged_in_home_page.click_on_notification()
                self.notification_target_page.verify_target_page_url(notification_link)
                self.browser.back()
                self.logged_in_home_page.log_out()

    def test_12_verify_page_refresh_on_clicking_notifications_without_target_link(self):
        """
        Scenario: When user clicks on any notification without target link, it should just refresh
        the page
        Given that I am on the notification home page
        And there are some notifications present
        When I click on any notification
        Then it should just refresh the page
        """
        self.login()
        self.logged_in_home_page.select_notification_type('testserver.type1')
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        notification_link = self.logged_in_home_page.click_on_notification()
        self.assertTrue(notification_link == 'No target link')

    def test_13_verify_on_clicking_notification_its_status_changes_to_read(self):
        """
        Scenario: When user clicks on any unread notification, it should change
        it's status to read
        When I click on any unread notification
        Then it's status should change to unread
        """
        self.login()
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.logged_in_home_page.click_on_notification()
        self.browser.back()
        self.logged_in_home_page.log_out()
        self.login()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        new_unread_notification_count = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(new_unread_notification_count == unread_notification_count - 1)

    def test_14_verify_on_clicking_notification_without_target_link_its_status_changes_to_read(self):
        """
        Scenario: When user clicks on any unread notification, it should change
        it's status to read
        When I click on any unread notification
        Then it's status should change to unread
        """
        self.login()
        self.logged_in_home_page.select_notification_type('testserver.type1')
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.logged_in_home_page.click_on_notification()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        new_unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
        self.assertTrue(new_unread_notification_count == unread_notification_count - 1)

    def test_15_verify_notification_count_decrease_on_clicking_notification(self):
        """
        Scenario: When user clicks on any notification, the notification count should decrease
        by 1
        Given that I am on the notification home page
        And there are some notifications present
        When I click on any unread notification
        Then it the main notification count should be decreased by 1
        """
        self.login()
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        notification_count = self.logged_in_home_page.get_notifications_count()
        self.logged_in_home_page.click_on_notification()
        self.browser.back()
        self.logged_in_home_page.log_out()
        self.login()
        new_notification_count = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(new_notification_count == notification_count - 1)

    def test_16_verify_notification_count_decreases_on_clicking_notification_without_target_link(self):
        """
        Scenario: When user clicks on any notification, the notification count should decrease
        by 1
        Given that I am on the notification home page
        And there are some notifications present
        When I click on any unread notification
        Then it the main notification count should be decreased by 1
        """
        self.login()
        self.logged_in_home_page.select_notification_type('testserver.type1')
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        notification_count = self.logged_in_home_page.get_notifications_count()
        self.logged_in_home_page.click_on_notification()
        new_notification_count = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(new_notification_count == notification_count - 1)

    def test_17_adding_notifications_in_one_namespace_does_not_change_count_in_other(self):
        """
        Scenario: When user adds notification in first namespace, it does not change
        notification count in 2nd namespace
        Given that I am on the notification home page
        And all name spaces have been initialized to 0 count
        When I add notifications in any namespace
        Then the notification count in other namespace remains unchanged
        """
        self.login()
        for namespace in self.namespaces:
            self.logged_in_home_page.set_namespace(namespace)
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.mark_as_read()
            display_notification_count = self.logged_in_home_page.get_notifications_count()
            self.assertTrue(display_notification_count == 0)
        self.logged_in_home_page.set_namespace(self.namespaces[0])
        self.logged_in_home_page.add_notification()
        notification_count_for_namespace_1 = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(notification_count_for_namespace_1 == 1)
        self.logged_in_home_page.set_namespace(self.namespaces[1])
        notification_count_for_namespace_2 = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(notification_count_for_namespace_2 == 0)

    def test_18_adding_notifications_in_one_namespace_does_not_change_unread_count_in_other(self):
        """
        Scenario: When user adds notification in first namespace, it does not change
        unread notification count in other namespace
        Given that I am on the notification home page
        And all name spaces have been initialized to 0 count
        When I add notifications in any namespace
        Then the unread notification count in other namespace remains unchanged
        """
        self.login()
        for namespace in self.namespaces:
            self.logged_in_home_page.set_namespace(namespace)
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.mark_as_read()
            display_notification_count = self.logged_in_home_page.get_notifications_count()
            self.assertTrue(display_notification_count == 0)
        self.logged_in_home_page.set_namespace(self.namespaces[1])
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count_for_namespace_2 = self.logged_in_home_page.return_unread_notifications_count()
        self.assertTrue(unread_notification_count_for_namespace_2 == 1)
        self.logged_in_home_page.set_namespace(self.namespaces[0])
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count_for_namespace_1 = self.logged_in_home_page.return_unread_notifications_count()
        self.assertTrue(unread_notification_count_for_namespace_1 == 0)

    def test_19_marking_notifications_as_read_in_one_namespace_does_not_impact_other(self):
        """
        Scenario: When user marks notifications in first namespace as read, it does not change
        notifications status in 2nd namespace
        Given that I am on the notification home page
        And all name spaces have some notifications
        When I mark notifications as read in one name space
        Then the notification status in other namespace remains unchanged
        """
        self.login()
        for namespace in self.namespaces:
            self.logged_in_home_page.set_namespace(namespace)
            self.logged_in_home_page.add_notification()
        self.logged_in_home_page.set_namespace(self.namespaces[0])
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.mark_as_read()
        notification_count_for_namespace_1 = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(notification_count_for_namespace_1 == 0)
        self.logged_in_home_page.set_namespace(self.namespaces[1])
        notification_count_for_namespace_2 = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(notification_count_for_namespace_2 > 0)


    def login(self):
        """
        Go to home page and login using correct credentials
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        self.login_page.provide_credentials(user_name, password)
        self.login_page.submit_correct_credentials()
        self.assertTrue(self.logged_in_home_page.is_browser_on_page())

