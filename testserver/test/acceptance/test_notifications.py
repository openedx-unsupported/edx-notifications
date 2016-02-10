from bok_choy.web_app_test import WebAppTest
from testserver.bokchoy_settings import HIDE_LINK_IS_VISIBLE
from pages import user_name, user_email, password
from pages.home_page import HomePage
from pages.registration_page import RegistrationPage
from pages.registration_success_page import RegistrationSuccess
from pages.login_page import LoginPage
from pages.logged_in_home_page import LoggedInHomePage
from pages.notification_target_page import NotificationTargetPage
from unittest import skipUnless


class TestAddNotifications(WebAppTest):

    notification_dict = {
        'open-edx.studio.announcements.new-announcement': 'Gettysburg Address',
        'open-edx.lms.discussions.reply-to-thread': 'testuser responded to your post in ',
        'open-edx.lms.discussions.thread-followed': 'A demo posting to the discussion forums was followed 3 times',
        'open-edx.lms.discussions.post-upvoted': 'post A demo posting to the discussion forums was upvoted 5 times',
        'open-edx.lms.discussions.cohorted-thread-added': 'testuser posted: Four score and seven years ago',
        'open-edx.lms.discussions.cohorted-comment-added': 'testuser responded: Four score and seven years ago',
        'open-edx.lms.discussions.comment-upvoted': 'response to A demo posting to the discussion forums was upvoted',
        'open-edx.lms.leaderboard.progress.rank-changed': 'You are now #2 for Progress in the cohort!',
        'open-edx.lms.leaderboard.gradebook.rank-changed': 'You are now #3 for Proficiency in the cohort!',
        'open-edx.lms.leaderboard.engagement.rank-changed': 'You are now #1 for Engagement in the cohort!',
        'open-edx.xblock.group-project.file-uploaded': 'First Activity: testuser uploaded a file',
        'open-edx.xblock.group-project.stage-open': 'First Activity: Upload(s) are open',
        'open-edx.xblock.group-project.stage-due': 'First Activity: Upload(s) due 4/25',
        'open-edx.xblock.group-project.grades-posted': 'First Activity: Grade(s) are posted',
        'open-edx.xblock.group-project-v2.file-uploaded': 'First Activity V2: testuser V2 uploaded a file',
        'open-edx.xblock.group-project-v2.stage-open': 'First Activity V2: Upload(s) V2 are open',
        'open-edx.xblock.group-project-v2.stage-due': 'First Activity V2: Upload(s) V2 due 4/25',
        'open-edx.xblock.group-project-v2.grades-posted': 'First Activity V2: Grade(s) are posted',
    }

    short_notification_dict = {
        'open-edx.studio.announcements.new-announcement': 'Gettysburg Address',
        'open-edx.lms.discussions.reply-to-thread': 'testuser responded to your post in ',
        'open-edx.lms.discussions.cohorted-thread-added': 'testuser posted: Four score and seven years ago',
        'open-edx.lms.leaderboard.progress.rank-changed': 'You are now #2 for Progress in the cohort!',
        'open-edx.xblock.group-project.grades-posted': 'First Activity: Grade(s) are posted',
    }

    if HIDE_LINK_IS_VISIBLE:
        notifications_container_tabs = ['View unread', 'View all', 'Mark as read', 'Hide', 'Settings']
    else:
        notifications_container_tabs = ['View unread', 'View all', 'Mark as read', 'Settings']

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

    def test_00_show_notification_pane(self):
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

    def test_01_hide_notification_pane(self):
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
    def test_02_hide_link(self):
        """
        Scenario: User is able to hide the notification container using hide link
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

    def test_03_verify_tabs(self):
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

    def test_04_verify_default_tab(self):
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

    def test_05_unread_notifications_count(self):
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

    def test_06_view_all_notification_count(self):
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
        for key in self.short_notification_dict:
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

    def test_07_unread_notifications_text(self):
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

    def test_08_view_all_notifications_text(self):
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
        for key, value in self.short_notification_dict.iteritems():
            self.logged_in_home_page.select_notification_type(key)
            self.logged_in_home_page.add_notification()
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.select_view_all_tab()
            notification_list = self.logged_in_home_page.return_notifications_list(key)
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()
            self.assertIn(value, notification_list[0])

    def test_09_mark_as_read(self):
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
        self.assertEqual(unread_notification_count, 0)
        display_notification_count = self.logged_in_home_page.get_notifications_count()
        self.assertEqual(display_notification_count, 0)

    def test_10_page_redirect(self):
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

    def test_11_page_refresh(self):
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
        self.assertEqual(notification_link, 'No target link')

    def test_12_status_change_one(self):
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
        self.assertEqual(new_unread_notification_count, unread_notification_count - 1)

    def test_13_status_change_two(self):
        """
        Scenario: When user clicks on any notification without target link, it should change
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
        self.assertEqual(new_unread_notification_count, unread_notification_count - 1)

    def test_14_notification_count_decrease_one(self):
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
        self.assertEqual(new_notification_count, notification_count - 1)

    def test_15_notification_count_decreases_two(self):
        """
        Scenario: When user clicks on any notification without target link, the notification
        count should decrease by 1
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
        self.assertEqual(new_notification_count, notification_count - 1)

    def test_16_namespace_one(self):
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
            self.assertEqual(display_notification_count, 0)
        self.logged_in_home_page.set_namespace(self.namespaces[0])
        self.logged_in_home_page.add_notification()
        notification_count_for_namespace_1 = self.logged_in_home_page.get_notifications_count()
        self.assertEqual(notification_count_for_namespace_1, 1)
        self.logged_in_home_page.set_namespace(self.namespaces[1])
        notification_count_for_namespace_2 = self.logged_in_home_page.get_notifications_count()
        self.assertEqual(notification_count_for_namespace_2, 0)

    def test_18_namespace_two(self):
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
            self.assertEqual(display_notification_count, 0)
        self.logged_in_home_page.set_namespace(self.namespaces[1])
        self.logged_in_home_page.add_notification()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count_for_namespace_2 = self.logged_in_home_page.return_unread_notifications_count()
        self.assertEqual(unread_notification_count_for_namespace_2, 1)
        self.logged_in_home_page.set_namespace(self.namespaces[0])
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        unread_notification_count_for_namespace_1 = self.logged_in_home_page.return_unread_notifications_count()
        self.assertEqual(unread_notification_count_for_namespace_1, 0)

    def test_19_namespace_three(self):
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
        self.assertEqual(notification_count_for_namespace_1, 0)
        self.logged_in_home_page.set_namespace(self.namespaces[1])
        notification_count_for_namespace_2 = self.logged_in_home_page.get_notifications_count()
        self.assertTrue(notification_count_for_namespace_2 > 0)

    def test_20_close_icon(self):
        """
        Scenario: When user clicks on close icon of any notification, it should remain on current
        page and notification count along with unread count should decrease by 1
        Given that I am on the notification home page
        And there are some notifications present
        When I click on any notification's close icon
        Then it should stay on the same page
        And the notification count should decrease by one
        And unread notification count should also decrease by one
        """
        self.login()
        self.logged_in_home_page.show_notifications_container()
        self.logged_in_home_page.verify_notifications_container_is_visible()
        self.logged_in_home_page.mark_as_read()
        self.logged_in_home_page.hide_notification_container()
        self.logged_in_home_page.verify_notifications_container_is_invisible()
        for key in self.notification_dict:
            self.logged_in_home_page.select_notification_type(key)
            self.logged_in_home_page.add_notification()
            initial_notification_count = self.logged_in_home_page.get_notifications_count()
            self.assertEqual(initial_notification_count, 1)
            self.logged_in_home_page.show_notifications_container()
            self.logged_in_home_page.verify_notifications_container_is_visible()
            initial_unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
            self.assertEqual(initial_unread_notification_count, 1)
            self.logged_in_home_page.verify_notifications_container_is_visible()
            self.logged_in_home_page.close_notification()
            self.assertTrue(self.logged_in_home_page.is_browser_on_page())
            final_unread_notification_count = self.logged_in_home_page.return_unread_notifications_count()
            self.assertEqual(final_unread_notification_count, 0)
            final_notification_count = self.logged_in_home_page.get_notifications_count()
            self.assertEqual(final_notification_count, 0)
            self.logged_in_home_page.hide_notification_container()
            self.logged_in_home_page.verify_notifications_container_is_invisible()

    def login(self):
        """
        Go to home page and login using correct credentials
        """
        self.home_page.visit()
        self.home_page.go_to_login_page()
        login_result = self.login_page.login_to_application(user_name, password)
        if login_result == 'User not registered':
            self.home_page.go_to_registration_page()
            self.registration_page.register(user_name, user_email, password)
            self.registration_success.go_to_login_page()
            self.login_page.login_to_application(user_name, password)
            self.assertTrue(self.logged_in_home_page.is_browser_on_page())
        self.assertTrue(self.logged_in_home_page.is_browser_on_page())

