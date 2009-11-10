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


import louie


__all__ = ("SignalingSet",)


class SignalingSet(object):
    """Minimal set-like container sending signals before and after addition/removal of items"""

    def __init__(self, iterable=()):
        self._s = set()
        # useul signals
        self.pre_add = louie.signal.Signal()
        self.post_add = louie.signal.Signal()
        self.pre_remove = louie.signal.Signal()
        self.post_remove = louie.signal.Signal()
        self.update(iterable)

    def __repr__(self):
        return u'<%s %s>' % (self.__class__.__name__, list(self._s))

    def add(self, item):
        if not item in self._s:
            louie.send(self.pre_add, sender=self, named={u'item': item})
            self._s.add(item)
            louie.send(self.post_add, sender=self, named={u'item': item})

    def update(self, *others):
        for iterable in others:
            for item in iterable:
                self.add(item)

    def remove(self, item):
        if not item in self:
            raise KeyError(item)
        louie.send(self.pre_remove, sender=self, named={u'item': item})
        self._s.remove(item)
        louie.send(self.post_remove, sender=self, named={u'item': item})

    def discard(self, item):
        try:
            self.remove(item)
        except KeyError, e:
            pass

    def copy(self):
        return self.__class__(self)

    def __iter__(self):
        return iter(self._s)

