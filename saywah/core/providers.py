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


__all__ = 'Provider', 'ProviderError', 'ProviderRemoteError', 'ProviderManager',


log = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider errors"""


class ProviderRemoteError(ProviderError):
    """Raised when communication with a remote provider fails somehow."""


class Provider(object):
    """A (microblogging) service provider"""
    # A pretty name for this provider
    name = u''
    # A short slug for this provider
    slug = u''

    @property
    def features(self):
        meth_names = ('send_message', 'get_new_messages')
        return tuple(n for n in meth_names if not getattr(getattr(self, n), '_disabled', False))

    # The following methods are to be overriden by provider implementations

    def send_message(self, account, message):
        raise NotImplementedError()
    send_message._disabled = True

    def get_new_messages(self, account):
        raise NotImplementedError()
    get_new_messages._disabled = True


class ProviderManager(object):
    """Manager for Provider objects"""
    def __init__(self):
        self._registry = {}

    @property
    def providers(self):
        return self._registry.copy()

    def register(self, provider):
        if provider.slug in self._registry:
            raise KeyError(u"Provider '%s' already registered" % provider.slug)
        self._registry[provider.slug] = provider

    def unregister(self, key):
        del self._registry[provider.slug]

    def unregister_all(self):
        self._registry.clear()

