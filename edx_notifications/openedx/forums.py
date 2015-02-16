"""
Notification types that will be used in common use cases for notifications around
discussion forums
"""

from edx_notifications.data import (
    NotificationType
)
from edx_notifications.lib.publisher import register_notification_type
from edx_notifications.signals import perform_type_registrations
from edx_notifications.renderers.basic import UnderscoreStaticFileRenderer

from django.dispatch import receiver


class ReplyToThreadRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a reply-to-thread notification
    """
    underscore_template_name = 'forums/reply_to_thread.html'


class ThreadFollowedRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a thread-followed notification
    """
    underscore_template_name = 'forums/thread_followed.html'


class PostUpvotedRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a post-upvoted notification
    """
    underscore_template_name = 'forums/post_upvoted.html'


@receiver(perform_type_registrations)
def register_forums_notification_types(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Register all standard NotificationTypes regarding forums. This will be called
    automatically on the Notification subsystem startup (because we are
    receiving the 'perform_type_registrations' signal)
    """

    # someone replying to thread use-case
    register_notification_type(
        NotificationType(
            name='open-edx.lms.discussions.reply-to-thread',
            renderer='edx_notifications.openedx.forums.ReplyToThreadRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name='open-edx.lms.discussions.thread-followed',
            renderer='edx_notifications.openedx.forums.ThreadFollowedRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name='open-edx.lms.discussions.post-upvoted',
            renderer='edx_notifications.openedx.forums.PostUpvotedRenderer',
        )
    )
