"""
File to support the startup of the Notification subsystem. This should be called
at least once at the beginning of any process lifecycle
"""

from django.dispatch import Signal


# Signal to all receivers that they should go register their NotificationTypes into
# the subsystem
perform_type_registrations = Signal(providing_args=[])  # pylint: disable=invalid-name


def initialize():
    """
    Startup entry point for the Notification subsystem
    """

    # alert the application tiers that they should register their
    # notification types
    perform_type_registrations.send(sender=None)
