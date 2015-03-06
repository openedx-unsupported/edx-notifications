"""
Assortment of helper utility methods
"""

from django.templatetags.static import static
from django.core.urlresolvers import reverse


def get_template_path(template_name):
    """
    returns a full URL path to our template directory
    """

    return static(
        'edx_notifications/templates/{template_name}'.format(
            template_name=template_name
        )
    )


def get_audio_path(audio_name):
    """
    returns a full URL path to audio directory
    """

    return static(
        'edx_notifications/audio/{audio_name}'.format(
            audio_name=audio_name
        )
    )


def get_notifications_widget_context(override_context=None):
    """
    As a convenience method, this will return all required
    context properties that the notifications_widget.html Django template needs
    """

    context = {
        'endpoints': {
            'unread_notification_count': (
                '{base_url}?read=False&unread=True'
            ). format(base_url=reverse('edx_notifications.consumer.notifications.count')),
            'mark_all_user_notifications_read': (
                '{base_url}'
            ). format(base_url=reverse('edx_notifications.consumer.notifications.mark_notifications_as_read')),
            'user_notifications_unread_only': (
                '{base_url}?read=False&unread=True'
            ). format(base_url=reverse('edx_notifications.consumer.notifications')),
            'user_notifications_all': (
                '{base_url}?read=True&unread=True'
            ). format(base_url=reverse('edx_notifications.consumer.notifications')),
            'user_notification_mark_read': (
                '{base_url}'
            ). format(base_url=reverse('edx_notifications.consumer.notifications.detail.no_param')),
            'renderer_templates_urls': reverse('edx_notifications.consumer.renderers.templates'),
        },
        'global_variables': {
            'app_name': 'Your App Name Here',
        },
        'refresh_watchers': {
            'name': 'none',
            'args': {},
        },
        'view_audios': {
            'notification_alert': get_audio_path('notification_alert.mp3'),
        },
        # global notifications by default, callers should override this if they want to only
        # display notifications within a namespace
        'namespace': None,
    }

    if override_context:
        context.update(override_context)

    return context
