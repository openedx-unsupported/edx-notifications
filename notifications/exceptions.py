"""
Specialized exceptions for the Notification subsystem
"""


class ItemNotFoundError(Exception):
    """
    Generic exception when a look up fails. Since we are abstracting away the backends
    we need to catch any native exceptions and re-throw as a generic exception
    """


class ItemConflictError(Exception):
    """
    Generic exception when trying to save an object that has the same primary key
    """
