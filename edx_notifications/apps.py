"""
Configuration for edx_notifications Django app
"""
from __future__ import absolute_import

import logging

from django.apps import AppConfig
from django.conf import settings


log = logging.getLogger(__name__)


class EdxNotificationsConfig(AppConfig):
    """
    Configuration class for edx_notifications Django app
    """
    name = 'edx_notifications'
    verbose_name = "Notification subsystem"

    def ready(self):
        if settings.FEATURES.get('ENABLE_NOTIFICATIONS', False):
            startup_notification_subsystem()


def startup_notification_subsystem():
    """
    Initialize the Notification subsystem
    """
    try:
        from openedx.core.djangoapps.course_groups.scope_resolver import CourseGroupScopeResolver
        from student.scope_resolver import CourseEnrollmentsScopeResolver, StudentEmailScopeResolver  # pylint: disable=import-error
        from edx_solutions_projects.scope_resolver import GroupProjectParticipantsScopeResolver
        from edx_notifications.scopes import register_user_scope_resolver
        from edx_notifications.namespaces import register_namespace_resolver
        from util.namespace_resolver import CourseNamespaceResolver  # pylint: disable=import-error
        from edx_notifications import startup

        startup.initialize()

        # register the scope resolvers that the runtime will be providing to edx-notifications.
        register_user_scope_resolver('course_enrollments', CourseEnrollmentsScopeResolver())
        register_user_scope_resolver('course_group', CourseGroupScopeResolver())
        register_user_scope_resolver('group_project_participants', GroupProjectParticipantsScopeResolver())
        register_user_scope_resolver('group_project_workgroup', GroupProjectParticipantsScopeResolver())
        register_user_scope_resolver('user_email_resolver', StudentEmailScopeResolver())

        # register namespace resolver
        register_namespace_resolver(CourseNamespaceResolver())
    except Exception as ex:
        # Note this will fail when we try to run migrations as manage.py will call startup.py
        # and startup.initialze() will try to manipulate some database tables.
        # We need to research how to identify when we are being started up as part of
        # a migration script
        log.error(
            'There was a problem initializing notifications subsystem. '
            'This could be because the database tables have not yet been created and '
            './manage.py lms syncdb needs to run setup.py. Error was "%s". Continuing...', str(ex)
        )
