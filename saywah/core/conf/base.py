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


__all__ = 'BaseConfigManager',


class BaseConfigManager(object):
   """Base configuration manager"""

   def load_providers(self, provider_manager):
       """Load and register providers from the underlaying configuration to the given ``ProviderManager``"""
       # TODO unharcode this by discovering all Providers found in saywah.providers package
       from saywah.providers.twitter import TwitterProvider
       provider_manager.register(TwitterProvider())

   def load_accounts(self, account_manager):
       """Load and register accounts from the underlaying configuration to the given ``AccountManager``"""
       raise NotImplementedError

   def store_accounts(self, account_manager):
       """Store the Accounts found in the given ``AccountManager`` to the underlaying configuration"""
       raise NotImplementedError


