"""
Django management command to raise a 'fire_background_notification_check' signal to all
application-level listeners
"""

import logging
from itertools import groupby
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template import Context, loader
log = logging.getLogger(__file__)
from edx_notifications import startup
from edx_notifications.lib.consumer import get_notifications_for_user
from edx_notifications.renderers.renderer import (
    get_all_renderers,
)
from edx_notifications import const

# this describes how we want to group together notification types into visual groups
grouping_config = {
    'groups': {
        'announcements': {
            'name': 'announcements',
            'display_name': 'Announcements',
            'group_order': 1
        },
        'group_work': {
            'name': 'group_work',
            'display_name': 'Group Work',
            'group_order': 2
        },
        'leaderboards': {
            'name': 'leaderboards',
            'display_name': 'Leaderboards',
            'group_order': 3
        },
        'discussions': {
            'name': 'discussions',
            'display_name': 'Discussion',
            'group_order': 4
        },
        '_default': {
            'name': '_default',
            'display_name': 'Other',
            'group_order': 5
        },
    },
    'type_mapping': {
        'open-edx.lms.discussions.cohorted-thread-added': 'group_work',
        'open-edx.lms.discussions.cohorted-comment-added': 'group_work',
        'open-edx.lms.discussions.*': 'discussions',
        'open-edx.lms.leaderboard.*': 'leaderboards',
        'open-edx.studio.announcements.*': 'announcements',
        'open-edx.xblock.group-project.*': 'group_work',
        '*': '_default'
    },
}


def get_path_for_digest_templates():
    """
    returns a list of all digest format templates that have been registered in the system.
    """
    result_dict = {}
    for class_name, renderer in get_all_renderers().iteritems():
        if renderer['digest_renderer_instance'].can_render_format(const.RENDER_FORMAT_DIGEST):
            result_dict[class_name] = renderer['digest_renderer_instance'].get_template_path(const.RENDER_FORMAT_DIGEST)
    return result_dict


def get_group_name_for_msg_type(msg_type):
    """
    Returns the particular group_name for the msg_type
    else return None if no group_name is found.
    """
    if msg_type in grouping_config['type_mapping']:
        group_name = grouping_config['type_mapping'][msg_type]
        if group_name in grouping_config['groups']:
            return group_name

    # no exact match so lets look upwards for wildcards
    search_type = msg_type
    dot_index = search_type.rindex('.')
    while dot_index != -1 and search_type != '*':
        search_type = search_type[0: dot_index]
        key = search_type + '.*'

        if key in grouping_config['type_mapping']:
            group_name = grouping_config['type_mapping'][key]
            if group_name in grouping_config['groups']:
                return group_name

        dot_index = search_type.rindex('.')

    # look for global wildcard
    if '*' in grouping_config['type_mapping']:
        key = '*'
        group_name = grouping_config['type_mapping'][key]
        if group_name in grouping_config['groups']:
            return group_name

    # this really shouldn't happen. This means misconfiguration
    return None


def get_group_rendering(group_data):
    """
    returns the list of the sorted user notifications renderings.
    """
    renderings = []
    result_dict = get_path_for_digest_templates()
    group_data = sorted(group_data, key=lambda k: k['msg']['created'])

    for user_msg in group_data:
        msg = user_msg['msg']
        render_context = msg['payload']
        created_date = msg['created']

        if datetime.date(created_date) == datetime.today().date():
            created_str = 'Today at ' + created_date.strftime("%H:%M%p")
        else:
            created_str = created_date.strftime("%B %d, %Y") + ' at ' + created_date.strftime("%H:%M%p")

        render_context.update({
            'display_created': created_str
        })
        renderer_class_name = msg['msg_type']['renderer']
        if renderer_class_name in result_dict:
            context = Context(render_context)
            template = loader.get_template(result_dict[renderer_class_name])
            notification_html = template.render(context)
            renderings.append({
                'user_msg': user_msg,
                'msg': msg,
                # render the particular NotificationMessage
                'html': notification_html,
                'group_name': get_group_name_for_msg_type(msg['msg_type']['name'])
            })

    return renderings


class Command(BaseCommand):
    """
    Django Management command to force a background check of all possible notifications
    """

    def handle(self, *args, **options):
        """
        Management command entry point, simply call into the signal firiing
        """
        # initialize the notification subsystem
        startup.initialize()

        # get all the users
        users = User.objects.all()

        for user in users:
            # now get all the user notifications.
            notification_groups = []
            user_msgs = get_notifications_for_user(
                int(user.id)
            )
            user_email = user.email
            result_set = [user_msg.get_fields() for user_msg in user_msgs]
            grouped_data = {}

            # group the user notifications by message type name.
            for key, group in groupby(result_set, lambda x: get_group_name_for_msg_type(x['msg']['msg_type']['name'])):
                for thing in group:
                    if key in grouped_data:
                        grouped_data[key].append(thing)
                    else:
                        grouped_data[key] = [thing]

            # then we want to order the groups according to the grouping_config
            # so we can specify which groups go up at the top
            group_orderings = sorted(grouping_config['groups'].items(), key=lambda t: t[1]['group_order'])

            for group_key, _ in group_orderings:
                if group_key in grouped_data:
                    notification_groups.append(
                        {
                            'group_title': grouping_config['groups'][group_key]['display_name'],
                            'messages': get_group_rendering(grouped_data[group_key])
                        }
                    )
