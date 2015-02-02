"""
View handlers for HTML serving
"""

from functools import wraps
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from django.template import RequestContext, loader
from django.utils.decorators import available_attrs

from edx_notifications.api.consumer import (
    get_notifications_count_for_user,
)


def user_passes_test(test_func):
    """
    Helper method for the decorator in order to assert
    conditions
    """
    def decorator(view_func):
        """
        Outer wrapper
        """
        def _wrapped_view(request, *args, **kwargs):
            """
            inner wrapper which throws exception if conditiions are not met
            """
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator


def login_required_403(function=None):
    """
    Decorator to assert that a user is logged in
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated()
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


@login_required_403
def notification_count(request):
    """
    Returns a basic HTML snippet rendering of a notification count
    """

    template = loader.get_template('basic_notification_count.html')

    context = RequestContext(
        request,
        {
            'count': get_notifications_count_for_user(request.user.id),
        }
    )
    return HttpResponse(template.render(context))
