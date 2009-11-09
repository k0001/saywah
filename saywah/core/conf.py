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

from __future__ import with_statement

import logging
import os
import re

import gconf
try:
    import json
except ImportError, e:
    import simplejson as json

from saywah.core.accounts import Account


__all__ = ('store_current_accounts', 'load_accounts', 'init')


log = logging.getLogger(__name__)
gconf_client = gconf.client_get_default()

GCONF_PATHS = {
    "accounts": "/apps/saywah/accounts",
}


def store_current_accounts():
    # should delete old stuff
    log.debug(u"Storing current accounts in gconf: %s" % GCONF_PATHS["accounts"])
    gconf_client.recursive_unset(GCONF_PATHS["accounts"], gconf.UNSET_INCLUDING_SCHEMA_NAMES)
    gconf_client.get_entry(GCONF_PATHS["accounts"], 'C', False).unref()
    for i,a in enumerate(list(Account.objects)):
        path = "%s/%03d" % (GCONF_PATHS["accounts"], i)
        for k,v in a.to_dict(raw=True).items():
            key = "%s/%s" % (path, k)
            if v is None:
                gconf_client.unset(key)
            elif isinstance(v, unicode):
                gconf_client.set_value(key, v.encode('utf-8'))
            else:
                gconf_client.set_value(key, v)
    gconf_client.suggest_sync()

def load_accounts():
    log.debug(u"Loading accounts from gconf: %s" % GCONF_PATHS["accounts"])
    naccs = 0
    for path in gconf_client.all_dirs(GCONF_PATHS["accounts"]):
        attrs = {}
        for k in Account.get_field_names():
            try:
                v = gconf_client.get_value("%s/%s" % (path, k))
                if isinstance(v, str):
                    v = v.decode('utf-8')
                attrs[k] = v
            except ValueError:
                attrs[k] = None
        Account.objects.add(Account.from_dict(attrs))
        naccs += 1
    log.debug(u"%d accounts loaded" % naccs)

def load_providers():
    # XXX: unharcode this by discovering all Providers found in saywah.providers package
    from saywah.providers.twitter import TwitterProvider
    TwitterProvider()

def init(log_level=logging.WARNING):
    # this is here so that everything explodes early if we can't write there
    logging.basicConfig(level=log_level)
    load_providers()
    load_accounts()

