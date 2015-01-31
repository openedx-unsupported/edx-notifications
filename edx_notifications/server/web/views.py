"""
View handlers for HTML serving
"""

from django.http import HttpResponse
from django.template import RequestContext, loader


def hello(request):
    """
    Test method
    """

    template = loader.get_template('test.html')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))
