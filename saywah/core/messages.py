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


import uuid

from saywah.core import models


__all__ = 'Message',


class Message(models.Model):
    remote_id = models.UnicodeField()
    text = models.UnicodeField()
    utc_sent_at = models.DatetimeField()
    sender_name = models.UnicodeField()
    sender_nick = models.UnicodeField()
    sender_avatar_url = models.UnicodeField()
    sender_home_url = models.UnicodeField()
    provider_slug = models.UnicodeField()

    _uuid_namespace = uuid.UUID('96b28113-3920-403a-9e20-ca062cd366d4')

    @property
    def uuid(self):
        s = self.provider_slug.encode('utf8') + self.remote_id.encode('utf8')
        return unicode(uuid.uuid5(self.__class__._uuid_namespace, s))

    def __repr__(self):
        return u"<%s: %s - %s>" % (self.__class__.__name__, self.sender_nick or self.sender_name or '', self.text)

