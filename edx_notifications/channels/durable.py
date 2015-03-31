"""
Implements a durable notification channel which will be a base class
that saves Notifications to a database for later
retrieval
"""

import logging
from importlib import import_module

from edx_notifications import const
from edx_notifications.channels.channel import BaseNotificationChannelProvider

from edx_notifications.stores.store import notification_store

from edx_notifications.data import (
    UserNotification,
    NotificationMessage,
)

log = logging.getLogger(__name__)


class BaseDurableNotificationChannel(BaseNotificationChannelProvider):
    """
    A durable notification channel will save messages to
    the database. This can be subclassed by any specialized
    Channel provider if it was to provide custom behavior (but still
    has the characteristic of using a durable stoage backend)
    """

    _cached_resolvers = {}

    def _get_linked_resolved_msg(self, msg):
        """
        This helper will attempt to resolve all
        links that are present in the message

        resolve any links that may need conversion into URL paths
        This uses a subdict named "_resolve_links" in the msg.resolve_links
        field:

            resolve_links = {
                "_resolve_links": {
                    "_click_link": {
                       "param1": "val1",
                       "param2": "param2"
                    },
                    :
                },
             :
            }

        This above will try to resolve the URL for the link named "_click_link" (for
        example, when a user clicks on a notification, the should go to that URL), with the
        URL parameters "param1"="val1" and "param2"="val2", and put that link name back in
        the main payload dictionary as "_click_link"
        """

        if msg.resolve_links:
            for link_name, link_params in msg.resolve_links.iteritems():
                resolved_link = self.resolve_msg_link(msg, link_name, link_params)
                if resolved_link:
                    # copy the msg because we are going to alter it and we don't want to affect
                    # the passed in version
                    msg = NotificationMessage.clone(msg)

                    # if we could resolve, then store the resolved link in the payload itself
                    msg.payload[link_name] = resolved_link

        # return the msg which could be a clone of the original one
        return msg

    def dispatch_notification_to_user(self, user_id, msg):
        """
        Send a notification to a user, which - in a durable Notification -
        is simply store it in the database, and - soon in the future -
        raise some signal to a waiting client that a message is available
        """

        store = notification_store()

        # get a msg (cloned from original) with resolved links
        msg = self._get_linked_resolved_msg(msg)

        # persist the message in our Store Provide
        _msg = store.save_notification_message(msg)

        # create a new UserNotification and point to the new message
        # this new mapping will have the message in an unread state
        # NOTE: We need to set this up after msg is saved otherwise
        # we won't have it's primary key (id)
        user_msg = UserNotification(
            user_id=user_id,
            msg=_msg
        )

        _user_msg = store.save_user_notification(user_msg)

        #
        # When we support in-broswer push notifications
        # such as Comet/WebSockets, this is where we should
        # signal the client to come fetch the
        # notification that has just been dispatched
        #

        #
        # Here is where we will tie into the Analytics pipeline
        #

        return _user_msg

    def bulk_dispatch_notification(self, user_ids, msg, exclude_user_ids=None):
        """
        Perform a bulk dispatch of the notification message to
        all user_ids that will be enumerated over in user_ids.

        NOTE: We will chunk together up to NOTIFICATION_BULK_PUBLISH_CHUNK_SIZE

        user_ids should be a list, a generator function, or a django.db.models.query.ValuesListQuerySet
        when directly feeding in a Django ORM queryset, where we select just the id column of the user
        """

        store = notification_store()

        # get a msg (cloned from original) with resolved links
        msg = self._get_linked_resolved_msg(msg)

        # persist the message in our Store Provide
        _msg = store.save_notification_message(msg)

        user_msgs = []

        exclude_user_ids = exclude_user_ids if exclude_user_ids else []

        cnt = 0
        total = 0

        # enumerate through the list of user_ids and chunk them
        # up. Be sure not to include any user_id in the exclude list
        for user_id in user_ids:
            if user_id not in exclude_user_ids:
                user_msgs.append(
                    UserNotification(
                        user_id=user_id,
                        msg=_msg
                    )
                )
                cnt = cnt + 1
                total = total + 1
                if cnt == const.NOTIFICATION_BULK_PUBLISH_CHUNK_SIZE:
                    store.bulk_create_user_notification(user_msgs)
                    user_msgs = []
                    cnt = 0

        if user_msgs:
            store.bulk_create_user_notification(user_msgs)

        return total

    def _get_link_resolver(self, resolver_name):
        """
        Returns a link resolver class from the name
        """

        # see if we have a cached resolver as it should be a singleton

        if resolver_name in self._cached_resolvers:
            return self._cached_resolvers[resolver_name]

        resolver = None
        if self.link_resolvers and resolver_name in self.link_resolvers:
            # need to have link_resolvers defined in our channel options config
            if 'class' in self.link_resolvers[resolver_name]:
                _class_name = self.link_resolvers[resolver_name]['class']
                config = {}
                if 'config' in self.link_resolvers[resolver_name]:
                    config = self.link_resolvers[resolver_name]['config']

                # now create an instance of the resolver
                module_path, _, name = _class_name.rpartition('.')
                class_ = getattr(import_module(module_path), name)
                resolver = class_(config)  # pylint: disable=star-args

                # put in our cache
                self._cached_resolvers[resolver_name] = resolver

        return resolver

    def resolve_msg_link(self, msg, link_name, params):
        """
        Generates the appropriate link given a msg, a link_name, and params
        """

        # right now we just support resolution through
        # type_name -> key lookups, aka 'type_to_url' in our
        # link_resolvers config dict. This is reserved for
        # future extension
        resolver = self._get_link_resolver('msg_type_to_url')

        resolved_link = None
        if resolver:
            resolved_link = resolver.resolve(msg.msg_type.name, link_name, params)

        return resolved_link
