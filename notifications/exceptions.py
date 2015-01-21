"""
Specialized exceptions for the Notification subsystem
"""


class NotificationLanguageNotSupported(Exception):
    """
    This exception is thrown when a rendering in a particular language is not supported
    """


class ItemNotFoundError(Exception):
    """
    Generic exception when a look up fails. Since we are abstracting away the backends
    we need to catch any native exceptions and re-throw as a generic exception
    """
