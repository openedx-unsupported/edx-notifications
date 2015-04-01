"""
Tests for renderer.py
"""

from django.test import TestCase

from edx_notifications.const import RENDER_FORMAT_UNDERSCORE, RENDER_FORMAT_SMS
from edx_notifications.renderers.renderer import (
    BaseNotificationRenderer
)

from edx_notifications.renderers.basic import (
    UnderscoreStaticFileRenderer
)

from edx_notifications.data import NotificationMessage, NotificationType
from edx_notifications.lib.publisher import register_notification_type


class TestBadRenderer(BaseNotificationRenderer):
    """
    For test purposes derive from BaseNotificationRenderer but only
    access base implementation
    """

    def can_render_format(self, render_format):
        """
        Returns (True/False) whether this renderer provides renderings
        into the requested format.
        """
        super(TestBadRenderer, self).can_render_format(render_format)

    def render_subject(self, msg, render_format, lang):
        """
        This basic renderer just returns the subject in the Msg payload
        """
        super(TestBadRenderer, self).render_subject(msg, render_format, lang)

    def render_body(self, msg, render_format, lang):
        """
        This basic renderer just returns the  body that is in the Msg payload
        """
        super(TestBadRenderer, self).render_body(msg, render_format, lang)

    def get_template_path(self, render_format):
        """
        Return a path to where a client can get the template
        """
        super(TestBadRenderer, self).get_template_path(render_format)


class TestUnderscoreStaticFileRenderer(UnderscoreStaticFileRenderer):
    """
    Simulates the use of an Underscore renderer
    """
    underscore_template_name = 'foo.underscore'


class RendererTests(TestCase):
    """
    Test cases for renderer.py
    """

    def test_no_base_instatiation(self):
        """
        Asserts that we cannot create an instance of the abstract
        base class
        """

        with self.assertRaises(TypeError):
            BaseNotificationRenderer()  # pylint: disable=abstract-class-instantiated

    def test_cant_access_base_classes(self):
        """
        Try to access a test derived class from BaseNotificationRenderer
        that only delegates to the base class
        """

        bad = TestBadRenderer()

        with self.assertRaises(NotImplementedError):
            bad.can_render_format(None)

        with self.assertRaises(NotImplementedError):
            bad.render_subject(None, None, None)

        with self.assertRaises(NotImplementedError):
            bad.render_body(None, None, None)

        with self.assertRaises(NotImplementedError):
            bad.get_template_path(None)

    def test_underscore(self):
        """
        Tests on the UnderscoreStaticFileRenderer
        """

        renderer = TestUnderscoreStaticFileRenderer('foo.underscore')

        self.assertTrue(renderer.can_render_format(RENDER_FORMAT_UNDERSCORE))

        msg_type = NotificationType(
            name='open-edx.edx_notifications.lib.tests.test_publisher',
            renderer='edx_notifications.renderers.basic.BasicSubjectBodyRenderer',
        )
        register_notification_type(msg_type)

        msg = NotificationMessage(
            namespace='test-runner',
            msg_type=msg_type,
            payload={
                'subject': 'test subject',
                'body': 'test body',
            }
        )

        self.assertEqual(
            renderer.render_subject(
                msg,
                RENDER_FORMAT_UNDERSCORE,
                None
            ),
            'test subject'
        )

        self.assertEqual(
            renderer.render_body(
                msg,
                RENDER_FORMAT_UNDERSCORE,
                None
            ),
            'test body'
        )

        url = renderer.get_template_path(RENDER_FORMAT_UNDERSCORE)

        with self.assertRaises(NotImplementedError):
            url = renderer.get_template_path(RENDER_FORMAT_SMS)
