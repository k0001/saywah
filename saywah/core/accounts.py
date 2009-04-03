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

__all__ = ("Account", "AccountsRegistry")

_utc_datetime_iso8601_strfmt = "%Y-%m-%dT%H:%M:%S.%f"


class Account(object):

    def __init__(self, username, password, service,
                 last_updated=None, last_received_message_id=None):
        self.username = username
        self.password = password
        self.service = service
        self.last_received_message_id = last_received_message_id
        if last_updated is not None and not isinstance(last_updated, datetime.datetime):
            raise TypeError(last_updated)
        self.last_updated = last_updated

    def __repr__(self):
        return u"<%s: %s - %s>" % (self.__class__.__name__, self.service, self.username)

    def to_raw_dict(self):
        d = {
            u'username': self.username,
            u'password': self.password,
            u'service': self.service }
        if self.last_updated:
            d[u'last_updated'] = self.last_updated.strftime(_utc_datetime_iso8601_strfmt)
        if self.last_received_message_id is not None:
            d[u'last_received_message_id'] = self.last_received_message_id
        return d

    @classmethod
    def from_raw_dict(cls, d):
        acc = Account(username=d['username'], password=d['password'], service=d['service'])
        if 'last_received_message_id' in d:
            acc.last_received_message_id = d['last_received_message_id']
        if 'last_updated' in d:
            acc.last_updated = datetime.datetime.strptime(d['last_updated'], _utc_datetime_iso8601_strfmt)
        return acc


class AccountsRegistry(list):
    def get_by_service_and_username(self, service, username):
        for k in self:
            if k.service == service and k.username == username:
                return k
        else:
            raise KeyError((service, username))

    def delete_by_service_and_username(self, service, username):
        for i,k in enumerate(self):
            if k.service == service and k.username == username:
                del self[i]
        else:
            raise KeyError((service, username))

    def load_raw_dicts(self, data):
        for rd in data:
            self.append(Account.from_raw_dict(rd))

    def dump_raw_dicts(self):
        return [d.to_raw_dict() for d in self]
