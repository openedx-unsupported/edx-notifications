"""
Django management command to raise a 'fire_background_notification_check' signal to all
application-level listeners
"""

import logging

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


def get_paths_for_digest_templates():
    """

    :return:
    """
    result_dict = {}
    for class_name, renderer in get_all_renderers().iteritems():
        if renderer['digest_renderer_instance'].can_render_format(const.RENDER_FORMAT_DIGEST):
            result_dict[class_name] = renderer['digest_renderer_instance'].get_template_path(const.RENDER_FORMAT_DIGEST)
    return result_dict

class Command(BaseCommand):
    """
    Django Management command to force a background check of all possible notifications
    """

    def handle(self, *args, **options):
        """
        Management command entry point, simply call into the signal firiing
        """
        print('Hello World')
        startup.initialize()
        result_dict = get_paths_for_digest_templates()
        render_templates = {}
        # get all the users
        users = User.objects.all()
        for user in users:
            # now get all the user notifications.
            html = []
            user_msgs = get_notifications_for_user(
                int(user.id)
            )
            user_email = user.email
            resultset = [user_msg.get_fields() for user_msg in user_msgs]
            for result in resultset:
                if result['msg']['msg_type']['renderer'] in result_dict:
                    context = Context(result['msg']['payload'])
                    template = loader.get_template(result_dict[result['msg']['msg_type']['renderer']])
                    template.render(context)
