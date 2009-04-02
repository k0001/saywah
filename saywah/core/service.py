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
import dbus.service
import dbus.mainloop.glib
import gobject

from .providers import ProviderDBusWrapper

__all__ = ('SaywahService', 'SaywahServiceDBusWrapper', 'start_dbus_service')


class SaywahService(object):
    def __init__(self):
        self.providers = {}


class SaywahServiceDBusWrapper(dbus.service.Object):
    def __init__(self, saywah_service, *args, **kwargs):
        super(SaywahServiceDBusWrapper, self).__init__(*args, **kwargs)
        self._saywah_service = saywah_service
        self._register_providers()

    def _register_providers(self):
        self._wrapped_providers = {}
        for k,v in self._saywah_service.providers.items():
            object_path = u'/providers/%s' % k
            wp = ProviderDBusWrapper(v, conn=self._connection,
                                     object_path=object_path,
                                     bus_name='org.saywah.Saywah')
            self._wrapped_providers[object_path] = wp


    # DBus 'org.saywah.Saywah' interface methods
    @dbus.service.method(dbus_interface='org.saywah.Saywah',
                         in_signature='', out_signature='as')
    def get_providers(self):
        return self._wrapped_providers.keys()


def start_dbus_service(saywah_service):
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName('org.saywah.Saywah', session_bus)
    dbus_saywah_service = SaywahServiceDBusWrapper(saywah_service,
                                                   conn=session_bus,
                                                   object_path='/',
                                                   bus_name='org.saywah.Saywah')
    mainloop = gobject.MainLoop()
    return mainloop.run()
