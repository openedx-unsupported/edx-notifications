"""
Notification types that will be used in common use cases for notifications around
course update announcements.
"""
from edx_notifications.renderers.basic import UnderscoreStaticFileRenderer


class NewCourseAnnouncementRenderer(UnderscoreStaticFileRenderer):
    """
    Renders a new-course-announcement notification
    """
    underscore_template_name = 'course_announcements/new_announcement.html'
