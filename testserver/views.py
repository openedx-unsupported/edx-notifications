"""
View handlers for HTML serving
"""

from django.template import RequestContext, loader
from django.http import (
    HttpResponse,
)

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect

from edx_notifications.lib.publisher import (
    publish_notification_to_user,
    get_notification_type,
    get_all_notification_types,
)

from edx_notifications.data import (
    NotificationMessage,
)

from edx_notifications.server.web.utils import get_notifications_widget_context

from .forms import *


@login_required
def index(request):
    """
    Returns a basic HTML snippet rendering of a notification count
    """

    if request.method == 'POST':
        type_name = request.POST['notification_type']
        msg_type = get_notification_type(type_name)

        msg = NotificationMessage(
            msg_type=msg_type,
            payload={
                'subject': 'Test Notification',
                'body': 'Here is test notification that has a simple subject and body',
            }
        )

        publish_notification_to_user(request.user.id, msg)

    template = loader.get_template('index.html')

    context_dict = {
        'user': request.user,
        'notification_types': get_all_notification_types(),
    }

    # call to the helper method to build up all the context we need
    # to render the "notification_widget" that is embedded in our
    # test page
    context_dict.update(get_notifications_widget_context())

    return HttpResponse(template.render(RequestContext(request, context_dict)))


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
        variables = RequestContext(
            request, {
                'form': form
            }
        )

    return render_to_response(
        'registration/register.html',
        variables,
    )

def register_success(request):
    return render_to_response(
        'registration/success.html',
    )

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
