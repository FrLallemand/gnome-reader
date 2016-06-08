#!C:\Python27\python.exe
# -*- encoding: utf-8 -*-

import sys
import os
import mimetypes
from define import App
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib


class SettingsMenu(Gtk.PopoverMenu):
    def __init__(self, adjustment = None):
        Gtk.PopoverMenu.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_resource("/org/gnome/gnome_reader/settings_menu.ui")
        #Gio.Application.get_default
        builder.connect_signals(self)
        self.scale = builder.get_object("zoom_level_scale")
        self._meta_data_display_button = builder.get_object("meta_data_display_button")
        self.add(builder.get_object("popover_box"))

        if adjustment is not None:
            self.set_adjustment(adjustment)

    def _on_scale_value_changed(self, widget):
        App().window.viewer.add_zoom(widget.get_value())

    def set_adjustment(self, adjustment):
        self.scale.set_adjustment(adjustment)

    def set_meta_data_button_sensitive(self, state):
        self._meta_data_display_button.set_sensitive(state)
