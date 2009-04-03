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
import time
import urllib

import httplib2

from saywah.core.providers import Provider, ProviderRemoteError

__all__ = ('TwitterProvider',)


log = logging.getLogger(__name__)


class TwiterRemoteError(ProviderRemoteError):
    """Communication with Twitter failed"""


class TwitterProvider(Provider):
    name = u'Twitter'
    slug = u'twitter'

    def send_message(self, account, message):
        if len(message) > 140:
            raise ValueError(u"Message must be at most 140 characters long")
        msg_id = int(time.time())
        data = {"status": message.encode("utf-8")}
        h = httplib2.Http()
        h.add_credentials(account.username, account.password)
        log.info(u"Sending message %s with %s account %s" % (msg_id, self.name, account.username))
        resp, content = h.request("http://twitter.com/statuses/update.json",
                                  "POST", urllib.urlencode(data))
        if resp.status != 200:
            log.warning(u"Message %s could not be sent: %s" % (msg_id, content))
            raise TwitterRemoteError(content)

        log.info(u"Message %s sent" % msg_id)

