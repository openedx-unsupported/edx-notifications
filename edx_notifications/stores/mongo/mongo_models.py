"""
Classes to support the Notification Store Mongodb backend
"""
from edx_notifications.base_data import DictField
from edx_notifications.data import UserNotification
from edx_notifications.stores.sql.models import SQLNotificationMessage


class MongoUserNotification(object):
    """
    Class with utility methods to allow conversion to the UserNotification object in place of the Django ORM's model.
    """

    @classmethod
    def to_data_object(cls, mongo_user_notification, user_id):
        """
        Generate a NotificationType data object
        """

        msg = SQLNotificationMessage.objects.get(id=mongo_user_notification['msg_id'])

        return UserNotification(
            user_id=user_id,
            msg=msg.to_data_object(),  # pylint: disable=no-member
            read_at=mongo_user_notification['read_at'],
            user_context=DictField.from_json(mongo_user_notification['user_context']),
            created=mongo_user_notification['created']
        )
