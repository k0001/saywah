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

__all__ = ("Account",)


class Account(object):
    def __init__(self, username, password, service,
                 last_updated=None, last_received_message_id=None):
        self.username = username
        self.password = password
        self.service = service
        self.last_received_message_id = last_received_message_id
        if not isinstance(last_updated, datetime.datetime):
            raise TypeError(last_updated)
        self.last_updated = last_updated

    def __repr__(self):
        return u"<%s: %s - %s>" % (self.__class__.__name__, self.service, self.username)
