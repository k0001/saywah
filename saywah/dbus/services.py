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


import logging
import threading
import time

import dbus
import dbus.mainloop.glib
import dbus.service
import gobject

from saywah.dbus.common import DBusPropertiesExposer


__all__ = ('DBUS_NAME', 'DBUS_OBJECT_PATHS', 'DBUS_INTERFACES',
           'ProvidersDBus', 'ProviderDBus', 'AccountsDBus',
           'AccountDBus',  'SaywahDBus', 'saywah_dbus_services')

log = logging.getLogger(__name__)

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

DBUS_CONNECTION = dbus.SessionBus()
DBUS_BUS_NAME =            'org.saywah.Saywah'
DBUS_OBJECT_PATHS = {
    'saywah':              '/org/saywah/Saywah',
    'providers':           '/org/saywah/Saywah/providers',
    'provider':            '/org/saywah/Saywah/providers/%(provider_slug)s',
    'accounts':            '/org/saywah/Saywah/accounts',
    'account':             '/org/saywah/Saywah/accounts/%(account_uuid)s' }
DBUS_INTERFACES = {
    'saywah':              'org.saywah.Saywah',
    'providers':           'org.saywah.Providers',
    'provider':            'org.saywah.Provider',
    'accounts':            'org.saywah.Accounts',
    'account':             'org.saywah.Account' }


class AccountMessagesFetcherThread(threading.Thread):
    def __init__(self, account, provider, callback):
        self._account = account
        self._provider = provider
        self._callback = callback
        self._seen_messages = set()
        super(AccountMessagesFetcherThread, self).__init__()

    def run(self):
        while True:
            for m in self._provider.get_new_messages(self._account):
                if not m.uuid in self._seen_messages:
                    self._seen_messages.add(m.uuid)
                    self._callback(m)
            log.debug(u"Waiting %d seconds before next Account %s messages update" \
                        % (self._provider.suggested_wait_time, self._account))
            time.sleep(self._provider.suggested_wait_time)

account_messages_fetcher_threads = {}


class ProvidersDBus(dbus.service.Object):
    """Providers collection DBus Object"""

    _instance = None
    _started = False

    @classmethod
    def start(cls, saywah_service):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        object_path = DBUS_OBJECT_PATHS['providers']
        log.debug(u"Starting %s at %s" % (cls.__name__, object_path))
        cls._instance = ProvidersDBus(saywah_service, object_path=object_path,
                                      conn=DBUS_CONNECTION, bus_name=DBUS_BUS_NAME)
        cls._instance._register_providers_from_manager()
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"Stoping %s services" % cls.__name__)
            cls._started = False
            cls._instance.unregister_all_providers()
            cls._instance = None

    def __init__(self, saywah_service, *args, **kwargs):
        self._saywah_service = saywah_service
        self._providerdbus_registry = {}
        super(ProvidersDBus, self).__init__(*args, **kwargs)

    def register_provider(self, provider):
        """
        Registers the given ``provider`` as a DBus Object identified by ``provider.slug``

        Returns the assigned DBus Object Path
        """
        object_path = DBUS_OBJECT_PATHS['provider'] % {'provider_slug': provider.slug}
        if object_path in self._providerdbus_registry:
            raise ValueError(u'%s already registered' % provider.slug)
        log.debug(u"Starting ProviderDBus at %s" % object_path)
        pd = ProviderDBus(self._saywah_service, provider,
                          object_path=object_path, conn=DBUS_CONNECTION, bus_name=DBUS_BUS_NAME)
        self._providerdbus_registry[object_path] = pd
        return object_path

    def unregister_provider(self, provider_slug):
        """Unregisters the previously registered Provider DBus Object identified by ``provider_slug``"""
        object_path = DBUS_OBJECT_PATHS['provider'] % {'provider_slug': provider_slug}
        del self._providerdbus_registry[object_path]

    def unregister_all_providers(cls):
        """Unregisters all Provider DBus Objects previously registered"""
        self._providerdbus_registry.clear()

    def _register_providers_from_manager(self):
        """Registers the Provider objects available in ``self._saywah_service`` using ``self.register_provider()``"""
        for provider in self._saywah_service.provider_manager.providers.values():
            self.register_provider(provider)


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['providers'], in_signature='', out_signature='as')
    def GetProviders(self):
        return self._providerdbus_registry.keys()

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['providers'], in_signature='', out_signature='')
    def ReloadProviders(self):
        self._saywah_service.reload_providers()


