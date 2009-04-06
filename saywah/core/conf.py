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

PATH_ROOT_DIR = os.path.expanduser(u'~/.saywah')
PATH_ACCOUNTS_JSON = os.path.join(PATH_ROOT_DIR, u'accounts.json')


def accounts_to_json(accounts, encoding='utf-8', indent=2):
    d = {u'accounts': [a.to_raw_dict() for a in accounts]}
    return json.dumps(d, encoding=encoding, indent=indent)

def accounts_from_json(js, encoding='utf-8'):
    d = json.loads(js, encoding=encoding)
    return [Account.from_raw_dict(a) for a in d['accounts']]

def store_current_accounts():
    accounts = list(Account.objects)
    js = accounts_to_json(accounts)
    if not os.path.isdir(PATH_ROOT_DIR):
        os.makedirs(PATH_ROOT_DIR)
    with open(PATH_ACCOUNTS_JSON, 'wb') as f:
        f.write(js)

def load_accounts():
    if not os.path.isfile(PATH_ACCOUNTS_JSON):
        return
    with open(PATH_ACCOUNTS_JSON, 'rb') as f:
        js = f.read()
    accounts = accounts_from_json(js)
    Account.objects.update(set(accounts))

def unload_accounts():
    Account.objects.clear()

def reload_accounts():
    unload_accounts()
    load_accounts()

