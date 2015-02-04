"""
Notification Consumer HTTP-based API enpoints
"""

import logging

from rest_framework import status
from rest_framework.response import Response

from edx_notifications.lib.consumer import (
    get_notifications_count_for_user,
    get_notifications_for_user
)

from edx_notifications.exceptions import (
    ItemNotFoundError,
)

from .api_utils import AuthenticatedAPIView

LOG = logging.getLogger("api")

FILTER_PARAMETER_NAMES = [
    ('read', bool),
    ('unread', bool),
    ('namespace', unicode),
    ('msg_type', unicode),
]

OPTIONS_PARAMETER_NAMES = [
    ('offset', int),
    ('limit', int),
]

BOOLEAN_TRUE_STRINGS = [
    'True',
    'true',
    '1',
    'yes',
]

BOOLEAN_FALSE_STRINGS = [
    'False',
    'false',
    '0',
    'no',
]


def _get_parameters_from_request(request, allowed_parameters):
    """
    Helper method to pull parameters from querystring passed in the request URL
    """

    params = {}
    for (filter_name, filter_type) in allowed_parameters:
        if filter_name in request.GET:
            value = None
            str_val = request.GET[filter_name]

            print 'type = {}'.format(filter_type)
            if filter_type == int:
                value = int(str_val)
            elif filter_type == bool:
                if str_val in BOOLEAN_TRUE_STRINGS:
                    value = True
                elif str_val in BOOLEAN_FALSE_STRINGS:
                    value = False
                else:
                    raise ValueError(
                        "Passed in expected bool '{val}' does not map to True or False".format(val=str_val)
                    )
            elif filter_type == str or filter_type == unicode:
                value = str_val
            else:
                raise ValueError('Unknown parameter type {name}'.format(name=filter_type))

            params[filter_name] = value

    return params


def _get_filter_and_options(request):
    """
    Helper method to construct a dict of all filter parameters
    that can be passed in from a query string
    """

    filters = _get_parameters_from_request(request, FILTER_PARAMETER_NAMES)
    options = _get_parameters_from_request(request, OPTIONS_PARAMETER_NAMES)

    return filters, options


class NotificationCount(AuthenticatedAPIView):
    """
    Returns the number of notifications for the logged in user
    """

    def get(self, request):
        """
        HTTP GET Handler
        """

        try:
            filters, __ = _get_filter_and_options(request)
        except ValueError:
            return Response({}, status.HTTP_400_BAD_REQUEST)

        print 'params = {}'.format(request.GET)
        print 'filters = {}'.format(filters)
        cnt = get_notifications_count_for_user(
            request.user.id,
            filters=filters
        )

        return Response(
            {
                'count': cnt,
            },
            status=status.HTTP_200_OK
        )


class NotificationDetail(AuthenticatedAPIView):
    """
    GET returns details on the notifications
    POST can mark notification
    """

    def get(self, request, msg_id):
        """
        HTTP GET Handler
        """

        try:
            user_msg = get_notifications_for_user(
                request.user.id,
                filters={
                    'msg_id': msg_id
                }
            )
        except ItemNotFoundError:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        return Response(user_msg[0].get_fields(), status.HTTP_200_OK)


class NotificationsList(AuthenticatedAPIView):
    """
    GET returns list of notifications
    """

    def get(self, request):
        """
        HTTP GET Handler
        """

        try:
            filters, options = _get_filter_and_options(request)
        except ValueError:
            return Response({}, status.HTTP_400_BAD_REQUEST)

        user_msgs = get_notifications_for_user(
            request.user.id,
            filters=filters,
            options=options,
        )

        resultset = [user_msg.get_fields() for user_msg in user_msgs]

        return Response(resultset, status.HTTP_200_OK)
