"""
Base objects that data.py uses
"""

import json
import copy
import dateutil.parser

from datetime import datetime

from weakref import WeakKeyDictionary


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

        if attribute not in dir(self):
            raise ValueError(
                (
                    "Attempting to add a new attribute '{name}' that was not part of "
                    "the original schema."
                ).format(name=attribute)
            )

        super(BaseDataObject, self).__setattr__(attribute, value)

    def __eq__(self, other):
        """
        Equality test - simply compare all of the fields
        """

        return self.__dict__ == other.__dict__


class TypedField(object):
    """
    Field Decscriptors used to enforce correct typing
    """

    _expected_type = None

    def __init__(self, expected_type, default=None):
        """
        Initializer which takes in the type this field
        should be set it is set
        """

        self._expected_type = expected_type
        self._default = default
        self._data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        """
        Descriptor getter
        """
        return self._data.get(instance, self._default)

    def __set__(self, instance, value):
        """
        Descriptor setter. Be sure to enforce type on setting. But None is allowed.
        """

        value_type = type(value)
        if value and type(value) != self._expected_type:
            raise TypeError(
                (
                    "Field expected type of '{expected}' got '{got}'"
                ).format(expected=self._expected_type, got=value_type)
            )
        self._data[instance] = value


class StringField(TypedField):
    """
    Specialized subclass of TypedField(unicode) as a convienence
    """

    def __init__(self):
        super(StringField, self).__init__(unicode)

    def __set__(self, instance, value):
        """
        Check to see if we were passed a str type, and if so
        coerce it into a unicode
        """

        if isinstance(value, str):
            super(StringField, self).__set__(instance, unicode(value))
        else:
            super(StringField, self).__set__(instance, value)


class IntegerField(TypedField):
    """
    Specialized subclass of TypedField(int) as a convienence
    """

    def __init__(self):
        super(IntegerField, self).__init__(int)


class DictField(TypedField):
    """
    Specialized subclass of TypedField(dict) as a convienence
    """

    def __init__(self):
        super(DictField, self).__init__(dict)

    @classmethod
    def to_json(cls, self):
        """
        Serialize to json
        """

        if not self:
            return None

        _dict = copy.deepcopy(self)

        for key, value in _dict.iteritems():
            if isinstance(value, datetime):
                _dict[key] = value.isoformat()

        return json.dumps(_dict)

    @classmethod
    def from_json(cls, value):
        """
        Descerialize from json
        """

        if not value:
            return None

        _dict = json.loads(value)

        for key, value in _dict.iteritems():
            if isinstance(value, basestring):
                # This could be a datetime posing as a ISO8601 formatted string
                # we so have to apply some heuristics here
                # to see if we want to even attempt
                if value.count('-') == 2 and value.count(':') == 2 and value.count('T') == 1:
                    # this is likely a ISO8601 serialized string, so let's try to parse
                    try:
                        _dict[key] = dateutil.parser.parse(value)
                    except ValueError:
                        # oops, I guess our heuristic was a bit off
                        # no harm, but just wasted CPU cycles
                        pass

        return _dict


class DateTimeField(TypedField):
    """
    Specialized subclass of TypedField(datetime) as a convienence
    """

    def __init__(self):
        super(DateTimeField, self).__init__(datetime)


class EnumField(StringField):
    """
    Specialized subclass of TypedField() which is basically an StringTypedField,
    but constrains what values can be set on it
    """

    def __init__(self, allowed_values=None):
        """
        Initializer with constrained values
        """

        self._allowed_values = allowed_values
        super(EnumField, self).__init__()

    def __set__(self, instance, value):
        """
        Descriptor setter. Be sure to enforce type on setting. But None is allowed.
        """

        if self._allowed_values:
            if value not in self._allowed_values:
                msg = (
                    "Attempting to set to '{value}'. Allowed values are: '{allowed}'."
                ).format(value=value, allowed=str(self._allowed_values))
                raise ValueError(msg)

        super(EnumField, self).__set__(instance, value)


class RelatedObjectField(TypedField):
    """
    This field is a related object that is joined to the containing object,
    for example a foreign key. The related object must be of type BaseDataObject
    """

    def __init__(self, related_type):
        """
        Initializer for related object which must be a subclass of
        BaseDataObject
        """

        if not issubclass(related_type, BaseDataObject):
            msg = (
                "Creating a related field of type '{name}' which is not a "
                "subclass of BaseDataObject."
            ).format(name=related_type)

            raise TypeError(msg)

        super(RelatedObjectField, self).__init__(related_type)
