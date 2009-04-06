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

from saywah.core import models


__all__ = ("Account",)


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

