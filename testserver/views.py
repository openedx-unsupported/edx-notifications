"""
View handlers for HTML serving
"""

from django.template import RequestContext, loader
from django.http import (
    HttpResponse,
)

def login(request):
    """
    Returns a basic HTML snippet rendering of a notification count
    """

    template = loader.get_template('login.html')

    context = RequestContext(request, {'count': 99 })
    return HttpResponse(template.render(context))
