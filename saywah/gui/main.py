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


def osd_notify(title, body, icon_data=""):
    n = DBUS_CONNECTION.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
    return n.Notify(u"Saywah", 0, icon_data, title, body, '', {}, -1,
                    dbus_interface='org.freedesktop.Notifications')


class SaywahGTK(object):
    def __init__(self):
        self._builder = gtk.Builder()
        self._builder.add_from_file(SAYWAH_GTKUI_XML_PATH)
        self._builder.connect_signals(self)

        self._loaded_providers = set()
        self._loaded_accounts = set()

        self.reload_model_providers()
        self.reload_model_accounts()

        win_main = self._builder.get_object(u'win_main')
        win_main.show_all()

    def _on_dbus_MessageArrived(self, message):
        osd_notify(unicode(message['sender_nick']), unicode(message['text']))

    def reload_model_accounts(self):
        m = self._builder.get_object('model_accounts')
        m.clear()
        self.reload_model_providers()
        for ppath in self._loaded_providers:
            provider = get_saywah_dbus_object(ppath)
            pprops = provider.GetAll('', dbus_interface='org.freedesktop.DBus.Properties')
            for apath in provider.GetAccounts(dbus_interface='org.saywah.Provider'):
                if not apath in self._loaded_accounts:
                    account = get_saywah_dbus_object(apath)
                    aprops = account.GetAll('', dbus_interface='org.freedesktop.DBus.Properties')
                    m.append([apath, ppath, aprops['username'], aprops['uuid'], pprops['name'], pprops['slug'],
                              get_pixbuf_from_filename(u'provider_%s.png' % pprops['slug'], 24, 24)])
                    account.connect_to_signal('MessageArrived', self._on_dbus_MessageArrived,
                                               dbus_interface='org.saywah.Account')
                    account.EnableMessageFetching(True, dbus_interface='org.saywah.Account')
                    self._loaded_accounts.add(apath)

    def reload_model_providers(self):
        m = self._builder.get_object(u'model_providers')
        m.clear()
        providers = get_saywah_dbus_object('/org/saywah/Saywah/providers')
        for ppath in providers.GetProviders(dbus_interface='org.saywah.Providers'):
            if not ppath in self._loaded_providers:
                provider = get_saywah_dbus_object(ppath)
                pprops = provider.GetAll(u'', dbus_interface='org.freedesktop.DBus.Properties')
                m.append([ppath, pprops['slug'], pprops['name'],
                          get_pixbuf_from_filename(u'provider_%s.png' % pprops['slug'], 24, 24)])
                self._loaded_providers.add(ppath)

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


def run():
    saywah_gtk = SaywahGTK()
    return mainloop.run()
