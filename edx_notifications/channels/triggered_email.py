"""
Implements a email notification channel
that sends email to the users.
"""

import logging
from edx_notifications.channels.durable import BaseDurableNotificationChannel
from edx_notifications.scopes import resolve_user_scope

log = logging.getLogger(__name__)


class TriggeredEmailChannelProvider(BaseDurableNotificationChannel):
    """
    A TriggeredEmail notification channel will
    send email to the user.
    """

    def dispatch_notification_to_user(self, user_id, msg, channel_context=None):
        """
        Send a notification to a user, which - in a TriggerEmailChannel Notification
        """

        # user_ids = resolve_user_scope('student_email_resolver', {'user_id': user_id})
        msg = super(TriggeredEmailChannelProvider, self)._get_linked_resolved_msg(msg)

        return msg

    def bulk_dispatch_notification(self, user_ids, msg, exclude_user_ids=None, channel_context=None):
        """
        Perform a bulk dispatch of the notification message to
        all user_ids that will be enumerated over in user_ids.

        user_ids should be a list, a generator function, or a django.db.models.query.ValuesListQuerySet
        when directly feeding in a Django ORM queryset, where we select just the id column of the user
        """
        exclude_user_ids = exclude_user_ids if exclude_user_ids else []

        # enumerate through the list of user_ids and call
        # dispatch_notification_to_user method.
        #  e sure not to include any user_id in the exclude list
        for user_id in user_ids:
            if user_id not in exclude_user_ids:
                self.dispatch_notification_to_user(user_id, msg, channel_context)

    def resolve_msg_link(self, msg, link_name, params, channel_context=None):
        """
        Generates the appropriate link given a msg, a link_name, and params
        """
        resolved_link = super(TriggeredEmailChannelProvider, self).resolve_msg_link(msg, link_name, params, channel_context=None)
        return resolved_link
