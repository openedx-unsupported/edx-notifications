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
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
    },
    'open-edx.lms.discussions.thread-followed': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
    },
    'open-edx.lms.discussions.post-upvoted': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
    },
    'open-edx.lms.discussions.comment-upvoted': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
    },
    'testserver.type1': {
        '_schema_version': 1,
        '_click_link': '',
        'subject': 'Test Notification',
        'body': 'Here is test notification that has a simple subject and body',
    },
    'open-edx.studio.announcements.new-announcement': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'course_name': 'Demo Course',
    },
    'open-edx.lms.discussions.cohorted-thread-added': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'link_to_thread': 'http://localhost',
    },
    'open-edx.lms.discussions.cohorted-comment-added': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'link_to_thread': 'http://localhost',
    },
    'open-edx.lms.leaderboard.progress.rank-changed': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'rank': 2,
    },
    'open-edx.lms.leaderboard.gradebook.rank-changed': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'rank': 3,
    },
    'open-edx.xblock.group-project.file-uploaded': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'action_username': 'testuser',
        'activity_name': 'First Activity',
        'verb': 'uploaded a file',
    },
    'open-edx.xblock.group-project.uploads-open': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
        'verb': 'Uploads are',
        'status': 'open',
    },
    'open-edx.xblock.group-project.uploads-due': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
        'verb': 'Uploads are',
        'status': 'due 4/18/2015',
    },
    'open-edx.xblock.group-project.reviews-open': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
        'verb': 'Review(s) are',
        'status': 'open',
    },
    'open-edx.xblock.group-project.reviews-due': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
        'verb': 'Review(s)',
        'status': 'due 4/25/2015',
    },
    'open-edx.xblock.group-project.grades-posted': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
        'verb': 'Grade(s) are',
        'status': 'posted',
    },
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


    # call to the helper method to build up all the context we need
    # to render the "notification_widget" that is embedded in our
    # test page
    context_dict = get_notifications_widget_context({
        'user': request.user,
        'notification_types': get_all_notification_types(),
        'global_variables': {
            'app_name': 'Notification Test Server',
        },
        # for test purposes, set up a short-poll which contacts the server
        # every 10 seconds to see if there is a new notification
        #
        # NOTE: short-poll technique should not be used in a production setting with
        # any reasonable number of concurrent users. This is just for
        # testing purposes.
        #
        'refresh_watcher': {
            'name': 'short-poll',
            'args': {
                'poll_period_secs': 10,
            },
        },
        'include_framework_js': True,
    })

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
