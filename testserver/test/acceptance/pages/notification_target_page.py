from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise
from . import default_timeout


class NotificationTargetPage(PageObject):

    url = None

    def is_browser_on_page(self):
        """
        Return true if title contains the word page
        :return:
        """
        return 'error!!' not in self.browser.title

    def verify_target_page_url(self, target_link):
        """
        Accepts the target link as parameter and wait until the current url becomes
        equal to target link
        :param target_link:
        :return:
        """
        EmptyPromise(
            lambda: target_link in self.browser.current_url,
            'target url is not correct',
            timeout=default_timeout
        ).fulfill()