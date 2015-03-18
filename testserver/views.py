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
from django.conf import settings
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

# set up three optional namespaces that we can switch through to test proper
# isolation of Notifications
NAMESPACES = [None, 'foo/bar/baz', 'test/test/test']
NAMESPACE = None

CANNED_TEST_PAYLOAD = {
    'testserver.type1': {
        '_schema_version': 1,
        '_click_link': '',
        'subject': 'Test Notification',
        'body': 'Here is test notification that has a simple subject and body',
    },
    'testserver.msg-with-resolved-click-link': {
        '_schema_version': 1,
        'subject': 'Clickable Notification',
        'body': 'You should be able to click and redirect on this Notification',
    },
    'open-edx.lms.discussions.reply-to-thread': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
    },
    'open-edx.lms.discussions.thread-followed': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'num_followers': 3,
    },
    'open-edx.lms.discussions.post-upvoted': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'num_upvotes': 5,
    },
    'open-edx.lms.discussions.comment-upvoted': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'num_upvotes': 5,
    },
    'open-edx.studio.announcements.new-announcement': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'title': 'Gettysburg Address',
        'excerpt': 'Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.'
    },
    'open-edx.lms.discussions.cohorted-thread-added': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'excerpt': 'Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.'
    },
    'open-edx.lms.discussions.cohorted-comment-added': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'original_poster_id': 1,
        'action_user_id': 2,
        'action_username': 'testuser',
        'thread_title': 'A demo posting to the discussion forums',
        'excerpt': 'Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.'
    },
    'open-edx.lms.leaderboard.progress.rank-changed': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'rank': 2,
        'leaderboard_name': 'Progress'
    },
    'open-edx.lms.leaderboard.gradebook.rank-changed': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'rank': 3,
        'leaderboard_name': 'Proficiency'
    },
    'open-edx.lms.leaderboard.engagement.rank-changed': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'rank': 1,
        'leaderboard_name': 'Engagement'
    },
    'open-edx.xblock.group-project.file-uploaded': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'action_username': 'testuser',
        'activity_name': 'First Activity',
        'verb': 'uploaded a file',
    },
    'open-edx.xblock.group-project.stage-open': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
        'stage': 'Upload(s)',
    },
    'open-edx.xblock.group-project.stage-due': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
        'stage': 'Upload(s)',
        'due_date': '4/25'
    },
    'open-edx.xblock.group-project.grades-posted': {
        '_schema_version': 1,
        '_click_link': 'http://localhost',
        'activity_name': 'First Activity',
    },
}


@login_required
def index(request):
    """
    Returns a basic HTML snippet rendering of a notification count
    """
    global NAMESPACE

    if request.method == 'POST':
        if request.POST.get('change_namespace'):
            namespace_str = request.POST['namespace']
            NAMESPACE = namespace_str if namespace_str != "None" else None
        else:
            type_name = request.POST['notification_type']
            msg_type = get_notification_type(type_name)

            msg = NotificationMessage(
                msg_type=msg_type,
                namespace=NAMESPACE,
                payload=CANNED_TEST_PAYLOAD[type_name],
            )

            if type_name == 'testserver.msg-with-resolved-click-link':
                msg.add_click_link_params({
                    'param1': 'param_val1',
                    'param2': 'param_val2',
                })

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
            'hide_link_is_visible': settings.HIDE_LINK_IS_VISIBLE,
            'always_show_dates_on_unread': True,
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
        'namespace': NAMESPACE,
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
