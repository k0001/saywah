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


import datetime
import logging

import dbus
import dbus.service

__all__ = ("Account", "AccountsRegistry")


_utc_datetime_iso8601_strfmt = "%Y-%m-%dT%H:%M:%S.%f"

log = logging.getLogger(__name__)


class Account(object):

    def __init__(self, username, password, provider,
                 last_updated=None, last_received_message_id=None):
        self.username = username
        self.password = password
        self.provider = provider
        self.last_received_message_id = last_received_message_id
        if last_updated is not None and not isinstance(last_updated, datetime.datetime):
            raise TypeError(last_updated)
        self.last_updated = last_updated

    def __repr__(self):
        return u"<%s: %s - %s>" % (self.__class__.__name__, self.provider.name, self.username)

    def _get_provider(self):
        if hasattr(self, '_provider'):
            return self._provider
        raise AttributeError

    def _set_provider(self, value):
        from saywah.core.providers import Provider
        if isinstance(value, Provider):
            self._provider = value
        elif isinstance(value, basestring):
            from saywah.core.service import saywah_service
            self._provider = saywah_service.providers[value]
        else:
            raise TypeError(value)

    provider = property(_get_provider, _set_provider)

    @property
    def slug(self):
        return self.username.replace(u' ', u'+')

    def to_raw_dict(self):
        d = {
            u'username': self.username,
            u'password': self.password,
            u'provider': self.provider.slug }
        if self.last_updated:
            d[u'last_updated'] = self.last_updated.strftime(_utc_datetime_iso8601_strfmt)
        if self.last_received_message_id is not None:
            d[u'last_received_message_id'] = self.last_received_message_id
        return d

    @classmethod
    def from_raw_dict(cls, d):
        acc = Account(username=d['username'], password=d['password'], provider=d['provider'])
        if 'last_received_message_id' in d:
            acc.last_received_message_id = d['last_received_message_id']
        if 'last_updated' in d:
            acc.last_updated = datetime.datetime.strptime(d['last_updated'], _utc_datetime_iso8601_strfmt)
        return acc


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
