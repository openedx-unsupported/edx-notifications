"""
Notification Consumer HTTP-based API enpoints
"""

import logging

from rest_framework import status
from rest_framework.response import Response

from django.http import Http404

from edx_notifications.lib.consumer import (
    get_notifications_count_for_user,
    get_notifications_for_user,
    get_notification_for_user,
    mark_notification_read,
    mark_all_user_notification_as_read
)

from edx_notifications.renderers.renderer import (
    get_all_renderers,
)

from edx_notifications.exceptions import (
    ItemNotFoundError,
)

from edx_notifications import const

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


def _find_notification_by_id(user_id, msg_id):
    """
    Helper method to look up a notification for a user, if it is not
    found then raise a Http404
    """

    try:
        user_msg = get_notification_for_user(int(user_id), int(msg_id))
    except ItemNotFoundError:
        raise Http404()

    return user_msg


class NotificationDetail(AuthenticatedAPIView):
    """
    GET returns details on the notifications
    POST can mark notification
    """

    _allowed_post_parameters = {
        'mark_as': ['read', 'unread'],
    }

    def get(self, request, msg_id):
        """
        HTTP GET Handler
        """

        # Get msg for user, raise Http404 if not found
        user_msg = _find_notification_by_id(request.user.id, int(msg_id))

        return Response(user_msg.get_fields(), status.HTTP_200_OK)

    def post(self, request, msg_id):
        """
        HTTP POST Handler which is used for such use-cases as 'mark as read'
        and 'mark as unread'
        """

        # make sure we only have expected parameter names and values
        if not self.validate_post_parameters(request):
            return Response({}, status.HTTP_400_BAD_REQUEST)

        if 'mark_as' in request.DATA:
            mark_as_read = request.DATA['mark_as'] == 'read'
            try:
                # this will raise an ItemNotFoundError if the user_id/msg_id combo
                # cannot be found
                mark_notification_read(request.user.id, int(msg_id), read=mark_as_read)
            except ItemNotFoundError:
                raise Http404()

        return Response({}, status.HTTP_200_OK)


class MarkNotifications(AuthenticatedAPIView):
    """
    Mark all the user notifications as read
    """

    def post(self, request):
        """
        HTTP POST Handler which is used for such use-cases as 'mark as read'
        """
        try:
            # this will raise an ItemNotFoundError if the user_id/msg_id combo
            # cannot be found
            mark_all_user_notification_as_read(request.user.id)
        except ItemNotFoundError:
            raise Http404()

        return Response({'success': True}, status.HTTP_200_OK)


class RendererTemplatesList(AuthenticatedAPIView):
    """
    GET returns a list of all Underscore templates that have been registered in the system
    """

    def get(self, request):  # pylint: disable=unused-argument
        """
        HTTP Get Handler
        """

        result_dict = {}

        for class_name, renderer in get_all_renderers().iteritems():
            if renderer.can_render_format(const.RENDER_FORMAT_UNDERSCORE):
                result_dict[class_name] = renderer.get_template_path(const.RENDER_FORMAT_UNDERSCORE)

        return Response(result_dict, status.HTTP_200_OK)
