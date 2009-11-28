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
import logging
import os

import dbus
import dbus.mainloop.glib
import gobject
import pygtk; pygtk.require20()
import gtk
import pango


mainloop = gobject.MainLoop()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

SAYWAH_GUI_PATH = os.path.abspath(os.path.dirname(__file__))
SAYWAH_GUI_RESOURCES_PATH = os.path.join(SAYWAH_GUI_PATH, u'resources')
SAYWAH_GTKUI_XML_PATH = os.path.join(SAYWAH_GUI_PATH, u'saywah.ui')

DBUS_CONNECTION = dbus.SessionBus()
DBUS_BUS_NAME = 'org.saywah.Saywah'

log = logging.getLogger(__name__)


def get_saywah_dbus_object(object_path):
    return DBUS_CONNECTION.get_object(DBUS_BUS_NAME, object_path)


def get_pixbuf_from_filename(fname, width, height):
    global _pixbuf_cache
    try:
        _pixbuf_cache
    except NameError:
        _pixbuf_cache = {}
    key = (fname, width, height)
    if not key in _pixbuf_cache:
        fname = os.path.join(SAYWAH_GUI_RESOURCES_PATH, fname)
        if not os.path.isfile(fname):
            pixbuf = None
        else:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(fname, width, height)
        _pixbuf_cache[key] = pixbuf
    return _pixbuf_cache[key]


class SaywahGTK(object):
    def __init__(self):
        self._builder = gtk.Builder()
        self._builder.add_from_file(SAYWAH_GTKUI_XML_PATH)
        self._builder.connect_signals(self)

        self.reload_model_providers()
        self.reload_model_accounts()

        win_main = self._builder.get_object(u'win_main')
        win_main.show_all()

    def reload_model_accounts(self):
        m = self._builder.get_object('model_accounts')
        m.clear()
        providers = get_saywah_dbus_object('/org/saywah/Saywah/providers')
        for ppath in providers.GetProviders(dbus_interface='org.saywah.Providers'):
            provider = get_saywah_dbus_object(ppath)
            pprops = provider.GetAll('', dbus_interface='org.freedesktop.DBus.Properties')
            for apath in provider.GetAccounts(dbus_interface='org.saywah.Provider'):
                account = get_saywah_dbus_object(apath)
                aprops = account.GetAll('', dbus_interface='org.freedesktop.DBus.Properties')
                m.append([apath, ppath, aprops['username'], aprops['uuid'], pprops['name'], pprops['slug'],
                          get_pixbuf_from_filename(u'provider_%s.png' % pprops['slug'], 24, 24)])

    def reload_model_providers(self):
        m = self._builder.get_object(u'model_providers')
        m.clear()
        providers = get_saywah_dbus_object('/org/saywah/Saywah/providers')
        for ppath in providers.GetProviders(dbus_interface='org.saywah.Providers'):
            provider = get_saywah_dbus_object(ppath)
            pprops = provider.GetAll(u'', dbus_interface='org.freedesktop.DBus.Properties')
            m.append([ppath, pprops['slug'], pprops['name'],
                      get_pixbuf_from_filename(u'provider_%s.png' % pprops['slug'], 24, 24)])

    def on_quit(self, widget):
        mainloop.quit()

    def on_menu_accounts_add_activate(self, widget):
        combo_providers = self._builder.get_object('combo_providers')
        entry_username = self._builder.get_object('entry_username')
        entry_password = self._builder.get_object('entry_password')
        dlg_account_add = self._builder.get_object('dlg_account_add')

        self.reload_model_accounts()
        combo_providers.set_active(0)
        combo_providers.grab_focus()
        entry_username.set_text('')
        entry_password.set_text('')

        response = dlg_account_add.run()
        if response == gtk.RESPONSE_OK:
            iprovider = combo_providers.get_active_iter()
            provider_slug = self._model_providers.get_value(iprovider, 1)
            username = entry_username.get_text().decode('utf8')
            password = entry_password.get_text().decode('utf8')
            accounts = get_saywah_dbus_object('/org/saywah/Saywah/accounts')
            apath = accounts.AddAccount(provider_slug, username, dbus_interface='org.saywah.Accounts')
            account = get_saywah_dbus_object('org.saywah.Saywah', apath)
            account.Set('', 'password', password, dbus_interface='org.freedesktop.DBus.Properties')
            accounts.StoreAccounts(dbus_interface='org.saywah.Accounts')
            uuid = account.Get('', 'uuid', dbus_interface='org.freedesktop.DBus.Properties')
            log.info(u"Added %s account %s [uuid:%s]" % (provider_slug, username, uuid))
            self.reload_model_accounts()
        dlg_account_add.hide()

    def on_btn_send_clicked(self, widget):
        def update_message_waiting(_tmp={}):
            btn_send = _tmp.setdefault('btn_send', self._builder.get_object('btn_send'))
            img_btn_send = _tmp.setdefault('img_btn_send', self._builder.get_object('img_btn_send'))
            if self._sending_message:
                if not 'next_frame' in _tmp:
                    btn_send.set_sensitive(False)
                    _tmp.setdefault('img_orig_stock', img_btn_send.get_stock())
                    _tmp['next_frame'] = 0
                n_frames = 31 # number of working-*.png images
                img_path = os.path.join(SAYWAH_GUI_RESOURCES_PATH, 'working-%02d.png' % (_tmp['next_frame'] % n_frames))
                img_btn_send.set_from_pixbuf(get_pixbuf_from_filename(img_path, 24, 24))
                _tmp['next_frame'] += 1
                return True
            else:
                img_btn_send.set_from_stock(*_tmp['img_orig_stock'])
                btn_send.set_sensitive(True)
                del _tmp['next_frame']
                return False

        def on_send_message_success():
            self._sending_message = False

        def on_send_message_error(error):
            self._sending_message = False
            raise TODO

        combo_accounts = self._builder.get_object('combo_accounts')
        model_accounts = self._builder.get_object('model_accounts')
        entry_message = self._builder.get_object('entry_message')

        iaccount = combo_accounts.get_active_iter()
        apath = model_accounts.get_value(iaccount, 0)
        account = get_saywah_dbus_object(apath)
        message = entry_message.get_text().decode('utf8')

        self._sending_message = True
        account.SendMessage(message, dbus_interface='org.saywah.Account',
                            reply_handler=on_send_message_success,
                            error_handler=on_send_message_error)

        log.info(u"Sending message: %s" % message)
        gobject.timeout_add(50, update_message_waiting)


