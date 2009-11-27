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


from saywah.core.accounts import AccountManager
from saywah.core.conf.gconf import GConfConfigManager
from saywah.core.providers import ProviderManager
from saywah.core.service import BaseSaywahService


__all__ = 'DefaultSaywahService',


class DefaultSaywahService(BaseSaywahService):
    """Default Saywah Service implementation"""
    account_manager = AccountManager()
    provider_manager = ProviderManager()
    config_manager = GConfConfigManager()


