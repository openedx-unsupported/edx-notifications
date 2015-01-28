"""
All pure data objects that the various Data Providers will product. This is help avoid
generic dictionaries from being passed around, plus this will help avoid any
implicit database-specific bindings that come with any uses of ORMs.
"""

from django.core.exceptions import ValidationError

from notifications import const

from notifications.base_data import (
    StringField,
    DictField,
    DateTimeField,
    IntegerField,
    EnumField,
    RelatedObjectField,
    BaseDataObject
)


class NotificationChannel(BaseDataObject):
    """
    Specifies a channel through which a notification is delivered
    """

    # the internal name of the channel
    name = StringField()

    # the human readible name of the channel
    display_name = StringField()

    # the human readible description of the channel
    description_name = StringField()


class NotificationType(BaseDataObject):
    """
    The Data Object representing the NotificationType
    """

    # the name (including namespace) of the notification, e.g. open-edx.lms.forums.reply-to-post
    name = StringField()

    # the human readible string of the name of the notification
    display_name = StringField()

    # the human readible string that describes the notification
    display_description = StringField()

    # default delivery channel for this type
    # None = no default
    default_channel = RelatedObjectField(NotificationChannel)


class NotificationMessage(BaseDataObject):
    """
    The basic Notification Message
    """

    # instance of NotificationMessageType, None = unloaded
    msg_type = RelatedObjectField(NotificationType)

    # namespace is an optional scoping field. This could
    # be used to indicate - for instance - a course_id. Note,
    # that we can filter on this property when
    # getting notifications
    namespace = StringField()

    # unconstained ID to some user identity service (e.g. auth_user in Django)
    from_user_id = IntegerField()

    # dict containing key/value pairs which comprise the notification data payload
    payload = DictField()

    # DateTime, the earliest that this notification should be delivered
    # for example, this could be used for a delayed notification.
    #
    # None = ASAP
    deliver_no_earlier_than = DateTimeField()

    # DateTime, when this notification is no longer considered valid even if it has not been read
    #
    # None = never
    expires_at = DateTimeField()

    # Duration in seconds, when this notification should be purged after being marked as read.
    #
    # None = never
    expires_secs_after_read = IntegerField()

    priority = EnumField(
        allowed_values=[
            const.NOTIFICATION_PRIORITY_NONE,
            const.NOTIFICATION_PRIORITY_LOW,
            const.NOTIFICATION_PRIORITY_MEDIUM,
            const.NOTIFICATION_PRIORITY_HIGH,
            const.NOTIFICATION_PRIORITY_URGENT,
        ],
        default=const.NOTIFICATION_PRIORITY_NONE
    )

    # timestamps
    created = DateTimeField()
    modified = DateTimeField()

    def validate(self):
        """
        Validator for this DataObject

        I'd like to consolidate this to be optional args on the fields and
        have introspection to make sure everything is OK, but since
        Fields are descriptors, that might make things a bit more difficult. Basically
        we need a way to look at the descriptor not the value the descriptor
        reveals
        """

        if not self.msg_type:
            raise ValidationError("Missing required property: msg_type")


class NotificationUserMap(BaseDataObject):
    """
    Maps a NotificationMessage to a User

    NOTE: We will have to figure out a way to model cursor behavior paging for large
    collections

    NOTE: If we can say that broadcast-type messages, e.g. course-wide, don't need to persist
    read_at state nor any personalization, then we could maybe do away with excessive fan-outs
    """

    # unconstrained pointer to edx-platform auth_user table
    user_id = IntegerField()

    # the message itself
    msg = RelatedObjectField(NotificationMessage)

    # time the user read the notification
    read_at = DateTimeField()

    # dict containing any user specific context (e.g. personalization) for the notification
    user_context = DictField()


class NotificationUserGroup(BaseDataObject):
    """
    A grouping of users into a group, e.g. "cohort", "course enrollments", etc.
    Note that in order to decouple the notification subsystem
    from any existing edx-platform dependencies, we need to
    have generic, abstract grouping mechanisms
    """


class NotificationTypeUserChannelPreference(BaseDataObject):
    """
    Specifies a User preference as to how he/she would like notifications of a certain type
    delivered
    """

    # unconstrained identifier that is provided by some identity service (e.g. auth_user Django Auth)
    user_id = IntegerField()

    # the NotificationType this preference is for
    notification_type = RelatedObjectField(NotificationType)

    # the Channel that this NotificationType should route to
    channel = RelatedObjectField(NotificationChannel)

    # dict containing any user specific context for this channel, for example a mobile # for SMS
    # message, or email address
    channel_context = DictField()
