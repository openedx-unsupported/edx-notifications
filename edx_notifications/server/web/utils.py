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


def get_notification_widget_context():
    """
    As a convenience method, this will return all required
    context properties that the notifications_widget needs
    """

    context = {
        'endpoints': {
            'unread_notification_count': (
                '{base_url}?read=False&unread=True'
            ). format(base_url=reverse('edx_notifications.consumer.notifications.count')),

            'user_notifications': reverse('edx_notifications.consumer.notifications'),
            'renderer_templates_urls': reverse('edx_notifications.consumer.renderers.templates'),
        },
        'view_templates': {
            'notification_icon': get_template_path('notification_icon.html'),
            'notification_pane': get_template_path('notification_pane.html'),
        }
    }

    return context
