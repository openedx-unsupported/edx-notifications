"""
Experimental APNS gateway for Notifications
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
    RENDER_FORMAT_MOBILEPUSH
)

from push_notifications.apns import apns_send_message

log = logging.getLogger(__name__)


class MobilePushNotificationChannelProvider(BaseNotificationChannelProvider):
    """
    A POC for a APNS gateway for Notifications, using django-push-notfications
    library
    """

    def _get_apns_token_for_user(self, user_id):
        """
        TBD
        """
        return "8d32766c0e430510b6f57d3da12b95a1d6b68cba22554c9eaf9f3afc8dca1b68"

    def dispatch_notification_to_user(self, user_id, msg):
        """
        Single notification to user
        """

        renderer = get_renderer_for_type(msg.msg_type)

        if renderer and renderer.can_render_format(RENDER_FORMAT_MOBILEPUSH):
            text_msg = renderer.render_body(msg, RENDER_FORMAT_MOBILEPUSH, None)

            # device = APNSDevice.objects.get(registration_id=apns_token)

            apns_send_message(
                registration_id=self._get_apns_token_for_user(user_id),
                alert=text_msg,
                sound='default'
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
