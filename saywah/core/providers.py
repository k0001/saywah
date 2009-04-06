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


__all__ = ('Provider', 'ProviderError', 'ProviderRemoteError')


log = logging.getLogger(__name__)


class ProviderError(Exception):
    """Base exception for provider errors"""


class ProviderRemoteError(ProviderError):
    """Raised when communication with a remote provider fails somehow."""


class Provider(object):
    # A pretty name for this provider
    name = u''
    # A short slug for this provider
    slug = u''
    # provider singletons are kept here
    register = {}

    def __new__(cls, *args, **kwargs):
        # ensure singletons for each provider are available in Provider.register
        if not cls.slug in Provider.register:
            obj = super(Provider, cls).__new__(cls, *args, **kwargs)
            Provider.register[cls.slug] = obj
            log.debug(u"%s registered" % cls.__name__)
        return Provider.register[cls.slug]

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

