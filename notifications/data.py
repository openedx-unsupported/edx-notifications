"""
All pure data objects that the various Data Providers will product. This is help avoid
generic dictionaries from being passed around, plus this will help avoid any
implicit database-specific bindings that come with any uses of ORMs. Also this helps
with any serialization/deserializations if we separate out services
"""


class BaseDataObject(object):
    """
    A base class for all Notification Data Objects
    """

    id = None  # pylint: disable=invalid-name

    def __init__(self, **kwargs):
        """
        Initializer which will allow for kwargs. Note we can only allow for setting
        of attributes which have been explicitly declared in any subclass
        """

        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
            else:
                raise ValueError(
                    (
                        "Initialization parameter '{name}' was passed in although"
                        "it is not a known attribute to the class."
                    ).format(name=key)
                )


class NotificationMessage(BaseDataObject):
    """
    The basic notification Msg
    """

    payload = {}  # dict
    type_id = None  # FK to NotificationMessageType


class NotificationMessageType(BaseDataObject):
    """
    The Data Object representing the NotificationMessageType
    """


class NotificationMessageUserMap(BaseDataObject):
    """
    Maps a NotificationMessage to a User

    NOTE: We will have to figure out a way to model cursor behavior paging for large
    collections
    """

    user_id = None  # int
