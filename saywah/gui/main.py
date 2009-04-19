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
import dbus.mainloop.glib
import gobject
import pygtk; pygtk.require20()
import gtk
import pango


SAYWAH_GUI_PATH = os.path.abspath(os.path.dirname(__file__))
SAYWAH_GUI_RESOURCES_PATH = os.path.join(SAYWAH_GUI_PATH, u'resources')
SAYWAH_GTKUI_XML_PATH = os.path.join(SAYWAH_GUI_PATH, u'saywah.ui')


mainloop = gobject.MainLoop()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
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
        self._preload_images()
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
                        self._get_pixbuf_from_filename(u'provider_%s.png' % pprops['slug'], 24, 24)])

    def _prepare_treeview_statuses(self):
        self._treeview_statuses = self._builder.get_object(u'treeview_statuses')
        self._col_statuses_message = self._builder.get_object(u'col_statuses_message')
        self._cr_statuses_message = self._builder.get_object(u'cr_statuses_message')
        self._cr_statuses_message.set_property('wrap-mode', pango.WRAP_WORD_CHAR)
        self._cr_statuses_message.set_property('single-paragraph-mode', True)
        self._cr_statuses_message.set_property('yalign', 0.0)

    def _prepare_win_main(self):
        self._win_main = self._builder.get_object(u'win_main')
        self._entry_message = self._builder.get_object(u'entry_message')
        self._btn_send = self._builder.get_object(u'btn_send')
        self._img_btn_send = self._builder.get_object(u'img_btn_send')

    def _prepare_combo_accounts(self):
        self._combo_accounts = self._builder.get_object(u'combo_accounts')
        self._combo_accounts.set_active(0)

    def _preload_images(self):
        working_imgs = glob.glob(os.path.join(SAYWAH_GUI_RESOURCES_PATH, 'working-*.png'))
        for fn in working_imgs:
            self._get_pixbuf_from_filename(fn, 24, 24)
        self._n_working_frames = len(working_imgs)

    def _get_pixbuf_from_filename(self, fname, width, height):
        if not hasattr(self, '_pixbuf_cache'):
            self._pixbuf_cache = {}
        key = (fname, width, height)
        if not key in self._pixbuf_cache:
            fname = os.path.join(SAYWAH_GUI_RESOURCES_PATH, fname)
            if not os.path.isfile(fname):
                pixbuf = None
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(fname, width, height)
                print 'loaded', fname
            self._pixbuf_cache[key] = pixbuf
        return self._pixbuf_cache[key]


    # GObject event handlers

    def on_win_main_destroy(self, widget):
        mainloop.quit()

    def on_treeview_statuses_size_allocate(self, widget, allocation):
        self._cr_statuses_message.set_property('wrap-width', self._col_statuses_message.get_width() - 5)

    def on_btn_send_clicked(self, widget):
        iaccount = self._combo_accounts.get_active_iter()
        apath = self._model_accounts.get_value(iaccount, 0)
        account = self._dbus_proxies_cache[apath]
        message = self._entry_message.get_text().decode('utf8')

        def update_message_waiting():
            if self._sending_message:
                if not hasattr(self, '_img_btn_next_frame'): # first time in this loop
                    self._btn_send.set_sensitive(False)
                    self._img_btn_send_orig_stock = self._img_btn_send.get_stock()
                    self._img_btn_next_frame = 0
                if self._img_btn_next_frame == self._n_working_frames - 1:
                    self._img_btn_next_frame = 0
                img_path = os.path.join(SAYWAH_GUI_RESOURCES_PATH, 'working-%02d.png' % self._img_btn_next_frame)
                self._img_btn_send.set_from_pixbuf(
                        self._get_pixbuf_from_filename(img_path, 24, 24))
                self._img_btn_next_frame += 1
                return True
            else:
                self._img_btn_send.set_from_stock(*self._img_btn_send_orig_stock)
                self._btn_send.set_sensitive(True)
                del self._img_btn_next_frame
                del self._img_btn_send_orig_stock
                return False

        def on_send_message_success():
            self._sending_message = False

        def on_send_message_error(error):
            self._sending_message = False
            raise TODO

        self._sending_message = True
        account.send_message(message, dbus_interface='org.saywah.Account',
                             reply_handler=on_send_message_success,
                             error_handler=on_send_message_error)
        gobject.timeout_add(50, update_message_waiting)



if __name__ == '__main__':
    saywah_gtk = SaywahGTK()
    mainloop.run()

