"""
Abstract base class that all NotificationChannels must implement
"""

import abc
import copy

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

        options = copy.deepcopy(channel_config['options'])
        options['name'] = key

        provider = class_(**options)  # pylint: disable=star-args
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
        mapping = mappings.get(search_name)
        if not mapping:
            search_name, __, __ = search_name.rpartition('.')

            # loop over all possible wildcards throughout the namespace
            # from most specific to generic
            while not mapping and search_name:
                mapping = mappings.get(search_name + '.*')
                if not mapping:
                    search_name, __, __ = search_name.rpartition('.')

            if not mapping:
                # did we reach the end without a mapping found? Use the global wildcard '*'
                mapping = mappings.get('*')
                if not mapping:
                    # oops, this shouldn't happen if things are configured correctly
                    msg = (
                        "NOTIFICATION_CHANNEL_PROVIDERS is not configured "
                        "with a global '*' definition. This must always be defined."
                    )
                    raise ImproperlyConfigured(msg)

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

    NOTE: When we switch over to gevent support, we should use some
    locking techniques in this area to prevent concurrent execution
    """

    global _CHANNEL_PROVIDERS  # pylint: disable=global-statement, global-variable-not-assigned

    if not _CHANNEL_PROVIDERS:
        _init_channel_providers()

    # first see what the user preference is
    channel = _get_channel_preference(user_id, msg_type)  # pylint: disable=assignment-from-none
    if not channel:
        channel = _get_system_channel_mapping(msg_type.name)

    return channel


def reset_notification_channels():
    """
    Clear out all cached channel definitions and mappings.
    This is useful for testing scenarious, but likely should not
    be called in normal runtimes

    NOTE: When we switch over to gevent support, we should use some
    locking techniques in this area to prevent concurrent execution
    """

    global _CHANNEL_PROVIDERS  # pylint: disable=global-statement
    global _CHANNEL_PROVIDERS_TYPE_MAPS  # pylint: disable=global-statement

    _CHANNEL_PROVIDERS = {}
    _CHANNEL_PROVIDERS_TYPE_MAPS = {}


class BaseNotificationChannelProvider(object):
    """
    The abstract base class that all NotificationChannelProviders
    need to implement
    """

    # Name of the notification channel
    _name = None
    _display_name = None
    _display_description = None

    @property
    def name(self):
        """
        Getter for _name field
        """
        return self._name

    @property
    def display_name(self):
        """
        Getter for _display_name field
        """
        return self._display_name

    @property
    def display_description(self):
        """
        Getter for _display_description
        """
        return self._display_description

    # don't allow instantiation of this class, it must be subclassed
    __metaclass__ = abc.ABCMeta

    def __init__(self, name=None, display_name=None, display_description=None):
        """
        Base implementation of __init__
        """

        self._name = name
        self._display_name = display_name
        self._display_description = display_description

    @abc.abstractmethod
    def dispatch_notification_to_user(self, user_id, msg):
        """
        Send a notification to a user. It is assumed that
        'user_id' and 'msg' are valid and have already passed
        all necessary validations
        """