#class SaywahGTK(object):
#    def __init__(self):
#        self._builder = gtk.Builder()
#        self._builder.add_from_file(SAYWAH_GTKUI_XML_PATH)
#        self._reload_model_accounts()
#        self._prepare_treeview_statuses()
#        self._prepare_win_main()
#        self._prepare_combo_accounts()
#        self._preload_images()
#        self._builder.connect_signals(self)
#        self._win_main.show_all()
#
#    def _reload_model_accounts(self):
#        self._model_accounts = self._builder.get_object(u'model_accounts')
#        self._model_accounts.clear()
#        providers = DBUS_CONNECTION.get_object(DBUS_BUS_NAME, '/org/saywah/Saywah/providers')
#        providers_paths = providers.GetProviders(dbus_interface='org.saywah.Providers')
#        for ppath in providers_paths:
#            provider = DBUS_CONNECTION.get_object(DBUS_BUS_NAME, ppath)
#            pprops = provider.GetAll('', dbus_interface='org.freedesktop.DBus.Properties')
#            for apath in provider.GetAccounts(dbus_interface='org.saywah.Provider'):
#                account = DBUS_CONNECTION.get_object(DBUS_BUS_NAME, apath)
#                aprops = account.GetAll(u'', dbus_interface='org.freedesktop.DBus.Properties')
#                self._model_accounts.append([
#                        apath,
#                        ppath,
#                        aprops['username'],
#                        aprops['uuid'],
#                        pprops['name'],
#                        pprops['slug'],
#                        self._get_pixbuf_from_filename(u'provider_%s.png' % pprops['slug'], 24, 24)])
#
#    def _reload_model_providers(self):
#        self._model_providers = self._builder.get_object(u'model_providers')
#        self._model_providers.clear()
#        providers = DBUS_CONNECTION.get_object(DBUS_BUS_NAME, '/org/saywah/Saywah/providers')
#        providers_paths = providers.GetProviders(dbus_interface='org.saywah.Providers')
#        for ppath in providers_paths:
#            provider = DBUS_CONNECTION.get_object(DBUS_BUS_NAME, ppath)
#            pprops = provider.GetAll(u'', dbus_interface='org.freedesktop.DBus.Properties')
#            self._model_providers.append([
#                    ppath,
#                    pprops['slug'],
#                    pprops['name'],
#                    self._get_pixbuf_from_filename(u'provider_%s.png' % pprops['slug'], 24, 24)])
#
#    def _prepare_treeview_statuses(self):
#        self._treeview_statuses = self._builder.get_object(u'treeview_statuses')
#        self._col_statuses_message = self._builder.get_object(u'col_statuses_message')
#        self._cr_statuses_message = self._builder.get_object(u'cr_statuses_message')
#        self._cr_statuses_message.set_property('wrap-mode', pango.WRAP_WORD_CHAR)
#        self._cr_statuses_message.set_property('single-paragraph-mode', True)
#        self._cr_statuses_message.set_property('yalign', 0.0)
#
#    def _prepare_win_main(self):
#        self._win_main = self._builder.get_object(u'win_main')
#        self._entry_message = self._builder.get_object(u'entry_message')
#        self._btn_send = self._builder.get_object(u'btn_send')
#        self._img_btn_send = self._builder.get_object(u'img_btn_send')
#
#    def _prepare_combo_accounts(self):
#        self._combo_accounts = self._builder.get_object(u'combo_accounts')
#        self._combo_accounts.set_active(0)
#
#    def _preload_images(self):
#        working_imgs = glob.glob(os.path.join(SAYWAH_GUI_RESOURCES_PATH, 'working-*.png'))
#        for fn in working_imgs:
#            self._get_pixbuf_from_filename(fn, 24, 24)
#        self._n_working_frames = len(working_imgs)
#
#    def _get_pixbuf_from_filename(self, fname, width, height):
#        if not hasattr(self, '_pixbuf_cache'):
#            self._pixbuf_cache = {}
#        key = (fname, width, height)
#        if not key in self._pixbuf_cache:
#            fname = os.path.join(SAYWAH_GUI_RESOURCES_PATH, fname)
#            if not os.path.isfile(fname):
#                pixbuf = None
#            else:
#                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(fname, width, height)
#            self._pixbuf_cache[key] = pixbuf
#        return self._pixbuf_cache[key]
#
#    def _show_dlg_account_add(self):
#        self._reload_model_providers()
#        combo_providers = self._builder.get_object('combo_providers')
#        combo_providers.set_active(0)
#        combo_providers.grab_focus()
#        entry_username = self._builder.get_object('entry_username')
#        entry_username.set_text('')
#        entry_password = self._builder.get_object('entry_password')
#        entry_password.set_text('')
#        dlg_account_add = self._builder.get_object('dlg_account_add')
#        response = dlg_account_add.run()
#        if response == gtk.RESPONSE_OK:
#            iprovider = combo_providers.get_active_iter()
#            provider_slug = self._model_providers.get_value(iprovider, 1)
#            username = entry_username.get_text().decode('utf8')
#            password = entry_password.get_text().decode('utf8')
#            accounts = DBUS_CONNECTION.get_object('org.saywah.Saywah', '/org/saywah/Saywah/accounts')
#            apath = accounts.AddAccount(provider_slug, username, dbus_interface='org.saywah.Accounts')
#            account = DBUS_CONNECTION.get_object('org.saywah.Saywah', apath)
#            account.Set('', 'password', password, dbus_interface='org.freedesktop.DBus.Properties')
#            accounts.StoreAccounts(dbus_interface='org.saywah.Accounts')
#            uuid = account.Get('', 'uuid', dbus_interface='org.freedesktop.DBus.Properties')
#            log.info(u"Added %s account %s [uuid:%s]" % (provider_slug, username, uuid))
#            self._reload_model_accounts()
#        dlg_account_add.hide()
#
#
#    # GObject event handlers
#
#    def on_quit(self, widget):
#        mainloop.quit()
#
#    def on_menu_accounts_add_activate(self, widget):
#        self._show_dlg_account_add()
#
#    def on_treeview_statuses_size_allocate(self, widget, allocation):
#        self._cr_statuses_message.set_property('wrap-width', self._col_statuses_message.get_width() - 5)
#
#    def on_btn_send_clicked(self, widget):
#        iaccount = self._combo_accounts.get_active_iter()
#        apath = self._model_accounts.get_value(iaccount, 0)
#        account = DBUS_CONNECTION.get_object('org.saywah.Saywah', apath)
#        message = self._entry_message.get_text().decode('utf8')
#
#        def update_message_waiting():
#            if self._sending_message:
#                if not hasattr(self, '_img_btn_next_frame'): # first time in this loop
#                    self._btn_send.set_sensitive(False)
#                    self._img_btn_send_orig_stock = self._img_btn_send.get_stock()
#                    self._img_btn_next_frame = 0
#                if self._img_btn_next_frame == self._n_working_frames - 1:
#                    self._img_btn_next_frame = 0
#                img_path = os.path.join(SAYWAH_GUI_RESOURCES_PATH, 'working-%02d.png' % self._img_btn_next_frame)
#                self._img_btn_send.set_from_pixbuf(self._get_pixbuf_from_filename(img_path, 24, 24))
#                self._img_btn_next_frame += 1
#                return True
#            else:
#                self._img_btn_send.set_from_stock(*self._img_btn_send_orig_stock)
#                self._btn_send.set_sensitive(True)
#                del self._img_btn_next_frame
#                del self._img_btn_send_orig_stock
#                return False
#
#        def on_send_message_success():
#            self._sending_message = False
#
#        def on_send_message_error(error):
#            self._sending_message = False
#            raise TODO
#
#        self._sending_message = True
#        account.SendMessage(message, dbus_interface='org.saywah.Account',
#                            reply_handler=on_send_message_success,
#                            error_handler=on_send_message_error)
#        log.info(u"Sending message: %s" % message)
#        gobject.timeout_add(50, update_message_waiting)


def run():
    saywah_gtk = SaywahGTK()
    return mainloop.run()
