"""
File containing link resolvers
"""

import logging
import abc

log = logging.getLogger(__name__)


class BaseLinkResolver(object):
    """
    The abstract base class that all link resolvers will need to implement
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def resolve(self, msg_type_name, link_name, params):
        """
        Takes a msg, link_name, and a set of dictionary params
        and returns a URL path
        """
        raise NotImplementedError()


class MsgTypeToUrlLinkResolver(BaseLinkResolver):
    """
    This resolver will convert a msg-type to a URL through
    static mappings defined in our settings configuration
    """

    def __init__(self, mappings):
        """
        Initializer. Mappings will include all the
        statically defined URL mappings
        """

        self.mappings = mappings

    def resolve(self, msg_type_name, link_name, params):
        """
        Takes a msg, link_name, and a set of dictionary params
        and returns a URL path
        """

        # do we have this link name?
        if link_name not in self.mappings:
            return None

        # do we have this msg-type?
        if msg_type_name not in self.mappings[link_name]:
            return None

        try:
            return self.mappings[link_name][msg_type_name].format(**params)  # pylint:disable=star-args
        except KeyError, ex:
            err_msg = (
                'TypeToURLResolver: attempted to resolve link_name "{link_name}" '
                'for msg_type "{msg_type}" with string "{format_string}" and '
                'parameters "{params}, but got KeyError: "{ex_msg}"! Check the configuration '
                'and caller!'
            ).format(
                link_name=link_name,
                msg_type=msg_type_name,
                format_string=self.mappings[link_name][msg_type_name],
                params=params,
                ex_msg=str(ex)
            )
            log.error(err_msg)
            # simply continue by returning None. Upstream will consider this as
            # not resolvable
            return None
