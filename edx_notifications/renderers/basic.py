"""
Simple Subject/Body Underscore renderers
"""

import copy
from django.templatetags.static import static
from django.contrib.staticfiles import finders

from edx_notifications.renderers.renderer import BaseNotificationRenderer

from edx_notifications.const import (
    RENDER_FORMAT_UNDERSCORE,
)

from underscore import _ as us


def path_to_underscore_template(name):
    """
    Helper to construct a full path to where we have
    system defined Underscore rendering templates
    """

    return static(
        'edx_notifications/templates/renderers/{name}'.format(name=name)
    )


class UnderscoreStaticFileRenderer(BaseNotificationRenderer):
    """
    This subclass of BaseNotification only provides a Underscore client
    side rendering format. This subclass only implements the get_template_url
    to return a URL where a client can retrieve the template via HTTP request. Underscore
    templates must be able to be fetched via a public HTTP request
    """

    underscore_template_name = None
    underscore_template = None

    def __init__(self, template_name=None):
        """
        Initializer
        """
        if template_name:
            self.underscore_template_name = template_name

    def can_render_format(self, render_format):
        """
        Returns (True/False) whether this renderer provides renderings
        into the requested format.
        """
        return render_format == RENDER_FORMAT_UNDERSCORE

    def render(self, msg, render_format, lang):
        """
        This basic renderer just returns the subject in the Msg payload
        """
        if not self.can_render_format(render_format):
            NotImplementedError()

        if not self.underscore_template:
            template_url_path = self.get_template_path(render_format)
            underscore_filepath = finders.find(template_url_path)

            if not underscore_filepath:
                err_msg = (
                    'Could not resolve Underscore static url path {url_path} '
                    'to a filesystem path.'
                ).format(url_path=template_url_path)
                raise Exception(err_msg)

            with open(underscore_filepath, "r") as _file:
                template_string = _file.read()
                self.underscore_template = us.template(template_string)

        _payload = copy.deepcopy(msg.payload)
        _payload.update({
            '__view': 'default'
        })

        return self.underscore_template(msg.payload)

    def get_template_path(self, render_format):
        """
        Return a path to where a client can get the template
        """

        if render_format == RENDER_FORMAT_UNDERSCORE and self.underscore_template_name:
            return path_to_underscore_template(self.underscore_template_name)

        raise NotImplementedError()


class BasicSubjectBodyRenderer(UnderscoreStaticFileRenderer):
    """
    Return the appropriate Underscore template for this notification type
    """

    underscore_template_name = 'basic_subject_body.underscore'
