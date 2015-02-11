"""
Simple Subject/Body Underscore renderers
"""

from django.templatetags.static import static

from edx_notifications.renderers.renderer import BaseNotificationRenderer

from edx_notifications.const import (
    RENDER_FORMAT_UNDERSCORE,
)


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

    underscore_template_path = None

    def can_render_format(self, render_format):
        """
        Returns (True/False) whether this renderer provides renderings
        into the requested format.
        """
        return render_format == RENDER_FORMAT_UNDERSCORE

    def render_subject(self, msg, render_format, lang):
        """
        This basic renderer just returns the subject in the Msg payload
        """
        return msg.payload['subject']

    def render_body(self, msg, render_format, lang):
        """
        This basic renderer just returns the  body that is in the Msg payload
        """
        return msg.payload['body']

    def get_template_path(self, render_format):
        """
        Return a path to where a client can get the template
        """

        if render_format == RENDER_FORMAT_UNDERSCORE and self.underscore_template_path:
            return self.underscore_template_path

        raise NotImplementedError()


class BasicSubjectBodyRenderer(UnderscoreStaticFileRenderer):
    """
    Return the appropriate Underscore template for this notification type
    """

    underscore_template_path = path_to_underscore_template('basic_subject_body.html')
