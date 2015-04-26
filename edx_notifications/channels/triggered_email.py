"""
Implements a email notification channel
that sends email to the users.
"""

import logging
from edx_notifications.channels.channel import BaseNotificationChannelProvider
from edx_notifications.scopes import resolve_user_scope

from edx_notifications.data import UserNotification

from edx_notifications.channels.link_resolvers import MsgTypeToUrlResolverMixin

log = logging.getLogger(__name__)


class TriggeredEmailChannelProvider(MsgTypeToUrlResolverMixin, BaseNotificationChannelProvider):
    """
    A TriggeredEmail notification channel will
    send email to the user.
    """

    def dispatch_notification_to_user(self, user_id, msg, channel_context=None):
        """
        Send a notification to a user, which - in a TriggerEmailChannel Notification
        """

        # call into one of the registered resolvers to get the email for this
        # user
        scope_results = resolve_user_scope('student_email_resolver', {'user_id': user_id})

        msg = self._get_linked_resolved_msg(msg)

        user_msg = UserNotification(
            user_id=user_id,
            msg=msg
        )

        for result in scope_results:
            #
            # Do the rendering and the sending of the email
            #
            if isinstance(result, dict):
                email = result['email']
            else:
                email = result
            print '***** email = {}'.format(email)

        return user_msg

    def bulk_dispatch_notification(self, user_ids, msg, exclude_user_ids=None, channel_context=None):
        """
        Perform a bulk dispatch of the notification message to
        all user_ids that will be enumerated over in user_ids.

        user_ids should be a list, a generator function, or a django.db.models.query.ValuesListQuerySet
        when directly feeding in a Django ORM queryset, where we select just the id column of the user
        """

        # enumerate through the list of user_ids and call
        # dispatch_notification_to_user method.
        #  e sure not to include any user_id in the exclude list
        for user_id in user_ids:
            if not exclude_user_ids or user_id not in exclude_user_ids:
                self.dispatch_notification_to_user(user_id, msg, channel_context)