class ProviderDBus(dbus.service.Object, DBusPropertiesExposer):
    """Single Provider DBus Object"""

    def __init__(self, saywah_service, provider, *args, **kwargs):
        self._saywah_service = saywah_service
        self._provider = provider
        super(ProviderDBus, self).__init__(*args, **kwargs)

    # DBusPropertiesExposer properties
    _dbus_properties = {
        'slug': property(lambda self: self._provider.slug),
        'name': property(lambda self: self._provider.name)
    }


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['provider'], in_signature='', out_signature='as')
    def GetFeatures(self):
        return self._provider.features

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['provider'], in_signature='', out_signature='as')
    def GetAccounts(self):
        for account in self._saywah_service.account_manager.accounts.values():
            if account.provider_slug == self._provider.slug:
                yield DBUS_OBJECT_PATHS['account'] % {'account_uuid': account.uuid.replace('-', '_')}

class AccountsDBus(dbus.service.Object):
    """Accounts collection DBus Object"""

    _instance = None
    _started = False

    @classmethod
    def start(cls, saywah_service):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        object_path = DBUS_OBJECT_PATHS['accounts']
        log.debug(u"Starting %s at %s" % (cls.__name__, object_path))
        cls._instance = AccountsDBus(saywah_service, object_path=object_path,
                                     conn=DBUS_CONNECTION, bus_name=DBUS_BUS_NAME)
        cls._instance._register_accounts_from_manager()
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"stoping %s services" % cls.__name__)
            cls._started = False
            cls._instance.unregister_all_accounts()
            cls._instance = Nonw

    def __init__(self, saywah_service, *args, **kwargs):
        self._saywah_service = saywah_service
        self._accountdbus_registry = {}
        super(AccountsDBus, self).__init__(*args, **kwargs)

    def register_account(self, account):
        """
        Registers the given ``account`` as a DBus Object identified by ``account.uuid``

        Returns the assigned DBus Object Path
        """
        object_path = DBUS_OBJECT_PATHS['account'] % {'account_uuid': account.uuid.replace('-', '_')}
        if object_path in self._accountdbus_registry:
            raise ValueError(u'%s already registered' % account.uuid)
        log.debug(u"Starting AccountDBus at %s" % object_path)
        ad = AccountDBus(self._saywah_service,  account,
                         object_path=object_path, conn=DBUS_CONNECTION, bus_name=DBUS_BUS_NAME)
        self._accountdbus_registry[object_path] = ad
        return object_path

    def unregister_account(self, account_uuid):
        """Unregisters the previously registered Account DBus Object identified by ``account_uuid``"""
        object_path = DBUS_OBJECT_PATHS['account'] % {'account_uuid': account.uuid.replace('-', '_')}
        del self._accountdbus_registry[object_path]

    @classmethod
    def unregister_all_accounts(cls):
        """Unregisters all Account DBus Objects previously registered"""
        self._accountdbus_registry.clear()

    def _register_accounts_from_manager(self):
        """Registers the Account objects available in ``self._saywah_service`` using ``self.register_account()``"""
        for account in self._saywah_service.account_manager.accounts.values():
            self.register_account(account)


    # DBus exposed methods


    @dbus.service.method(dbus_interface=DBUS_INTERFACES['accounts'], in_signature='', out_signature='as')
    def GetAccounts(self):
        return self._accountdbus_registry.keys()

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['accounts'], in_signature='ss', out_signature='s')
    def AddAccount(self, provider_slug, account_username):
        for account in self._saywah_service.account_manager.accounts.values():
            if account.provider_slug == provider_slug and account.username == account_username:
                object_path = DBUS_OBJECT_PATHS['account'] % {'account_uuid': account.uuid.replace('-', '_')}
                raise ValueError(u"Account username '%s' for service provider '%s' already exists at '%s'" % (
                                        account_username, provider_slug, object_path))
        account = self._saywah_service.account_manager.create(provider_slug=provider_slug, username=account_username)
        self._saywah_service.account_manager.register(account)
        object_path = self.register_account(account)
        log.info(u"New '%s' account '%s' added at '%s'" % (provider_slug, account_username, object_path))
        return object_path

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['accounts'], in_signature='', out_signature='')
    def ReloadAccounts(self):
        self._saywah_service.reload_accounts()

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['accounts'], in_signature='', out_signature='')
    def StoreAccounts(self):
        self._saywah_service.store_accounts()


