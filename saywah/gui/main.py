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


import os

import pygtk
pygtk.require20()
import gtk


SAYWAH_GTKUI_PATH = os.path.join(os.path.dirname(__file__), u'saywah.ui')
assert os.path.isfile(SAYWAH_GTKUI_PATH)


class MainWindowGTK(object):
    def __init__(self, widget):
        super(MainWindowGTK, self).__init__()
        self._w = widget
        self._w.connect(u'destroy', gtk.main_quit)
        self._w.show_all()


class SaywahGTK(object):
    def __init__(self):
        super(SaywahGTK, self).__init__()
        self._builder = gtk.Builder()
        self._builder.add_from_file(SAYWAH_GTKUI_PATH)
        self._main_win = MainWindowGTK(self._builder.get_object(u'win_main'))


saywah_gtk = SaywahGTK()
gtk.main()


