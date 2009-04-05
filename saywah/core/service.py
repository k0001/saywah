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

from saywah.core.providers import ProviderDBusWrapper
from saywah.core.accounts import Account, AccountsRegistry, AccountDBusWrapper


__all__ = ('SaywahService', 'SaywahServiceDBusWrapper', 'saywah_service')


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


# Our SaywahService singleton
saywah_service = SaywahService()

