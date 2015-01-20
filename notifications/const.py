"""
Lists of constants that can be used in the Notifications subsystem
"""

import sys


class _const(object):
    """
    Helper class for system constants as found at:
    http://code.activestate.com/recipes/65207-constants-in-python/?in=user-97991
    """
    class ConstError(TypeError):
        """
        Specialized exception
        """
        pass

    def __setattr__(self, name, value):
        """
        Override for the setter function, so that constants can only be set once
        during the runtime
        """
        if name in self.__dict__:
            # don't allow redefinition!
            raise self.ConstError("Can't rebind const({name})".format(name=name))

        self.__dict__[name] = value


sys.modules[__name__] = _const()
