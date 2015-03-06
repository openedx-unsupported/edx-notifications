"""
Notification types that will be used in common use cases for notifications around
Group Projects
"""

from edx_notifications.data import (
    NotificationType
)
from edx_notifications.lib.publisher import register_notification_type
from edx_notifications.signals import perform_type_registrations
from edx_notifications.renderers.basic import UnderscoreStaticFileRenderer

from django.dispatch import receiver


class GroupProjectGenericRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a notification when ranking in the progress leaderboard changes
    """
    underscore_template_name = 'group_project/generic.html'


@receiver(perform_type_registrations)
def register_notification_types(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Register some standard NotificationTypes.
    This will be called automatically on the Notification subsystem startup (because we are
    receiving the 'perform_type_registrations' signal)
    """

    register_notification_type(
        NotificationType(
            name=u'open-edx.xblock.group-project.file-uploaded',
            renderer='edx_notifications.openedx.group_project.GroupProjectGenericRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name=u'open-edx.xblock.group-project.uploads-open',
            renderer='edx_notifications.openedx.group_project.GroupProjectGenericRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name=u'open-edx.xblock.group-project.uploads-due',
            renderer='edx_notifications.openedx.group_project.GroupProjectGenericRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name=u'open-edx.xblock.group-project.reviews-open',
            renderer='edx_notifications.openedx.group_project.GroupProjectGenericRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name=u'open-edx.xblock.group-project.reviews-due',
            renderer='edx_notifications.openedx.group_project.GroupProjectGenericRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name=u'open-edx.xblock.group-project.grades-posted',
            renderer='edx_notifications.openedx.group_project.GroupProjectGenericRenderer',
        )
    )
