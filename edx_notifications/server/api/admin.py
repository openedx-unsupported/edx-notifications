"""
Administration endpoints
"""
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseForbidden

from edx_notifications.lib.admin import purge_user_data
from edx_notifications.server.api.api_utils import AuthenticatedAPIView


class DeleteUsersData(AuthenticatedAPIView):
    """
    POST removes all data for given user IDs
    """

    def post(self, request):
        """
        HTTP POST Handler
        """
        if 'user_ids' not in request.data:
            return HttpResponseBadRequest('Missing user ids')
        if not request.user.is_staff:
            return HttpResponseForbidden()
        user_ids = request.data.get('user_ids')
        purge_user_data(user_ids)
        return HttpResponse(status=204)
