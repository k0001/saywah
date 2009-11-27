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

from __future__ import absolute_import

import logging

import gconf

from saywah.core.conf.base import BaseConfigManager


__all__ = 'GConfConfigManager',

log = logging.getLogger(__name__)

GCONF_PATHS = {
    "accounts": "/apps/saywah/accounts",
}


class GConfConfigManager(BaseConfigManager):
    """Gonfig manager using GConf as backend"""

    def __init__(self, *args, **kwargs):
        super(GConfConfigManager, self).__init__(*args, **kwargs)
        self._gconf_client = gconf.client_get_default()

    def load_accounts(self, account_manager):
        log.debug(u"Loading accounts from GConf: %s" % GCONF_PATHS["accounts"])
        for account_path in self._gconf_client.all_dirs(GCONF_PATHS["accounts"]):
            attrs = {}
            attrs['uuid'] = account_path.rsplit('/', 1)[1]
            for entry in self._gconf_client.all_entries(account_path):
                key = entry.key.rsplit('/', 1)[1]
                # XXX isn't there a more pythonic way?
                value = {
                    gconf.VALUE_BOOL: entry.value.get_bool,
                    gconf.VALUE_FLOAT: entry.value.get_float,
                    gconf.VALUE_INT: entry.value.get_int,
                    gconf.VALUE_STRING: lambda: entry.value.get_string().decode('utf8')
                }[entry.value.type]()
                attrs[key] = value
            account = account_manager.create(**attrs)
            account_manager.register(account)
            log.debug(u"Account '%s' loaded from GConf" % account.uuid)
        log.info(u"Accounts loaded from GConf")

    def store_accounts(self, account_manager):
        log.debug(u"Storing current accounts in GConf: %s" % GCONF_PATHS["accounts"])
        self._gconf_client.recursive_unset(GCONF_PATHS["accounts"], gconf.UNSET_INCLUDING_SCHEMA_NAMES)
        self._gconf_client.suggest_sync()
        for account in account_manager.accounts.values():
            path = "%s/%s" % (GCONF_PATHS["accounts"], account.uuid)
            for k,v in account.to_dict(raw=True).items():
                key = "%s/%s" % (path, k)
                if v is None:
                    self._gconf_client.unset(key)
                elif isinstance(v, unicode):
                    self._gconf_client.set_value(key, v.encode('utf-8'))
                else:
                    self._gconf_client.set_value(key, v)
            log.debug(u"Stored account '%s' to GConf" % account.uuid)
        self._gconf_client.suggest_sync()
        log.info(u"Accounts stored to GConf")

