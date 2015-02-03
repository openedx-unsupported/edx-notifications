"""
Helpers for the HTTP APIs
"""

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication


class AuthenticatedAPIView(APIView):
    """
    Returns the number of notifications for the logged in user
    """
    authentication_classes = (SessionAuthentication,)
