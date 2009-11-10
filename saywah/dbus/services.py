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
import gobject
import louie

from saywah.core.accounts import Account
from saywah.core.providers import Provider
from saywah.core.service import saywah_service
from saywah.core.conf import store_current_accounts


__all__ = (u'DBUS_NAME', u'DBUS_OBJECT_PATHS', u'DBUS_INTERFACES',
           u'AccountDBus', u'ProviderDBus', u'SaywahDBus',
           u'saywah_dbus_services')

log = logging.getLogger(__name__)

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

DBUS_CONNECTION = dbus.SessionBus()
DBUS_BUS_NAME =             u'org.saywah.Saywah'
DBUS_OBJECT_PATHS = {
    u'saywah':              u'/org/saywah/Saywah',
    u'provider':            u'/org/saywah/Saywah/providers/%(provider)s',
    u'provider_account':    u'/org/saywah/Saywah/providers/%(provider)s/accounts/%(username)s' }
DBUS_INTERFACES = {
    u'saywah':              u'org.saywah.Saywah',
    u'provider':            u'org.saywah.Provider',
    u'account':             u'org.saywah.Account' }


class DBusPropertiesExposer(object):
    """
    Reusable org.freedesktop.DBus.Properties Implementation Mixin.

    Usage:
        Add your python ``property`` objects to an instance attribute dict named ``_dbus_properties``.
    """
    _dbus_properties = {}

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='ss', out_signature='v')
    def Get(self, interface_name, property_name):
        try:
            return self._dbus_properties[property_name].fget(self)
        except KeyError, e:
            raise AttributeError(property_name)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='ssv', out_signature='')
    def Set(self, interface_name, property_name, value):
        try:
            prop = self._dbus_properties[property_name].fset(self, value)
        except (KeyError, TypeError), e:
            raise AttributeError(property_name)

    @dbus.service.method(dbus_interface='org.freedesktop.DBus.Properties',
                         in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface_name):
        return dict((k, v.fget(self)) for (k,v) in self._dbus_properties.items())


class ProviderDBus(dbus.service.Object, DBusPropertiesExposer):
    registry = {}
    _started = False

    def __init__(self, provider, *args, **kwargs):
        self._provider = provider
        super(ProviderDBus, self).__init__(*args, **kwargs)

    @classmethod
    def start(cls):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        cls.register_providers(Provider.registry.values())
        log.debug(u"Starting %s services" % cls.__name__)
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"Stoping %s services" % cls.__name__)
            cls.unregister_providers()
            cls._started = False

    @classmethod
    def register_providers(cls, providers):
        for p in providers:
            object_path = DBUS_OBJECT_PATHS['provider'] % { u'provider': p.slug }
            pd = ProviderDBus(p, conn=DBUS_CONNECTION, object_path=object_path, bus_name=DBUS_BUS_NAME)
            cls.registry[object_path] = pd

    @classmethod
    def unregister_providers(cls):
        cls.registry.clear()


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'provider'],
                         in_signature='', out_signature='as')
    def get_features(self):
        return self._provider.features


    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'provider'],
                         in_signature='', out_signature='as')
    def get_accounts(self):
        return AccountDBus.registry.keys()


    # DBusPropertiesExposer properties
    _dbus_properties = {
        u'slug': property(lambda self: self._provider.slug),
        u'name': property(lambda self: self._provider.name)
    }


