"""
All pure data objects that the various Data Providers will product. This is help avoid
generic dictionaries from being passed around, plus this will help avoid any
implicit database-specific bindings that come with any uses of ORMs. Also this helps
with any serialization/deserializations if we separate out services
"""

from .utils import BaseInitializer


class NotificationMessage(BaseInitializer):
    """
    The basic notification Msg
    """

    msg_id = None
    payload = None
