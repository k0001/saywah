# -*- coding: utf8 -*-

# This file is part of Saywah.
# Copyright (C) 2009 Renzo Carbonara <gnuk0001@gmail.com>
#
# Saywah is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Saywah is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Saywah.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides tools to ease serialization of objects.
"""

import datetime
import re

__all__ = ('Field', 'Model', 'UnicodeField', 'IntegerField', 'FloatField', 'DatetimeField')


class Field(object):
    def __init__(self, type, default=None):
        super(Field, self).__init__()
        self._type = type
        if default is not None and not isinstance(default, self._type):
            raise TypeError('%s instance expected, got %s' % (self._type, repr(default)))
        self._default = default

    def __get__(self, obj, type):
        return obj._field_values[self._attr_name_for(obj)]

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, self._type):
            raise TypeError('%s instance expected, got %s' % (self._type, repr(value)))
        obj._field_values[self._attr_name_for(obj)] = value

    def _attr_name_for(self, obj):
        for k,v in obj.__class__.get_fields().items():
            if v is self:
                return k

    def _values_for(self, obj):
        return obj._field_values

    def prepare(self, obj):
        if not hasattr(obj, '_field_values'):
            obj._field_values = {}
        obj._field_values[self._attr_name_for(obj)] = self._default

    def to_raw(self, value):
        """Encode the given value supported by this Field as an unicode string"""
        raise NotImplementedError()

    def from_raw(self, u):
        """Decode the given unicode string as a value supported by this Field"""
        raise NotImplementedError()


class Model(object):
    def __init__(self, **kwargs):
        super(Model, self).__init__()
        # Field default values

        for k,v in self.__class__.get_fields().items():
            v.prepare(self)
            if k in kwargs:
                setattr(self, k, kwargs[k])

    @classmethod
    def get_fields(cls):
        out = {}
        for c in reversed([c for c in cls.mro() if issubclass(c, Model)]):
            for k,v in c.__dict__.items():
                if isinstance(v, Field):
                    out[k] = v
        return out

    @classmethod
    def get_field_names(cls):
        return tuple(cls.get_fields().keys())


    def to_dict(self, raw=False):
        ud = {}
        for k,v in self.__class__.get_fields().items():
            if raw:
                ud[k] = v.to_raw(getattr(self, k))
            else:
                ud[k] = getattr(self, k)
        return ud

    @classmethod
    def from_dict(cls, ud, raw=False):
        obj = cls()
        for k,v in cls.get_fields().items():
            if k in ud:
                if raw:
                    setattr(obj, k, v.from_raw(ud[k]))
                else:
                    setattr(obj, k, ud[k])
        return obj

    def __hash__(self):
        return hash(tuple(self.to_dict(raw=True).items()))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.to_dict(raw=True) == other.to_dict(raw=True)


# some basic fields

class UnicodeField(Field):
    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.pop('type', unicode)
        super(UnicodeField, self).__init__(**kwargs)

    def to_raw(self, v):
        if v is not None:
            return v

    def from_raw(self, v):
        if v is not None:
            return v


class IntegerField(Field):
    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.pop('type', (int, long))
        super(IntegerField, self).__init__(**kwargs)

    def to_raw(self, v):
        if v is not None:
            return v

    def from_raw(self, v):
        if v is not None:
            return int(v)


class FloatField(Field):
    def __init__(self, **kwargs):
        kwargs['type'] = kwargs.pop('type', float)
        super(FloatField, self).__init__(**kwargs)

    def to_raw(self, v):
        if v is not None:
            return v

    def from_raw(self, v):
        if v is not None:
            return float(v)


class DatetimeField(Field):
    _utc_iso8601_fmt = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, utc_offset=None, **kwargs):
        if utc_offset:
            if not isinstance(utc_offset, datetime.timedelta):
                raise TypeError('utc_offset: %s instance expected, got %s' % (
                                     datetime.timedelta, repr(utc_offset)))
            self._utc_offset = utc_offset
        else:
            self._utc_offset = datetime.timedelta(0)
        kwargs['type'] = kwargs.pop('type', datetime.datetime)
        super(DatetimeField, self).__init__(**kwargs)

    def __get__(self, obj, type):
        value = super(DatetimeField, self).__get__(obj, type)
        if value is not None:
            return value + self._utc_offset

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, datetime.datetime):
                raise TypeError('%s instance expected, got %s' % (datetime.datetime, repr(value)))
            value -= self._utc_offset
        super(DatetimeField, self).__set__(obj, value)

    def to_raw(self, v):
        if v is not None:
            utc_dt = v - self._utc_offset
            return utc_dt.strftime(self._utc_iso8601_fmt)

    def from_raw(self, v):
        if v is not None:
            utc_dt = datetime.datetime.strptime(v, self._utc_iso8601_fmt)
            return utc_dt + self._utc_offset
