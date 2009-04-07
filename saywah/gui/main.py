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


SAYWAH_GUI_PATH = os.path.abspath(os.path.dirname(__file__))
SAYWAH_GUI_RESOURCES_PATH = os.path.join(SAYWAH_GUI_PATH, u'resources')
SAYWAH_GTKUI_XML_PATH = os.path.join(SAYWAH_GUI_PATH, u'saywah.ui')

twitter_pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(SAYWAH_GUI_RESOURCES_PATH, u'twitter_32.png'), 24, 24)

test_statuses = [
    {
        u'message': u'Hello World',
        u'sender': u'k0001',
        u'provider': u'Twitter',
        u'sender_pic': u'k0001.gif',
    },
    {
        u'message': u'From @dehora: "on the Web, programming languages are an implementation detail" -- http://is.gd/r0Fz',
        u'sender': u'maristaran',
        u'provider': u'Twitter',
        u'sender_pic': u'manu.jpg',
    },
    {
        u'message': u'Para el que no fue, están pasando el recital de Radiohead por Canal 13',
        u'sender': u'fzunino',
        u'provider': u'Twitter',
        u'sender_pic': u'fzunino.jpg',
    },
    {
        u'message': u'Nothing in this life feels as good as the sensation you get the moment you step into the Bombonera http://twitpic.com/2vqsh (Boca vs Godoy)',
        u'sender': u'santisiri',
        u'provider': u'Twitter',
        u'sender_pic': u'santisiri.png',
    },
    {
        u'message': u'Niels Bohr: "Prediction is very difficult, especially about the future"',
        u'sender': u'earlkman',
        u'provider': u'Twitter',
        u'sender_pic': u'earlkman.jpg',
    },
]

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
        self._load_statuses()

    def _load_statuses(self):
        m = self._w.get_model()
        for i in test_statuses:
            sender_pic = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(SAYWAH_GUI_RESOURCES_PATH,
                                                                           u'test', i[u'sender_pic']),
                                                              48, 48)
            iter = m.append([i[u'sender'], sender_pic, i[u'message'], i[u'provider'], twitter_pixbuf])


class SaywahGTK(object):
    def __init__(self):
        super(SaywahGTK, self).__init__()
        self._builder = gtk.Builder()
        self._builder.add_from_file(SAYWAH_GTKUI_XML_PATH)
        self._providers_combo = ProvidersComboGTK(self._builder.get_object(u'combo_providers'))
        self._statuses_treeview = StatusesTreeViewGTK(self._builder.get_object(u'treeview_statuses'))
        self._main_win = MainWindowGTK(self._builder.get_object(u'win_main'))


saywah_gtk = SaywahGTK()
gtk.main()


