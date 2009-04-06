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


import datetime
import logging

import dbus
import dbus.mainloop.glib
import dbus.service

from saywah.core.service import saywah_service


__all__ = (u'DBUS_NAME', u'DBUS_OBJECT_PATHS', u'DBUS_INTERFACES',
           u'AccountDBus', u'ProviderDBus', u'SaywahDBus',
           u'saywah_dbus_services')


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

log = logging.getLogger(__name__)

DBUS_BUS_NAME =             u'org.saywah.Saywah'
DBUS_OBJECT_PATHS = {
    u'saywah':              u'/org/saywah/Saywah',
    u'provider':            u'/org/saywah/Saywah/providers/%(provider)s',
    u'provider_account':    u'/org/saywah/Saywah/providers/%(provider)s/accounts/%(username)s' }
DBUS_INTERFACES = {
    u'saywah':              u'org.saywah.Saywah',
    u'provider':            u'org.saywah.Provider',
    u'account':             u'org.saywah.Account' }


class ProviderDBus(dbus.service.Object):
    register = {}
    _started = False

    def __init__(self, provider, *args, **kwargs):
        self._provider = provider
        super(ProviderDBus, self).__init__(*args, **kwargs)

    @classmethod
    def start(cls, connection):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        cls.register_providers(connection, ())
        log.debug(u"Starting %s services" % cls.__name__)
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"Stoping %s services" % cls.__name__)
            cls.unregister_providers()
            cls._started = False

    @classmethod
    def register_providers(cls, connection, providers):
        for p in providers:
            object_path = DBUS_OBJECT_PATHS['provider'] % { u'provider': p.slug }
            pd = ProviderDBus(p, conn=connection, object_path=object_path, bus_name=DBUS_BUS_NAME)
            cls.register[object_path] = pd

    @classmethod
    def unregister_providers(cls):
        cls.register.clear()


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'provider'],
                         in_signature='', out_signature='as')
    def get_features(self):
        return self._provider.features


    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'provider'],
                         in_signature='', out_signature='as')
    def get_accounts(self):
        return AccountDBus.register.keys()


class AccountDBus(dbus.service.Object):
    register = {}
    _started = False

    def __init__(self, account, *args, **kwargs):
        self._account = account
        super(AccountDBus, self).__init__(*args, **kwargs)

    @classmethod
    def start(cls, connection):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        cls.register_accounts(connection, ())
        log.debug(u"Starting %s services" % cls.__name__)
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"stoping %s services" % cls.__name__)
            cls.unregister_accounts()
            cls._started = False

    @classmethod
    def register_accounts(cls, connection, accounts):
        for a in accounts:
            object_path = DBUS_OBJECT_PATHS['account'] % { u'provider': a.provider_slug,
                                                           u'username': a.slug }
            ad = AccountDBus(a, conn=connection, object_path=object_path, bus_name=DBUS_BUS_NAME)
            cls.register[object_path] = ad

    @classmethod
    def unregister_accounts(cls):
        cls.register.clear()


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'account'],
                         in_signature='', out_signature='a{ss}')
    def get_details(self):
        return dict((k, unicode(v)) for (k,v) in self._account.to_raw_dict().items() if k != u'password')


    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'account'],
                         in_signature='s', out_signature='')
    def send_message(self, message):
        self._account.provider.send_message(self._account, message)


class SaywahDBus(dbus.service.Object):
    _instance = None
    _started = False

    def __init__(self, saywah_service, *args, **kwargs):
        self._saywah_service = saywah_service
        super(SaywahDBus, self).__init__(*args, **kwargs)

    @classmethod
    def start(cls, connection):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        log.debug(u"Starting %s services" % cls.__name__)
        cls._instance = SaywahDBus(saywah_service,
                                    conn=connection,
                                    object_path=DBUS_OBJECT_PATHS['saywah'],
                                    bus_name=DBUS_BUS_NAME)
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"Stoping %s services" % cls.__name__)
            cls._instance = None
            cls._started = False


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'saywah'],
                         in_signature='', out_signature='as')
    def get_providers(self):
        return ProviderDBus.register.keys()

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'saywah'],
                         in_signature='', out_signature='as')
    def get_accounts(self):
        return AccountsDBus.register.keys()


class saywah_dbus_services(object):
    _started = False

    @classmethod
    def start(cls):
        if cls._started:
            raise RuntimeError(u'DBus service already started')
        log.info(u"Starting all Saywah services")
        conn = dbus.SessionBus()
        try:
            SaywahDBus.start(conn)
            ProviderDBus.start(conn)
            AccountDBus.start(conn)
        except Exception, e:
            log.error(u"Starting all Saywah services failed")
            cls.stop()
            raise
        else:
            cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"Stoping all Saywah services")
            SaywahDBus.stop(conn)
            ProviderDBus.stop(conn)
            AccountDBus.stop(conn)
            cls._started = False

start = saywah_dbus_services.start
stop = saywah_dbus_services.stop

