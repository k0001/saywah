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
import uuid

from saywah.core import models
from saywah.core.providers import Provider


__all__ = ("Account",)


log = logging.getLogger(__name__)


class Account(models.Model):
    # provider singletons are kept here
    _registry = {}

    uuid = models.UnicodeField()
    username = models.UnicodeField()
    password = models.UnicodeField()
    provider_slug = models.UnicodeField()
    last_received_message_id = models.UnicodeField()
    last_updated = models.DatetimeField()

    def __repr__(self):
        return u"<%s: %s - %s>" % (self.__class__.__name__, self.provider_slug, self.username)


class AccountManager(object):
    """Manager for Account objects"""

    def __init__(self):
        self._registry = {}

    @property
    def accounts(self):
        return self._registry.copy()

    def register(self, account):
        if account.uuid in self._registry:
            raise KeyError(u"Account '%s' already registered" % account.uuid)
        self._registry[account.uuid] = account

    def unregister(self, key):
        del self._registry[account.uuid]

    def unregister_all(self):
        self._registry.clear()

    def create(self, provider_slug, username, **kwargs):
        account_type = Account # XXX we should support per-provider account types sometime later
        account = account_type(uuid=unicode(uuid.uuid4()), provider_slug=provider_slug, username=username)
        for k,v in kwargs.items():
            if k in account_type.get_field_names():
                setattr(account, k, v)
        return account

