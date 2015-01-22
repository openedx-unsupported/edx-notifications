"""
Helpful utilities and base classes
"""


class BaseInitializer(object):
    """
    A base class that allows for kwarg based initialization
    """

    def __init__(self, **kwargs):
        """
        Initializer which will allow for kwargs. Note we can only allow for setting
        of attributes which have been explicitly declared in any subclass
        """

        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
            else:
                raise Exception(
                    (
                        "Initialization parameter '{name}' was passed in although"
                        "it is not a known attribute to the class."
                    ).format(name=key)
                )
