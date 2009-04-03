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
import os

try:
    import json
except ImportError:
    import simplejson as json

import dbus
import dbus.service
import dbus.mainloop.glib
import gobject

from .providers import ProviderDBusWrapper
from .accounts import Account, AccountsRegistry, AccountDBusWrapper


__all__ = ('SaywahService', 'SaywahServiceDBusWrapper', 'start_dbus_saywah_service',
           'saywah_service')

log = logging.getLogger(__name__)

CONFIG_PATH = os.path.expanduser("~/.config/saywah")


class SaywahService(object):
    def __init__(self):
        self.providers = {}
        self.accounts = AccountsRegistry()
        self._ready = False

    def setup(self):
        if self._ready:
            raise RuntimeError(u"Saywah service already set up")
        log.info(u"Setting up SaywahService")
        if not os.path.isdir(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)
        self._setup__load_providers()
        self._setup__load_accounts()
        self._ready = True

    def sync(self):
        log.info(u"Syncronizing SaywahService")
        if not self.ready:
            raise RuntimeError(u"Saywah service not set up")
        self._sync__save_accounts()

    def _setup__load_providers(self):
        # XXX: some day this will be un-hardcoded =)
        from ..providers.twitter import TwitterProvider
        self.providers[TwitterProvider.slug] = TwitterProvider()

    def _setup__load_accounts(self):
        accs_cfg_path = os.path.join(CONFIG_PATH, 'accounts.json')
        log.info(u"Loading accounts from %s" % accs_cfg_path)
        with open(accs_cfg_path, 'rb') as f:
            raw_accs_data = json.load(f, encoding='utf-8')
        # remove accounts whose service is not supported
        raw_accs = [d for d in raw_accs_data['accounts'] if d['provider'] in self.providers]
        self.accounts.load_raw_dicts(raw_accs)

    def _sync__save_accounts(self):
        accs_cfg_path = os.path.join(CONFIG_PATH, 'accounts.json')
        d = {u'accounts': self.accounts.dump_raw_dicts()}
        with open(accs_cfg_path, 'wb') as f:
            json.dump(d, f, indent=2, encoding='utf-8')

    @property
    def ready(self):
        return self._ready


class SaywahServiceDBusWrapper(dbus.service.Object):
    def __init__(self, saywah_service, *args, **kwargs):
        super(SaywahServiceDBusWrapper, self).__init__(*args, **kwargs)
        self._saywah_service = saywah_service
        self._register_providers()
        self._register_accounts()

    def _register_providers(self):
        self._wrapped_providers = {}
        for k,v in self._saywah_service.providers.items():
            object_path = u'/providers/%s' % k
            wp = ProviderDBusWrapper(v, conn=self._connection,
                                     object_path=object_path,
                                     bus_name='org.saywah.Saywah')
            self._wrapped_providers[object_path] = wp

    def _register_accounts(self):
        self._wrapped_accounts = {}
        for a in self._saywah_service.accounts:
            object_path = u'/accounts/%s/%s' % (a.provider.slug, a.slug)
            ap = AccountDBusWrapper(a, conn=self._connection,
                                    object_path=object_path,
                                    bus_name='org.saywah.Saywah')
            self._wrapped_accounts[object_path] = ap


    # DBus 'org.saywah.Saywah' interface methods
    @dbus.service.method(dbus_interface='org.saywah.Saywah',
                         in_signature='', out_signature='as')
    def get_providers(self):
        return self._wrapped_providers.keys()


    @dbus.service.method(dbus_interface='org.saywah.Saywah',
                         in_signature='', out_signature='as')
    def get_accounts(self):
        return self._wrapped_accounts.keys()


# Our SaywahService singleton
saywah_service = SaywahService()

def start_dbus_saywah_service():
    if not saywah_service.ready:
        raise RuntimeError(u"Saywah service not set up")
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName('org.saywah.Saywah', session_bus)
    dbus_saywah_service = SaywahServiceDBusWrapper(saywah_service,
                                                   conn=session_bus,
                                                   object_path='/',
                                                   bus_name='org.saywah.Saywah')
    mainloop = gobject.MainLoop()
    log.info(u"Sarting gobject main loop")
    return mainloop.run()
