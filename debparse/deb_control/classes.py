# coding: utf-8
from __future__ import unicode_literals

import collections

ANY = object()


class Stub(object):
    # valid attributes for this stub
    # can by `ANY` special value or iterable of strings.
    valid_attribures = ANY

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            if self.valid_attribures == ANY or key in self.valid_attribures:
                kwargs.pop(key)
                setattr(self, key, value)
        super(Stub, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<%s: %s>' % (
            self.__class__.__name__,
            self._repr_data(),
        )

    def _repr_data(self):
        return str(self.__dict__)


class ControlData(Stub):
    def _repr_data(self):
        return str([
            package.id
            for package in self.packages
            if package.id is not None
        ])

    @property
    def source_package(self):
        for package in self.packages:
            if package.type == 'source':
                return package

    @property
    def binary_packages(self):
        return collections.OrderedDict([
            (package.id, package)
            for package in self.packages
            if package.type == 'binary'
        ])


class Package(Stub, collections.OrderedDict):
    """
    Case-insensitive read-only ordered mapping of fields in paragraph,
    representing package.
    """
    valid_attribures = (
        '_raw',
    )

    def __getitem__(self, item):
        if not isinstance(item, basestring):
            raise TypeError(item)
        for key in self:
            if item.lower() == key.lower():
                return super(Package, self).__getitem__(key)
        raise KeyError(item)

    def _repr_data(self):
        return str(self.keys())

    @property
    def type(self):
        if 'Source' in self:
            return 'source'
        elif 'Package' in self:
            return 'binary'
        return 'unknown'

    @property
    def id(self):
        if self.type == 'source':
            return self['Source'].text
        if self.type == 'binary':
            return self['Package'].text

# TODO:
#   * Every field value must be FieldValue inheritor, it
#   should have type, format or is_list at least. So we need to make
#   ListField. Also _raw must be in each fieldvalue.
#   * I guess not every fieldvalue must have meta, but only the first one
#   or maybe meta is not useful at all.
#   * canonical name could be in key object maybe
#   * all i can is enum of values need at some point.
#   if we want to make validation or something, but maybe we don't want
#   it by design


class FieldMeta(Stub):
    pass


class FieldValue(Stub):
    def _repr_data(self):
        return self._raw


class SimpleField(FieldValue):
    pass


class ContactField(FieldValue):
    pass


class DependencySimple(FieldValue):
    type = 'simple'


class DependencyAlternative(DependencySimple):
    type = 'alternative'


class DependencyPlaceholder(DependencySimple):
    type = 'placeholder'


class Restriction(Stub):
    pass
