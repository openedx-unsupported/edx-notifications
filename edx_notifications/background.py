"""
All code to support background Notification triggers
"""

from django.dispatch import Signal


# Signal to all receivers that they should go through and perform any checks
# as to conditions when
perform_notification_scan = Signal(providing_args=[])  # pylint: disable=invalid-name


def fire_background_notification_check():
    """
    This method will evoke the Django signal which applications can receive and perform any logic to see
    if any Notifications should be fired
    """

    perform_notification_scan.send(sender=None)
