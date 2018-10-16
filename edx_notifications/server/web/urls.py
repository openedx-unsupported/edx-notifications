"""
We currently have no server-side HTML generation. This file is reserved for future use.
"""
from settings import js_info_dict
from django.conf.urls import include, url
from django.views.i18n import javascript_catalog

urlpatterns = [  # pylint: disable=invalid-name

    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),

]
