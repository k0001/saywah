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
try:
    import json
except ImportError, e:
    import simplejson as json

from saywah.core.accounts import Account


__all__ = ('store_current_accounts', 'load_accounts', 'init')


log = logging.getLogger(__name__)

PATH_ROOT_DIR = os.path.expanduser(u'~/.saywah')
PATH_ACCOUNTS_JSON = os.path.join(PATH_ROOT_DIR, u'accounts.json')


def accounts_to_json(accounts, encoding='utf-8', indent=2):
    d = {u'accounts': [a.to_raw_dict() for a in accounts]}
    return json.dumps(d, encoding=encoding, indent=indent)

def accounts_from_json(js, encoding='utf-8'):
    d = json.loads(js, encoding=encoding)
    return [Account.from_raw_dict(a) for a in d['accounts']]

def store_current_accounts():
    log.debug(u"Storing current accounts in %s" % PATH_ACCOUNTS_JSON)
    accounts = list(Account.objects)
    js = accounts_to_json(accounts)
    with open(PATH_ACCOUNTS_JSON, 'wb') as f:
        f.write(js)

def load_accounts():
    log.debug(u"Loading accounts from %s" % PATH_ACCOUNTS_JSON)
    if not os.path.isfile(PATH_ACCOUNTS_JSON):
        log.debug(u"Nothing to load")
        return
    with open(PATH_ACCOUNTS_JSON, 'rb') as f:
        js = f.read()
    accounts = accounts_from_json(js)
    Account.objects.update(set(accounts))
    log.debug(u"%d accounts loaded" % len(accounts))

def load_providers():
    # XXX: unharcode this by discovering all Providers found in saywah.providers package
    from saywah.providers.twitter import TwitterProvider
    TwitterProvider()

def init(log_level=logging.WARNING):
    # this is here so that everything explodes early if we can't write there
    if not os.path.isdir(PATH_ROOT_DIR):
        os.makedirs(PATH_ROOT_DIR)
        log.debug(u"Directory %s created" % PATH_ROOT_DIR)
    logging.basicConfig(level=log_level)
    load_providers()
    load_accounts()