class AccountDBus(dbus.service.Object, DBusPropertiesExposer):
    """Single Provider DBus Object"""

    def __init__(self, saywah_service, account, *args, **kwargs):
        self._saywah_service = saywah_service
        self._account = account
        self._last_messages = []
        super(AccountDBus, self).__init__(*args, **kwargs)

    # DBusPropertiesExposer properties
    _dbus_properties = {
        'uuid': property(lambda self: self._account.uuid),
        'username': property(lambda self: self._account.username),
        'password': property(lambda self: self._account.password,
                             lambda self, v: setattr(self._account, 'password', v)),
        'provider_slug': property(lambda self: self._account.provider_slug),
        'last_received_message_id': property(lambda self: self._account.last_received_message_id or u""),
        'last_updated': property(lambda self: self._account.to_dict(raw=True)['last_updated'] or u"")
    }

    def _new_message_fetched_callback(self, message):
        d = message.to_dict(raw=True)
        d['uuid'] = message.uuid
        self.MessageArrived(d)


    # DBus exposed methods

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['account'], in_signature='s', out_signature='')
    def SendMessage(self, message):
        provider = self._saywah_service.provider_manager.providers[self._account.provider_slug]
        provider.send_message(self._account, message)

    @dbus.service.method(dbus_interface=DBUS_INTERFACES['account'], in_signature='', out_signature='b')
    def EnableMessageFetching(self, enable):
        provider = self._saywah_service.provider_manager.providers[self._account.provider_slug]
        if enable:
            if not self._account.uuid in account_messages_fetcher_threads:
                log.info(u"Enabled message fetching for Account: %s" % self._account)
                thread = AccountMessagesFetcherThread(self._account, provider, self._new_message_fetched_callback)
                account_messages_fetcher_threads[self._account.uuid] = thread
                thread.start()
        else:
            if self._account.uuid in account_messages_fetcher_threads:
                log.info(u"Disabled message fetching for Account: %s" % self._account)
                account_messages_fetcher_threads[self._account.uuid].stop()
                del account_messages_fetcher_threads[self._account.uuid]

    @dbus.service.signal(dbus_interface=DBUS_INTERFACES['account'], signature='a{sv}')
    def MessageArrived(self, message):
        self._last_messages.append(message)
        if len(self._last_messages) == 20:
            self._last_messages.pop(0)


class SaywahDBus(dbus.service.Object):
    """Saywah root DBus Object"""

    _instance = None
    _started = False

    def __init__(self, saywah_service, *args, **kwargs):
        self._saywah_service = saywah_service
        super(SaywahDBus, self).__init__(*args, **kwargs)

    @classmethod
    def start(cls, saywah_service):
        if cls._started:
            raise RuntimeError(u'%s services already started' % cls.__name__)
        object_path = DBUS_OBJECT_PATHS['saywah']
        log.debug(u"Starting %s at %s" % (cls.__name__, object_path))
        cls._instance = SaywahDBus(saywah_service, object_path=object_path,
                                   conn=DBUS_CONNECTION, bus_name=DBUS_BUS_NAME)
        cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"Stoping %s services" % cls.__name__)
            cls._instance = None
            cls._saywah_service = None
            cls._started = False


class saywah_dbus_services(object):
    """Saywah DBus daemon entry point"""

    _started = False
    _bus_name = None

    @classmethod
    def start(cls, saywah_service):
        if cls._started:
            raise RuntimeError(u'DBus service already started')
        log.info(u"Starting all Saywah services")
        cls._bus_name = dbus.service.BusName(DBUS_BUS_NAME, DBUS_CONNECTION)
        log.info("DBus services using bus name: %s" % DBUS_BUS_NAME)
        try:
            SaywahDBus.start(saywah_service)
            ProvidersDBus.start(saywah_service)
            AccountsDBus.start(saywah_service)
        except Exception, e:
            log.error(u"Starting all Saywah services failed")
            cls.stop()
            raise
        else:
            log.info(u"Started all Saywah services")
            cls._started = True

    @classmethod
    def stop(cls):
        if cls._started:
            log.debug(u"Stoping all Saywah services")
            SaywahDBus.stop()
            ProvidersDBus.stop()
            AccountsDBus.stop()
            cls._bus_name = None
            cls._started = False

    @classmethod
    def run(cls):
        gobject.threads_init()
        mainloop = gobject.MainLoop()
        return mainloop.run()

