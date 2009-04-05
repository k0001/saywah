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

__all__ = ("Account",)


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

