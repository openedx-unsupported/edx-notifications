"""
Abstract base class that all NotificationChannels must implement
"""

import abc

from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_CHANNEL_PROVIDERS = {}
_CHANNEL_PROVIDERS_TYPE_MAPS = {}


def _init_channel_providers():
    """
    Initialize all the channel provider singletons
    """

    global _CHANNEL_PROVIDERS  # pylint: disable=global-statement,global-variable-not-assigned

    config = getattr(settings, 'NOTIFICATION_CHANNEL_PROVIDERS')

    if not config:
        raise ImproperlyConfigured("Settings not configured with NOTIFICATION_CHANNEL_PROVIDERS!")

    for key, channel_config in config.iteritems():
        if 'class' not in channel_config or 'options' not in channel_config:
            msg = (
                "Misconfigured NOTIFICATION_CHANNEL_PROVIDERS settings, "
                "must have both 'class' and 'options' defined for all providers."
            )
            raise ImproperlyConfigured(msg)

        module_path, _, name = channel_config['class'].rpartition('.')
        class_ = getattr(import_module(module_path), name)

        provider = class_(**channel_config['options'])
        _CHANNEL_PROVIDERS[key] = provider


def _get_system_channel_mapping(type_name):
    """
    Return the NotificationType<-->NotificationChannel that is
    defined at the system (aka settings) level
    """

    global _CHANNEL_PROVIDERS_TYPE_MAPS  # pylint: disable=global-statement, global-variable-not-assigned

    if type_name not in _CHANNEL_PROVIDERS_TYPE_MAPS:
        mappings = getattr(settings, 'NOTIFICATION_CHANNEL_PROVIDER_TYPE_MAPS')

        if not mappings:
            raise ImproperlyConfigured("Settings not configured with NOTIFICATION_CHANNEL_PROVIDER_TYPE_MAPS!")

        search_name = type_name

        # traverse upwards in the type namespacing to find a match
        # most specific takes presendence
        # most generic is '*'
        if search_name not in mappings:
            search_name, __, __ = search_name.rpartition('.')

            while (search_name + '.*') not in mappings:
                search_name, __, __ = search_name.rpartition('.')

                # at the end?
                if not search_name:
                    break

            if not search_name:
                search_name = '*'
                # no match then, we take the global '*'
                if search_name not in mappings:
                    msg = (
                        "NOTIFICATION_CHANNEL_PROVIDERS is not configured "
                        "with a global '*' definition. This must always be defined."
                    )
                    raise ImproperlyConfigured(msg)

        mapping = mappings[search_name]

        if mapping not in _CHANNEL_PROVIDERS:
            msg = (
                "Bad mapping of NotificationType to NotificationChannel. "
                "Mapping was looking for NotificationChannel {name} but "
                "it was not found".format(name=mapping)
            )
            raise ImproperlyConfigured(msg)

        _CHANNEL_PROVIDERS_TYPE_MAPS[type_name] = _CHANNEL_PROVIDERS[mapping]

    return _CHANNEL_PROVIDERS_TYPE_MAPS[type_name]


def _get_channel_preference(user_id, msg_type):  # pylint: disable=unused-argument
    """
    Returns what the user has chosen to be his/her preference
    for notifications.

    Return of None = no preference declared
    """

    # not yet implemented
    return None


def get_notification_channel(user_id, msg_type):
    """
    Returns the appropriate NotificationChannel
    for this user and msg_type.

    Ultimately, this will be user-selectable, e.g.
    'send my discussion forum notifications to my mobile device via SMS'
    but for now, we're always mapping to the system default
    """

    global _CHANNEL_PROVIDERS  # pylint: disable=global-statement, global-variable-not-assigned

    if not _CHANNEL_PROVIDERS:
        _init_channel_providers()

    # first see what the user preference is
    channel = _get_channel_preference(user_id, msg_type)  # pylint: disable=assignment-from-none
    if not channel:
        channel = _get_system_channel_mapping(msg_type.name)

    return channel


class BaseNotificationChannelProvider(object):
    """
    The abstract base class that all NotificationChannelProviders
    need to implement
    """

    @abc.abstractmethod
    def dispatch_notification_to_user(self, user_id, msg):
        """
        Send a notification to a user. It is assumed that
        'user_id' and 'msg' are valid and have already passed
        all necessary validations
        """
