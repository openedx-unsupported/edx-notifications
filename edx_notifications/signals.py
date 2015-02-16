"""
Django signals that can be raised by the Notification subsystem
"""

from django.dispatch import Signal


# Signal to all receivers that they should go register their NotificationTypes into
# the subsystem
perform_type_registrations = Signal(providing_args=[])  # pylint: disable=invalid-name
