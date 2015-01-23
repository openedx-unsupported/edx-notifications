"""
Base objects that data.py uses
"""

from datetime import datetime


class TypedField(object):
    """
    Placeholder object to indicate that a field has not yet been set.
    This is because None is ambiguous as it might have semantic meaning
    even after an object has been initialized/loaded.
    """

    _expected_type = None

    def __init__(self, expected_type):
        """
        Initializer which takes in the type this field
        should be set it is set
        """

        self._expected_type = expected_type

    def assert_type(self, assert_type):
        """
        Asserts that the passed in type is the same as
        our expected type
        """

        if assert_type != self._expected_type:
            raise TypeError(
                (
                    "Field expected type of '{expected}' got '{got}'"
                ).format(expected=self._expected_type, got=assert_type)
            )


class StringTypedField(TypedField):
    """
    Specialized subclass of TypedField(unicode) as a convienence
    """

    def __init__(self):
        super(StringTypedField, self).__init__(unicode)


class IntegerTypedField(TypedField):
    """
    Specialized subclass of TypedField(int) as a convienence
    """

    def __init__(self):
        super(IntegerTypedField, self).__init__(int)


class DictTypedField(TypedField):
    """
    Specialized subclass of TypedField(dict) as a convienence
    """

    def __init__(self):
        super(DictTypedField, self).__init__(dict)


class DateTimeTypedField(TypedField):
    """
    Specialized subclass of TypedField(datetime) as a convienence
    """

    def __init__(self):
        super(DateTimeTypedField, self).__init__(datetime)


class BaseDataObject(object):
    """
    A base class for all Notification Data Objects
    """

    id = None  # pylint: disable=invalid-name

    _is_loaded = False
    _is_dirty = False  # Returns if this object has been modified after initialization

    def __init__(self, **kwargs):
        """
        Initializer which will allow for kwargs. Note we can only allow for setting
        of attributes which have been explicitly declared in any subclass
        """

        for key in kwargs.keys():
            value = kwargs[key]
            if key in dir(self):
                setattr(self, key, value)
            else:
                raise ValueError(
                    (
                        "Initialization parameter '{name}' was passed in although "
                        "it is not a known attribute to the class."
                    ).format(name=key)
                )

    def __setattr__(self, attribute, value):
        """
        Don't allow new attributes to be added outside of
        attributes that were present after initialization
        We want our data models to have a schema that is fixed as design time!!!
        """

        if not attribute in dir(self):
            raise ValueError(
                (
                    "Attempting to add a new attribute '{name}' that was not part of "
                    "the original schema."
                ).format(name=attribute)
            )

        existing = getattr(self, attribute)

        # see if we are replacing a TypeField, if so then the type's should match!
        # however we will allow for None to be always allowed
        is_existing_typed = isinstance(existing, TypedField)
        if is_existing_typed and value:
            # This will raise TypeError if we are attempting to set
            # an attribute of an unexpected type
            existing.assert_type(type(value))
        elif not is_existing_typed and value and existing:
            # if field has already been set, then we can't change
            # types (unless from or to None)
            if not isinstance(value, type(existing)):
                raise TypeError(
                    (
                        "Attempting to change a field from type '{from_type}' to '{to_type}'. "
                        "This is not allowed!"
                    ).format(from_type=type(existing), to_type=type(value))
                )

        super(BaseDataObject, self).__setattr__(attribute, value)

    def __getattribute__(self, attribute):
        """
        Allow for lazy loading of objects
        We assume that the 'id' field is already set
        So we can look it up in the database
        """

        value = super(BaseDataObject, self).__getattribute__(attribute)
        # be sure to add lazy loading
        return value
