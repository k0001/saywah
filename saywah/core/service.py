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


__all__ = 'SaywahService',


log = logging.getLogger(__name__)


class BaseSaywahService(object):
    """Internal Saywah API services base implementation"""
    account_manager = None
    provider_manager = None
    config_manager = None

    def setup(self):
        log.info(u"Setting up SaywahService")
        self.reload_providers()
        self.reload_accounts()

    def reload_providers(self):
        self.provider_manager.unregister_all()
        self.config_manager.load_providers(self.provider_manager)

    def reload_accounts(self):
        self.account_manager.unregister_all()
        self.config_manager.load_accounts(self.account_manager)

    def store_accounts(self):
        self.config_manager.store_accounts(self.account_manager)

