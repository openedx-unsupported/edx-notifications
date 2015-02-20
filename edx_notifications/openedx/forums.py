"""
Notification types that will be used in common use cases for notifications around
discussion forums
"""

from edx_notifications.renderers.basic import UnderscoreStaticFileRenderer


class ReplyToThreadRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a reply-to-thread notification
    """
    underscore_template_name = 'forums/reply_to_thread.html'


class ThreadFollowedRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a thread-followed notification
    """
    underscore_template_name = 'forums/thread_followed.html'


class PostUpvotedRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a post-upvoted notification
    """
    underscore_template_name = 'forums/post_upvoted.html'
