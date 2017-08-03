"""
NotificationChannelProvider to integrate with the Urban Airship mobile push
notification services
"""
import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from edx_notifications.channels.channel import BaseNotificationChannelProvider

# system defined constants that only we should know about
UA_API_ENDPOINT = 'https://go.urbanairship.com/'
HEADER_DICT = {
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.urbanairship+json; version=3;'
}

log = logging.getLogger(__name__)


class UrbanAirshipNotificationChannelProvider(BaseNotificationChannelProvider):
    """
    Implementation of the BaseNotificationChannelProvider abstract interface
    """

    def __init__(self, name=None, display_name=None, display_description=None,
                 link_resolvers=None, application_id=None, rest_api_key=None):
        """
        Initializer
        """

        if not application_id or not rest_api_key:
            raise Exception('Missing application_id or rest_api_key configuration!')

        self.application_id = application_id
        self.rest_api_key = rest_api_key

        super(UrbanAirshipNotificationChannelProvider, self).__init__(
            name=name,
            display_name=display_name,
            display_description=display_description,
            link_resolvers=link_resolvers
        )

    def dispatch_notification_to_user(self, user_id, msg, channel_context=None):
        """
        Send a notification to a user. It is assumed that
        'user_id' and 'msg' are valid and have already passed
        all necessary validations
        :param user_id:
        :param msg:
        :param channel_context:
        :return:
        """

        obj = {
            'notification': {'alert': msg.payload['excerpt']},
            'audience': {'named_user': user_id},
            'device_types': 'all'
        }
        obj = json.dumps(obj)

        resp = requests.post(
            UA_API_ENDPOINT + 'api/push',
            obj,
            headers=HEADER_DICT,
            auth=HTTPBasicAuth(self.application_id, self.rest_api_key)
        )
        print resp

    def bulk_dispatch_notification(self, user_ids, msg, exclude_user_ids=None, channel_context=None):
        """
        Perform a bulk dispatch of the notification message to
        all user_ids that will be enumerated over in user_ids.
        :param user_ids:
        :param msg:
        :param exclude_user_ids:
        :param channel_context:
        :return:
        """
        cnt = 0
        for user_id in user_ids:
            if not exclude_user_ids or user_id not in exclude_user_ids:
                self.dispatch_notification_to_user(user_id, msg, channel_context=channel_context)
                cnt += 1

        return cnt

    def bulk_dispatch_notification_to_tag(
            self, tag, msg
    ):
        """
        Perform bulk dispatch to all the named users in given tag
        :param tag:
        :param msg:
        :return:
        """
        # Tag validation
        if tag is None or len(tag) < 1:
            raise Exception('No tag is provided')

        obj = {
            'notification': {'alert': msg.payload['excerpt']},
            'device_types': 'all',
            'audience': {'tag': tag}
        }
        obj = json.dumps(obj)

        # Send request to UA API
        resp = requests.post(
            UA_API_ENDPOINT + 'api/push',
            data=obj,
            headers=HEADER_DICT,
            auth=HTTPBasicAuth(self.application_id, self.rest_api_key)
        )

        # For debugging TODO remove it
        resp = resp.json()
        print resp

    def resolve_msg_link(self, msg, link_name, params, channel_context=None):
        """
        Generates the appropriate link given a msg, a link_name, and params
        """
        # Click through links do not apply for mobile push notifications
        return None
