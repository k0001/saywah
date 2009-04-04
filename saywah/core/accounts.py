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

import dbus
import dbus.service

from saywah.core import models

__all__ = ("Account", "AccountsRegistry")


log = logging.getLogger(__name__)


class Account(models.Model):
    username = models.UnicodeField()
    password = models.UnicodeField()
    provider_slug = models.UnicodeField()
    last_received_message_id = models.UnicodeField()
    last_updated = models.DatetimeField()

    objects = set()

    def __repr__(self):
        return u"<%s: %s - %s>" % (self.__class__.__name__, self.provider_slug, self.username)

    def _get_provider(self):
        from saywah.core.service import saywah_service
        if self.provider_slug:
            return saywah_service.providers[self.provider_slug]

    def _set_provider(self, value):
        from saywah.core.providers import Provider
        if value is None:
            self.provider_slug = None
        elif isinstance(value, Provider):
            self.provider_slug = value.slug
        else:
            raise TypeError(value)

    provider = property(_get_provider, _set_provider)

    @property
    def slug(self):
        return self.username.replace(u' ', u'+')


class AccountDBusWrapper(dbus.service.Object):
    def __init__(self, account, *args, **kwargs):
        self._account = account
        super(AccountDBusWrapper, self).__init__(*args, **kwargs)

    # DBus 'org.saywah.Account' interface methods
    @dbus.service.method(dbus_interface='org.saywah.Account',
                         in_signature='', out_signature='a{ss}')
    def get_details(self):
        d = dict((k, unicode(v)) for (k,v) in self._account.to_raw_dict().items())
        del d['password']
        return d

    @dbus.service.method(dbus_interface='org.saywah.Account',
                         in_signature='s', out_signature='')
    def send_message(self, message):
        self._account.provider.send_message(self._account, message)



class AccountsRegistry(object):
    def __init__(self, iterable=None):
        self._list = list(iterable or ())

    def get_by_service_and_username(self, service, username):
        for k in self._list:
            if k.service == service and k.username == username:
                return k
        else:
            raise KeyError((service, username))

    def delete_by_service_and_username(self, service, username):
        for i,k in enumerate(self._list):
            if k.service == service and k.username == username:
                del self._list[i]
        else:
            raise KeyError((service, username))

    def load(self, account):
        if not isinstance(account, Account):
            raise TypeError(account)
        log.debug(u'Loading %s' % repr(account))
        self._list.append(account)

    def load_raw_dicts(self, data):
        for rd in data:
            self.load(Account.from_raw_dict(rd))

    def dump_raw_dicts(self):
        return [d.to_raw_dict() for d in self._list]

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, repr(self._list))

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)
