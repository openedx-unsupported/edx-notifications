"""
File to support the startup of the Notification subsystem. This should be called
at least once at the beginning of any process lifecycle
"""

from edx_notifications.signals import perform_type_registrations
from edx_notifications.openedx import notification_type_registration  # pylint: disable=unused-import

# This is unfortunate, but to have the standard Open edX
# NotificationTypes get registered on startup we have
# to import the modules, otherwise, they will
# not register their Django signal receivers


def initialize():
    """
    Startup entry point for the Notification subsystem
    """

    # alert the application tiers that they should register their
    # notification types
    perform_type_registrations.send(sender=None)
