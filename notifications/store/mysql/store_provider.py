"""
Concrete MySQL implementation of the data provider interface
"""

import json
import copy
import dateutil.parser

from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from notifications.store.store import BaseNotificationStoreProvider
from notifications.data import NotificationMessage
from notifications.exceptions import ItemNotFoundError

from notifications.store.mysql.models import (
    SQLNotificationMessage,
)


def _json_serialize_dict(src_dict):
    """
    This helper method will help serialize the payload dict into a string
    as MySQL will want to store the payload as a string.
    We can't use the json.dumps() as a serializer because datetime will
    throw an exception
    """

    # go through and see if we have any datetime types

    _dict = copy.deepcopy(src_dict)

    for key, value in _dict.iteritems():
        if isinstance(value, datetime):
            _dict[key] = value.isoformat()

    return json.dumps(_dict)


def _json_deseralize_dict(src_str):
    """
    Deserializes a json payload into a python dict,
    converting back datestrings into a native datetime
    """

    _dict = json.loads(src_str)

    for key, value in _dict.iteritems():
        if isinstance(value, basestring):
            # This could be a datetime posing as a ISO8601 formatted string
            # we so have to apply some heuristics here
            # to see if we want to even attempt
            if value.count('-') == 2 and value.count(':') == 2 and value.count('T') == 1:
                # this is likely a ISO8601 serialized string, so let's try to parse
                try:
                    _dict[key] = dateutil.parser.parse(value)
                except ValueError:
                    # oops, I guess our heuristic was a bit off
                    # no harm, but just wasted CPU cycles
                    pass

    return _dict


class MySQLNotificationStoreProvider(BaseNotificationStoreProvider):
    """
    Concrete MySQL implementation of the abstract base class (interface)
    """

    def get_notification_message_by_id(self, msg_id):
        """
        For the given message id return the corresponding NotificationMessage data object
        """

        try:
            obj = SQLNotificationMessage.objects.get(id=msg_id)
        except ObjectDoesNotExist:
            raise ItemNotFoundError()

        msg = NotificationMessage(
            id=obj.id,
            payload=_json_deseralize_dict(obj.payload)
        )
        return msg

    def save_notification_message(self, msg):
        """
        Saves a passed in NotificationMsg data object. If 'id' is set by the caller
        it will try to update the object. If it does not exist it will throw an
        exception.

        If it is created, then the id property will be set on the NotificationMsg and returned
        """

        if msg.id:
            try:
                obj = SQLNotificationMessage.objects.get(id=msg.id)
            except ObjectDoesNotExist:
                raise ItemNotFoundError()
        else:
            obj = SQLNotificationMessage(
                payload=_json_serialize_dict(msg.payload)
            )

        obj.save()
        msg.id = obj.id
        return msg

    def get_notifications_for_user(self, user_id, read=True, unread=True):
        """
        Returns a (unsorted) collection (list) of notifications for the user.

        NOTE: We will have to add paging (with sorting/filtering) in the future

        ARGS:
            - user_id: The id of the user
            - read: Whether to return read notifications (default True)
            - unread: Whether to return unread notifications (default True)

        RETURNS: type list   i.e. []
        """

        result_set = []

        return result_set
