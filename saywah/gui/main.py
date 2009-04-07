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
import pango


SAYWAH_GUI_PATH = os.path.abspath(os.path.dirname(__file__))
SAYWAH_GUI_RESOURCES_PATH = os.path.join(SAYWAH_GUI_PATH, u'resources')
SAYWAH_GTKUI_XML_PATH = os.path.join(SAYWAH_GUI_PATH, u'saywah.ui')

twitter_pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(SAYWAH_GUI_RESOURCES_PATH, u'twitter_32.png'), 24, 24)

class MainWindowGTK(object):
    def __init__(self, widget):
        super(MainWindowGTK, self).__init__()
        self._w = widget
        self._w.connect(u'destroy', gtk.main_quit)
        self._w.show_all()


class ProvidersComboGTK(object):
    def __init__(self, widget):
        super(ProvidersComboGTK, self).__init__()
        self._w = widget
        self._load_providers()
        self._w.set_active(0)

    def _load_providers(self):
        m = self._w.get_model()
        m.append([twitter_pixbuf, u"k0001"])


class StatusesTreeViewGTK(object):
    def __init__(self, widget):
        super(StatusesTreeViewGTK, self).__init__()
        self._w = widget
        self._col_message = self._w.get_column(0)
        self._cr_message = self._col_message.get_cell_renderers()[0]
        self._cr_message.set_property('wrap-mode', pango.WRAP_WORD_CHAR)
        self._w.connect('size-allocate', self._on_w_size_allocate)

    def _on_w_size_allocate(self, widget, allocation):
        self._cr_message.set_property('wrap-width', self._col_message.get_width() - 5)


class SaywahGTK(object):
    def __init__(self):
        super(SaywahGTK, self).__init__()
        self._builder = gtk.Builder()
        self._builder.add_from_file(SAYWAH_GTKUI_XML_PATH)
        self._providers_combo = ProvidersComboGTK(self._builder.get_object(u'combo_providers'))
        self._main_win = MainWindowGTK(self._builder.get_object(u'win_main'))


saywah_gtk = SaywahGTK()
gtk.main()

