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
import os

from saywah.core import conf


__all__ = ('SaywahService', 'SaywahServiceDBusWrapper', 'saywah_service')


log = logging.getLogger(__name__)


class SaywahService(object):
    def __init__(self):
        super(SaywahService, self).__init__()
        self._ready = False

    def setup(self):
        if not self.ready:
            log.info(u"Setting up SaywahService")
            self.load_accounts()

    def save_accounts(self):
        conf.store_current_accounts()

    def load_accounts(self):
        conf.load_accounts()

    @property
    def ready(self):
        return self._ready

# Our SaywahService singleton
saywah_service = SaywahService()

