"""
Notifications type receivers that register
their particular Notifications Types when they receive
the signal
"""

from edx_notifications.data import (
    NotificationType
)
from edx_notifications.lib.publisher import register_notification_type
from edx_notifications.signals import perform_type_registrations

from django.dispatch import receiver


@receiver(perform_type_registrations)
def register_notification_types(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Register all standard NotificationTypes regarding forums and course announcements.
    This will be called automatically on the Notification subsystem startup (because we are
    receiving the 'perform_type_registrations' signal)
    """

    # someone replying to thread use-case
    register_notification_type(
        NotificationType(
            name='open-edx.lms.discussions.reply-to-thread',
            renderer='edx_notifications.openedx.forums.ReplyToThreadRenderer',
        )
    )

    # someone following the thread use-case
    register_notification_type(
        NotificationType(
            name='open-edx.lms.discussions.thread-followed',
            renderer='edx_notifications.openedx.forums.ThreadFollowedRenderer',
        )
    )

    # someone voting the thread use-case
    register_notification_type(
        NotificationType(
            name='open-edx.lms.discussions.post-upvoted',
            renderer='edx_notifications.openedx.forums.PostUpvotedRenderer',
        )
    )

    # someone voting the comment use-case
    register_notification_type(
        NotificationType(
            name='open-edx.lms.discussions.comment-upvoted',
            renderer='edx_notifications.openedx.forums.CommentUpvotedRenderer',
        )
    )

    # updates/announcements in the course use-case.
    register_notification_type(
        NotificationType(
            name='open-edx.studio.announcements.new_announcement',
            renderer='edx_notifications.openedx.course_announcements.NewCourseAnnouncementRenderer',
        )
    )
