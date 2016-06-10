#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, Gio, GLib, Gdk
from gnomereader.window import Window

class Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id='org.gnome.Reader',
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name('Reader')
        GLib.set_prgname('gnome-reader')

        # TODO : create config schema
        #self.settings = Gio.Settings.new('org.gnome.Reader')

        self._window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.set_accels_for_action("win.zoom-in", ["<Control>plus"])
        self.set_accels_for_action("win.zoom-out", ["<Control>minus"])
        self.set_accels_for_action("win.open-epub", ["<Control>o"])

        self.build_app_menu()

    def do_activate(self):
        if not self._window:
            self._window = Window(self)
        self._window.present()

    def build_app_menu(self):
        action_entries = [
            ('about', self.about),
            ('help', self.help),
            ('quit', self.quit),
        ]
        for action, callback in action_entries:
            action = Gio.SimpleAction.new(action, None)
            action.connect("activate", callback)
            self.add_action(action)

    def about(self, action, param):
        about_dialog = Gtk.AboutDialog(authors=["François Lallemand", "Quentin Ladeveze"],
                                       copyright="EMPTYYYYYYY",
                                       program_name="Gnome-reader",
                                       version="0.0.3",
                                       license="GPL v3",
                                       license_type=Gtk.License.GPL_3_0,
                                       transient_for=self._window,
                                       modal=True)
        about_dialog.present()

    def help(self, action, param):
        pass

    def quit(self, action, param):
        self._window.destroy()
