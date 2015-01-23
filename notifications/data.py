"""
All pure data objects that the various Data Providers will product. This is help avoid
generic dictionaries from being passed around, plus this will help avoid any
implicit database-specific bindings that come with any uses of ORMs.
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
                        "Initialization parameter '{name}' was passed in although "
                        "it is not a known attribute to the class."
                    ).format(name=key)
                )

    def __setattr__(self, attribute, value):
        """
        Don't allow new attributes to be added outside of
        attributes that were present after initialization
        We want our data models to have a fixed schema!!!
        """

        if not hasattr(self, attribute):
            raise ValueError(
                (
                    "Attempting to add a new attribute '{name}' that was not part of "
                    "the original schema."
                ).format(name=attribute)
            )

        super(BaseDataObject, self).__setattr__(attribute, value)


class NotificationMessage(BaseDataObject):
    """
    The basic notification Msg
    """

    payload = {}  # dict
    type_id = None  # FK to NotificationMessageType

    # DateTime, the earliest that this notification should be delivered
    # for example, this could be used for a delayed notification.
    #
    # None = ASAP
    deliver_no_earlier_than = None

    # DateTime, when this notification is no longer considered valid even if it has not been read
    #
    # None = never
    expires_at = None

    # TimeDelta, when this notification should be purged after being marked as read.
    #
    # None = never
    expires_after_read = None


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

    user_id = None  # int, unconstrained pointer to edx-platform auth_user table
    msg_id = None   # FK to NotificationMessage
    read_at = None  # DateTime (UTC)

    # dict containing any user specific context (e.g. personalization) for the notification
    user_context = {}


class NotificationUserGroup(BaseDataObject):
    """
    A grouping of users into a group, e.g. "cohort", "course enrollments", etc.
    Note that in order to decouple the notification subsystem
    from any existing edx-platform dependencies, we need to
    have generic, abstract grouping mechanisms
    """


class NotificationChannel(BaseDataObject):
    """
    Specifies a channel through which a notification is delivered
    """


class NotificationTypeUserChannellPreference(BaseDataObject):
    """
    Specifies a User preference as to how he/she would like notifications of a certain type
    delivered
    """

    user_id = None  # int, unconstrained pointer to edx-platform auth_user table
    type_id = None  # FK to NotificationMessageType
    channel_id = None  # FK to NotificationChannel

    # dict containing any user specific context for this channel, for example a mobile # for SMS
    # message, or email address
    channel_context = {}
