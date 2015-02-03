"""
A abstract class defining the interface methods that a notification will
implement

A NotificationRenderer knows how to take a NotificationMessage and present
a rendering of that message to a particular format, such as json, HTML, etc.

Note that a NotificationRender can be associated with more than one
NotificationType
"""

import abc


class BaseNotificationRenderer(object):
    """
    Abstract Base Class for NotificationRender types.

    A NotificationRender knows how to convert a NotificationMessage payload into
    a human (e.g. HTML, text, etc) or machine (e.g. JSON) renderer format.

    Note: with the utilization of the abc.abstractmethod decorators you cannot
    create an instance of the class directly
    """

    # don't allow instantiation of this class, it must be subclassed
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def can_render_format(self, msg, render_format):
        """
        Returns (True/False) whether this renderer is able to convert the passed in message
        into the requested format.
        """

    @abc.abstractmethod
    def can_render_lang(self, msg, lang):
        """
        Returns (True/False) whether this renderer is able to covert the passed in message
        into the requested language
        """

    @abc.abstractmethod
    def render_subject(self, msg, render_format, lang):
        """
        Renders a subject line for this particular notification in the requested format and
        language

        If subclasses returns None or empty string, then the caller will
        subsitute a generic subject, e.g. "You have received a notification..."
        if the NotificationChannel *must* have a subject line, for example
        email-based delivery channels.

        If the requested language is not supported then subclasses should
        throw a NotificationLanguageNotSupported exception. The calling code
        should trap that and try with a different language
        """

        # Base implementation will say it cannot render a Subject
        return None

    @abc.abstractmethod
    def render_body(self, msg, render_format, lang):
        """ for
        Renders a body for this particular notification in the requested format and language

        If the requested language is not supported then subclasses should
        throw a NotificationLanguageNotSupported exception. The calling code
        should trap that and try with a different language
        """
