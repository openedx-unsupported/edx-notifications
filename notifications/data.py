"""
All pure data objects that the various Data Providers will product. This is help avoid
generic dictionaries from being passed around, plus this will help avoid any
implicit database-specific bindings that come with any uses of ORMs.
"""

from notifications.base_data import (
    TypedField,
    DictTypedField,
    DateTimeTypedField,
    IntegerTypedField,
    BaseDataObject
)


class NotificationMessageType(BaseDataObject):
    """
    The Data Object representing the NotificationMessageType
    """


class NotificationMessage(BaseDataObject):
    """
    The basic notification Msg
    """

    # instance of NotificationMessageType, None = unloaded
    msg_type = TypedField(NotificationMessageType)

    # dict containing key/value pairs which comprise the notification data payload
    payload = DictTypedField()

    # DateTime, the earliest that this notification should be delivered
    # for example, this could be used for a delayed notification.
    #
    # None = ASAP
    deliver_no_earlier_than = DateTimeTypedField()

    # DateTime, when this notification is no longer considered valid even if it has not been read
    #
    # None = never
    expires_at = DateTimeTypedField()

    # Duration in seconds, when this notification should be purged after being marked as read.
    #
    # None = never
    expires_secs_after_read = IntegerTypedField()


class NotificationMessageUserMap(BaseDataObject):
    """
    Maps a NotificationMessage to a User

    NOTE: We will have to figure out a way to model cursor behavior paging for large
    collections

    NOTE: If we can say that broadcast-type messages, e.g. course-wide, don't need to persist
    read_at state nor any personalization, then we could maybe do away with excessive fan-outs
    """

    user_id = None  # int, unconstrained pointer to edx-platform auth_user table
    msg = None  # Instance of the Message, None = unloaded
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
    notification_type = NotificationMessageType()  # FK to NotificationMessageType
    channel = NotificationChannel()  # FK to NotificationChannel

    # dict containing any user specific context for this channel, for example a mobile # for SMS
    # message, or email address
    channel_context = {}
