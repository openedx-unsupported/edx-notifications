"""
One time initialization of the Notification subsystem
"""

import logging

from edx_notifications.lib.publisher import (
    register_notification_type,
)

from edx_notifications.data import (
    NotificationType,
)

logger = logging.getLogger("testserver")

def start_up():
    """
    Initialize the Notification subsystem
    """

    logger.info('Registering NotificationTypes...')

    register_notification_type(
        NotificationType(
            name='testserver.type1',
            renderer='edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
        )
    )
