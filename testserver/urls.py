"""
URL mappings for Notifications Server
"""

from __future__ import absolute_import

from django.urls import path, include
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.views import LoginView

from . import views as testserver_views


urlpatterns = [  # pylint: disable=invalid-name
    path('', testserver_views.index),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html')),
    path('logout/', testserver_views.logout_page),
    path('register/', testserver_views.register),
    path('register/success/', testserver_views.register_success),

    path('api/', include('edx_notifications.server.api.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]
