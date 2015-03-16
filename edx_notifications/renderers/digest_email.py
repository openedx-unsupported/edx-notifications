from django.templatetags.static import static

from edx_notifications.renderers.renderer import BaseNotificationRenderer

from edx_notifications.const import (
    RENDER_FORMAT_UNDERSCORE,
    RENDER_FORMAT_DIGEST)



def path_to_digest_template(name):
    """
    Helper to construct a full path to where we have
    system defined Digest Email rendering templates
    """
    pass #TODO have to figure it out
    # return static(
    #     'edx_notifications/templates/renderers/{name}'.format(name=name)
    # )



class EmailDigestTemplateRenderer(BaseNotificationRenderer):
    """
    This subclass of BaseNotification only provides an Email Digest renderer.
    These templates will be used to render html for sending out Digest emails.
    """

    digest_notification_template_name = None

    def __init__(self, template_name=None):
        """
        Initializer
        """
        if template_name:
            self.digest_notification_template_name = template_name

    def can_render_format(self, render_format):
        """
        Returns (True/False) whether this renderer provides renderings
        into the requested format.
        """
        return render_format == RENDER_FORMAT_DIGEST

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

        if render_format == RENDER_FORMAT_DIGEST and self.digest_notification_template_name:
            return path_to_digest_template(self.digest_notification_template_name)

        raise NotImplementedError()


