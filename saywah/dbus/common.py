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


import dbus


__all__ = 'DBusPropertiesExposer',


class DBusPropertiesExposer(object):
    """
    Reusable org.freedesktop.DBus.Properties Implementation Mixin.

    Usage:
        Add your python ``property`` objects to an instance attribute dict named ``_dbus_properties``.
    """
    _dbus_properties = {}

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties', in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        try:
            return self._dbus_properties[property_name].fget(self)
        except KeyError, e:
            raise AttributeError(property_name)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties', in_signature='ssv', out_signature='')
    def Set(self, interface_name, property_name, value):
        try:
            prop = self._dbus_properties[property_name].fset(self, value)
        except (KeyError, TypeError), e:
            raise AttributeError(property_name)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties', in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        return dict((k, v.fget(self)) for (k,v) in self._dbus_properties.items())

