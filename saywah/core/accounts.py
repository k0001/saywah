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
    username = models.UnicodeField()
    password = models.UnicodeField()
    provider_slug = models.UnicodeField()
    last_received_message_id = models.UnicodeField()
    last_updated = models.DatetimeField()

    _uuid_namespace = uuid.UUID('4c3a97ad-8a3f-4542-98b8-6aa98a3a15aa')

    @property
    def uuid(self):
        s = self.provider_slug.encode('utf8') + self.username.encode('utf8')
        return unicode(uuid.uuid5(self.__class__._uuid_namespace, s))

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
        account = account_type(provider_slug=provider_slug, username=username, **kwargs)
        return account

