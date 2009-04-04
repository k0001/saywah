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
import locale
import logging
import re
import time
import urllib

try:
    import json
except ImportError:
    import simplejson as json

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
        log.info(u"Sending message %s with Twitter account %s" % (msg_id, account.username))
        resp, content = h.request("http://twitter.com/statuses/update.json",
                                  "POST", urllib.urlencode(data))
        if resp.status != 200:
            log.warning(u"Message %s could not be sent: %s" % (msg_id, content))
            raise TwitterRemoteError(content)
        log.info(u"Message %s sent" % msg_id)

    def get_new_messages(self, account):
        h = httplib2.Http()
        h.add_credentials(account.username, account.password)
        log.info(u"Receiving Twitter messages for account %s" % account.username)
        resp, content = h.request("http://twitter.com/statuses/friends_timeline.json", "GET")
        if resp.status != 200:
            log.warning(u"Error receiving Twitter messages")
            raise TwitterRemoteError(content)
        log.info(u"Twitter messages for account % received" % account.username)
        statuses = json.loads(content, encoding='utf-8')
        out = []
        for status in statuses:
            print repr(status['created_at'])
            message = {
                'id': status['id'],
                'utc_created_at': utc_datetime_from_twitter_timestamp(status['created_at']),
                'raw_text': status['text'],
                'sender_id': status['user']['id'],
                'sender_name': status['user']['name'],
                'sender_nick': status['user']['screen_name'],
                'sender_avatar': status['user']['profile_image_url'],
                'sender_home': u'http://twitter.com/%s' % status['user']['screen_name'] }
            out.append(message)
        # TODO: return some model
        return out


def utc_datetime_from_twitter_timestamp(s):
    """Parses as datetime.datetime in UTC a string formated Twitter timestamp"""
    # we must parse the date in an english locale (due to %a and %b)
    prev_loc = locale.getlocale()
    try:
        locale.setlocale(locale.LC_ALL, 'C')
        return datetime.datetime.strptime(s, '%a %b %d %H:%M:%S +0000 %Y')
    finally:
        locale.setlocale(locale.LC_ALL, prev_loc)

