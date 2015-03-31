"""
One time initialization of the Notification subsystem
"""

import logging

from django.dispatch import receiver

from edx_notifications.lib.publisher import (
    register_notification_type,
)

from edx_notifications.data import (
    NotificationType,
)

from edx_notifications import startup

logger = logging.getLogger("testserver")


@receiver(startup.perform_type_registrations)
def perform_type_registrations_handler(sender, **kwargs):  # pylint: disable=unused-argument
    """
    Register test notification types
    """

    logger.info('Registering NotificationTypes...')

    register_notification_type(
        NotificationType(
            name='testserver.type1',
            renderer='edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
        )
    )

    register_notification_type(
        NotificationType(
            name='testserver.msg-with-resolved-click-link',
            renderer='edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
        )
    )


def start_up():
    """
    Initialize the Notification subsystem
    """

    startup.initialize()