class AccountDBus(dbus.service.Object, DBusPropertiesExposer):
    registry = {}
    _started = False

    def __init__(self, account, *args, **kwargs):
        self._account = account
        super(AccountDBus, self).__init__(*args, **kwargs)

    @classmethod
    def start(cls):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        log.debug(u"Starting %s services" % cls.__name__)
        cls.register_accounts(list(Account.objects))
        louie.dispatcher.connect(receiver=cls._on_account_post_add_handler,
                                 signal=Account.objects.post_add)
        louie.dispatcher.connect(receiver=cls._on_account_post_remove_handler,
                                 signal=Account.objects.post_remove)
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"stoping %s services" % cls.__name__)
            cls.unregister_accounts()
            louie.dispatcher.disconnect(receiver=cls._on_account_post_add_handler,
                                        signal=Account.objects.post_add)
            louie.dispatcher.disconnect(receiver=cls._on_account_post_remove_handler,
                                        signal=Account.objects.post_remove)
            cls._started = False

    @classmethod
    def register_accounts(cls, accounts):
        for a in accounts:
            object_path = DBUS_OBJECT_PATHS['provider_account'] % { u'provider': a.provider_slug,
                                                                    u'username': a.slug }
            if not object_path in cls.registry:
                ad = AccountDBus(a, conn=DBUS_CONNECTION, object_path=object_path, bus_name=DBUS_BUS_NAME)
                cls.registry[object_path] = ad

    @classmethod
    def unregister_accounts(cls):
        cls.registry.clear()

    @classmethod
    def unregister_account(cls, account):
        for k,v in cls.register.items():
            if v._account == account:
                del cls.register[k]
                return
        else:
            raise KeyError(account)

    @classmethod
    def _on_account_post_add_handler(cls, named=None):
        cls.register_accounts([named['item']])

    @classmethod
    def _on_account_post_remove_handler(cls, named=None):
        cls.unregister_accounts([named['item']])


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'account'],
                         in_signature='', out_signature='a{ss}')
    def get_details(self):
        return dict((k, unicode(v)) for (k,v) in self._account.to_dict(raw=True).items() if k != u'password')


    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'account'],
                         in_signature='s', out_signature='')
    def send_message(self, message):
        self._account.provider.send_message(self._account, message)


    # DBusPropertiesExposer properties
    _dbus_properties = {
        u'slug': property(lambda self: self._account.slug),
        u'username': property(lambda self: self._account.username),
        u'password': property(lambda self: self._account.password),
        u'provider_slug': property(lambda self: self._account.provider_slug),
        u'last_received_message_id': property(lambda self: self._account.last_received_message_id or u""),
        u'last_updated': property(lambda self: self._account.to_dict(raw=True)['last_updated'] or u"")
    }


class SaywahDBus(dbus.service.Object):
    _instance = None
    _started = False

    def __init__(self, saywah_service, *args, **kwargs):
        self._saywah_service = saywah_service
        super(SaywahDBus, self).__init__(*args, **kwargs)

    @classmethod
    def start(cls):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        log.debug(u"Starting %s services" % cls.__name__)
        cls._instance = SaywahDBus(saywah_service,
                                   conn=DBUS_CONNECTION,
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
        return ProviderDBus.registry.keys()

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'saywah'],
                         in_signature='', out_signature='as')
    def get_accounts(self):
        return AccountDBus.registry.keys()

    @dbus.service.method(dbus_interface=DBUS_INTERFACES[u'saywah'],
                         in_signature='ss', out_signature='')
    def add_account(self, provider_slug, account_username):
        for a in Account.objects:
            if a.provider_slug == provider_slug and a.username == account_username:
                raise ValueError(u"Account username '%s' for service provider '%s' already exists" % (
                                        account_username, provider_slug))
        a = Account(provider_slug=provider_slug, username=account_username)
        Account.objects.add(a)
        store_current_accounts()
        log.info(u"New '%s' account '%s' added" % (provider_slug, account_username))


class saywah_dbus_services(object):
    _started = False
    _bus_name = None

    @classmethod
    def start(cls):
        if cls._started:
            raise RuntimeError(u'DBus service already started')
        log.info(u"Starting all Saywah services")
        cls._bus_name = dbus.service.BusName(DBUS_BUS_NAME, DBUS_CONNECTION)
        log.info("DBus services using bus name: %s" % DBUS_BUS_NAME)
        try:
            SaywahDBus.start()
            ProviderDBus.start()
            AccountDBus.start()
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
            SaywahDBus.stop()
            ProviderDBus.stop()
            AccountDBus.stop()
            cls._bus_name = None
            cls._started = False

start = saywah_dbus_services.start
stop = saywah_dbus_services.stop

def run():
    mainloop = gobject.MainLoop()
    return mainloop.run()

