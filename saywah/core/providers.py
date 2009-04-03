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

from .accounts import Account

__all__ = ('Provider', 'ProviderDBusWrapper')


class Provider(object):
    @property
    def features(self):
        meth_names = ('send_message',)
        return tuple(n for n in meth_names if getattr(getattr(self, n), '_disabled'))

    # The following methods are to be overriden by provider implementations

    def send_message(self, account, message):
        raise NotImplementedError
    send_message._disabled = True


class ProviderDBusWrapper(dbus.service.Object):
    def __init__(self, provider, *args, **kwargs):
        self._provider = provider
        super(ProviderDBusWrapper, self).__init__(*args, **kwargs)

    # DBus 'org.saywah.Provider' interface methods
    @dbus.service.method(dbus_interface='org.saywah.Provider',
                         in_signature='', out_signature='as')
    def get_features(self):
        return self._provider.features

    @dbus.service.method(dbus_interface='org.saywah.Provider',
                         in_signature='sss', out_signature='')
    def send_message(self, service, username, message):
        from .service import saywah_service
        account = saywah_service.accounts.get_by_service_and_username(service, username)
        self._provider.send_message(account, message)
