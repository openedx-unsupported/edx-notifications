"""
NotificationChannelProvider to integrate with the Urban Airship mobile push
notification services
"""
import json
import logging

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

from edx_notifications.channels.channel import BaseNotificationChannelProvider

# system defined constants that only we should know about
UA_API_PUSH_ENDPOINT = 'https://go.urbanairship.com/api/push/'
PUSH_REQUEST_HEADER = {
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

        resp = {}
        try:
            resp = requests.post(
                UA_API_PUSH_ENDPOINT,
                obj,
                headers=PUSH_REQUEST_HEADER,
                auth=HTTPBasicAuth(self.application_id, self.rest_api_key)
            )
            resp = resp.json()
            if not resp['ok']:
                log.warning(resp['details'])

        except RequestException as ex:
            log.error(ex.message)

        return resp

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
        assert channel_context['group'], 'No group is defined in context'
        assert channel_context['tag'], 'No tag is defined in context'
        assert msg.payload['excerpt'], 'No excerpt defined in payload'
        assert msg.payload['announcement_date'], 'No announcement date ' \
                                                 'defined in payload'
        group = channel_context['group']
        tag = channel_context['tag']
        excerpt = msg.payload['excerpt']
        announcement_date = msg.payload['announcement_date']

        obj = {
            'notification': {
                'alert': excerpt,
                'actions': {
                    'open': {
                        'type': 'url',
                        'content': 'https://www.mckinseyacademy.com/{}/'
                                   'announcements/{}/'.format(tag, announcement_date)
                    }
                }
            },
            'device_types': 'all',
            'audience': {
                'group': group,
                'tag': tag
            }
        }

        obj = json.dumps(obj)

        # Send request to UA API
        resp = {}
        try:
            resp = requests.post(
                UA_API_PUSH_ENDPOINT,
                data=obj,
                headers=PUSH_REQUEST_HEADER,
                auth=HTTPBasicAuth(self.application_id, self.rest_api_key)
            )
            resp = resp.json()
            if not resp['ok']:
                log.warning(resp['details'])

        except RequestException as ex:
            log.error(ex.message)

        return resp

    def dispatch_notification_to_tag(self, msg, group, tag):
        """
        Perform bulk dispatch to all the named users in given tag
        :param group:
        :param tag:
        :param msg:
        :return:
        """
        assert msg.payload['excerpt'], 'No excerpt defined in payload'
        assert msg.payload['announcement_date'], 'No announcement date ' \
                                                 'defined in payload'
        # Create request JSON object
        obj = {
            'notification': {
                'alert': msg.payload['excerpt'],
                'actions': {
                    'open': {
                        'type': 'url',
                        'content': 'https://www.mckinseyacademy.com/{}/'
                                   'announcements/{}/'.format(tag, msg.payload['announcement_date'])
                    }
                }
            },
            'device_types': 'all',
            'audience': {
                'group': group,
                'tag': tag
            }
        }

        obj = json.dumps(obj)

        # Send request to UA API
        resp = {}
        try:
            resp = requests.post(
                UA_API_PUSH_ENDPOINT,
                data=obj,
                headers=PUSH_REQUEST_HEADER,
                auth=HTTPBasicAuth(self.application_id, self.rest_api_key)
            )
            resp = resp.json()
            if not resp['ok']:
                log.warning(resp['details'])

        except RequestException as ex:
            log.error(ex.message)

        return resp

    def resolve_msg_link(self, msg, link_name, params, channel_context=None):
        """
        Generates the appropriate link given a msg, a link_name, and params
        """
        # Click through links do not apply for mobile push notifications
        return None
