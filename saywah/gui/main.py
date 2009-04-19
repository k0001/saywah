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


import glob
import os

import dbus
import pygtk
pygtk.require20()
import gtk
import pango


SAYWAH_GUI_PATH = os.path.abspath(os.path.dirname(__file__))
SAYWAH_GUI_RESOURCES_PATH = os.path.join(SAYWAH_GUI_PATH, u'resources')
SAYWAH_GTKUI_XML_PATH = os.path.join(SAYWAH_GUI_PATH, u'saywah.ui')

session_bus = dbus.SessionBus()



class SaywahGTK(object):
    def __init__(self):
        super(SaywahGTK, self).__init__()
        self._builder = gtk.Builder()
        self._builder.add_from_file(SAYWAH_GTKUI_XML_PATH)
        self._reload_model_accounts()
        self._prepare_treeview_statuses()
        self._prepare_win_main()
        self._prepare_combo_accounts()
        self._builder.connect_signals(self)
        self._win_main.show_all()

    def _reload_model_accounts(self):
        self._dbus_proxies_cache = {}
        self._model_accounts = self._builder.get_object(u'model_accounts')
        self._model_accounts.clear()
        dsaywah = session_bus.get_object('org.saywah.Saywah', '/org/saywah/Saywah')
        providers_paths = dsaywah.get_providers(dbus_interface='org.saywah.Saywah')
        for ppath in providers_paths:
            provider = session_bus.get_object('org.saywah.Saywah', ppath)
            self._dbus_proxies_cache[ppath] = provider
            pprops = provider.GetAll(u'', dbus_interface='org.freedesktop.DBus.Properties')
            for apath in provider.get_accounts(dbus_interface='org.saywah.Provider'):
                account = session_bus.get_object('org.saywah.Saywah', apath)
                self._dbus_proxies_cache[apath] = account
                aprops = account.GetAll(u'', dbus_interface='org.freedesktop.DBus.Properties')
                self._model_accounts.append([
                        apath,
                        ppath,
                        aprops['username'],
                        aprops['slug'],
                        pprops['name'],
                        pprops['slug'],
                        self._get_provider_pixbuf(pprops['slug'])])

    def _prepare_treeview_statuses(self):
        self._treeview_statuses = self._builder.get_object(u'treeview_statuses')
        self._col_statuses_message = self._builder.get_object(u'col_statuses_message')
        self._cr_statuses_message = self._builder.get_object(u'cr_statuses_message')
        self._cr_statuses_message.set_property('wrap-mode', pango.WRAP_WORD_CHAR)
        self._cr_statuses_message.set_property('single-paragraph-mode', True)
        self._cr_statuses_message.set_property('yalign', 0.0)

    def _prepare_win_main(self):
        self._win_main = self._builder.get_object(u'win_main')
        self._btn_send = self._builder.get_object(u'btn_send')
        self._entry_message = self._builder.get_object(u'entry_message')


    def _prepare_combo_accounts(self):
        self._combo_accounts = self._builder.get_object(u'combo_accounts')
        self._combo_accounts.set_active(0)

    def _get_provider_pixbuf(self, provider_slug):
        if not hasattr(self, '_providers_pixbuf_cache'):
            self._providers_pixbuf_cache = {}
        if not provider_slug in self._providers_pixbuf_cache:
            fname = os.path.join(SAYWAH_GUI_RESOURCES_PATH, u'provider_%s.png' % provider_slug)
            if not os.path.isfile(fname):
                pixbuf = None
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(fname, 24, 24)
            self._providers_pixbuf_cache[provider_slug] = pixbuf
        return self._providers_pixbuf_cache[provider_slug]


    # GObject event handlers

    def on_win_main_destroy(self, widget):
        gtk.main_quit()

    def on_treeview_statuses_size_allocate(self, widget, allocation):
        self._cr_statuses_message.set_property('wrap-width', self._col_statuses_message.get_width() - 5)

    def on_btn_send_clicked(self, widget):
        iaccount = self._combo_accounts.get_active_iter()
        apath = self._model_accounts.get_value(iaccount, 0)
        account = self._dbus_proxies_cache[apath]
        message = self._entry_message.get_text().decode('utf8')
        account.send_message(message, dbus_interface='org.saywah.Account')

saywah_gtk = SaywahGTK()
gtk.main()

