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

from push_notifications.apns import apns_send_message, apns_send_bulk_message

log = logging.getLogger(__name__)


class MobilePushNotificationChannelProvider(BaseNotificationChannelProvider):
    """
    A POC for a APNS gateway for Notifications, using django-push-notfications
    library
    """

    def _get_apns_tokens_for_user(self, user_id):
        """
        TBD
        """

        # NOTE: We'd probably want to put this user_id -> apns_token lookup
        # in some LRU cache. New tokens are registered from a mobile client
        # then we'd invalidate the cache

        # hard code for test purposes, otherwise this will come from
        # a look-up table. IMPORTANT it's possible for one user
        # to make more than one device, and thus more than one
        # apns_token. So it is a one-to-many mapping.
        return ["8d32766c0e430510b6f57d3da12b95a1d6b68cba22554c9eaf9f3afc8dca1b68"]

    def dispatch_notification_to_user(self, user_id, msg):
        """
        Single notification to user
        """

        renderer = get_renderer_for_type(msg.msg_type)

        if renderer and renderer.can_render_format(RENDER_FORMAT_MOBILEPUSH):
            text_msg = renderer.render_body(msg, RENDER_FORMAT_MOBILEPUSH, None)

            # device = APNSDevice.objects.get(registration_id=apns_token)

            registration_ids = self._get_apns_tokens_for_user(user_id)

            for registration_id in registration_ids:
                apns_send_message(
                    registration_id=registration_id,
                    alert=text_msg,
                    sound='default'
                )

    def bulk_dispatch_notification(self, user_ids, msg, exclude_user_ids=None):
        """
        Perform a bulk dispatch of the notification message to
        all user_ids that will be enumerated over in user_ids.
        """

        renderer = get_renderer_for_type(msg.msg_type)

        if renderer and renderer.can_render_format(RENDER_FORMAT_MOBILEPUSH):
            text_msg = renderer.render_body(msg, RENDER_FORMAT_MOBILEPUSH, None)

            registration_ids = list()
            cnt = 0
            for user_id in user_ids:
                if not exclude_user_ids or user_id not in exclude_user_ids:
                    tokens = self._get_apns_tokens_for_user(user_id)
                    for token in tokens:
                        registration_ids.append(token)
                    cnt = cnt + len(tokens)
                    # chunk by 100 at a time, no specific reason why
                    # just picking that arbitrarily
                    if cnt > 100:
                        # ship ahoy!
                        apns_send_bulk_message(
                            registration_ids=registration_ids,
                            alert=text_msg,
                            sound='default'
                        )
                        registration_ids = list()
                        cnt = 0

            if cnt > 0:
                apns_send_bulk_message(
                    registration_ids=registration_ids,
                    alert=text_msg,
                    sound='default'
                )

    def resolve_msg_link(self, msg, link_name, params):
        """
        Generates the appropriate link given a msg, a link_name, and params
        """
        return None
