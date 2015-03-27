"""
Experimental SMS gateway for Notifications
"""

import logging
from importlib import import_module

from edx_notifications import const
from edx_notifications.channels.channel import BaseNotificationChannelProvider

from edx_notifications.stores.store import notification_store
from edx_notifications.renderers.renderer import get_renderer_for_type

from edx_notifications.data import (
    UserNotification,
    NotificationMessage,
)
from edx_notifications.const import (
    RENDER_FORMAT_SMS
)
from twilio.rest import TwilioRestClient

log = logging.getLogger(__name__)


class TwilioNotificationChannelProvider(BaseNotificationChannelProvider):
    """
    A POC for a SMS gateway for Notifications, using the Twilio
    SMS provider
    """

    def __init__(self, account_SID=None, account_authtoken=None, from_tel=None, to_tel=None, **kwargs):
        """
        Initializer
        """
        self.account_SID = account_SID
        self.account_authtoken = account_authtoken
        self.from_tel = from_tel
        self.to_tel = to_tel

    def dispatch_notification_to_user(self, user_id, msg):
        """
        Single notification to user
        """

        renderer = get_renderer_for_type(msg.msg_type)

        if renderer and renderer.can_render_format(RENDER_FORMAT_SMS):
            client = TwilioRestClient(self.account_SID, self.account_authtoken)
            text_msg = renderer.render_subject(msg, RENDER_FORMAT_SMS, None) + ". " + renderer.render_body(msg,RENDER_FORMAT_SMS, None)

            message = client.messages.create(
                body=text_msg,
                to=self.to_tel,
                from_=self.from_tel
            )

    def bulk_dispatch_notification(self, user_ids, msg, exclude_user_ids=None):
        """
        Perform a bulk dispatch of the notification message to
        all user_ids that will be enumerated over in user_ids.
        """
        for user_id in user_ids:
            if not exclude_user_ids or user_id not in exclude_user_ids:
                self.dispatch_notification_to_user(user_id, msg)

    def resolve_msg_link(self, msg, link_name, params):
        """
        Generates the appropriate link given a msg, a link_name, and params
        """
        return None
