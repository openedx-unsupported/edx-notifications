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
from django.templatetags.static import static

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


CANNED_TEST_PAYLOAD = {
    'open-edx.lms.discussions.reply-to-thread': {
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'link_to_thread': 'http://localhost',
    },
    'open-edx.lms.discussions.thread-followed': {
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'link_to_thread': 'http://localhost',
    },
    'open-edx.lms.discussions.post-upvoted': {
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'link_to_thread': 'http://localhost',
    },
    'testserver.type1': {
        'subject': 'Test Notification',
        'body': 'Here is test notification that has a simple subject and body',
    },
    'open-edx.studio.announcements.new_announcement': {
        'course_name': 'Demo Course',
    }
}


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
            payload=CANNED_TEST_PAYLOAD[type_name],
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

    # we always need to pass along the URL to the RequireJS main
    context_dict['requirejs_main_url'] = static('js/main.js')

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
            raise Exception('Invalid registration form')
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
