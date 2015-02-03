"""
Notification Consumer HTTP-based API enpoints
"""

import logging

from rest_framework import status
from rest_framework.response import Response

from edx_notifications.lib.consumer import (
    get_notifications_count_for_user
)

from .api_utils import AuthenticatedAPIView

LOG = logging.getLogger("api")


class NotificationCount(AuthenticatedAPIView):
    """
    Returns the number of notifications for the logged in user
    """

    def get(self, request):
        """
        HTTP GET Handler
        """
        cnt = get_notifications_count_for_user(request.user.id)

        return Response(
            {
                'count': cnt,
            },
            status=status.HTTP_200_OK
        )
