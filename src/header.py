#!C:\Python27\python.exe
# -*- encoding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Notify', '0.7')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, Gio, GLib, WebKit, Gdk
from epub import Epub
from viewer import Viewer
import sys
import os

class Header(Gtk.HeaderBar):
    def __init__(self):
        Gtk.HeaderBar.__init__(self)
        self.title = "Lecteur d'epub"
        self.props.show_close_button = True
        self._open_button = Gtk.Button()
        self._open_button.set_label("Ouvrir")
        self.pack_start(self._open_button)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.get_style_context().add_class(Gtk.STYLE_CLASS_LINKED)
        self._previous_button = Gtk.Button()
        self._previous_button.set_image(Gtk.Image.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON))
        self._previous_button.set_sensitive(False)
        box.add(self._previous_button)

        self._next_button = Gtk.Button()
        self._next_button.set_image(Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON))
        self._next_button.set_sensitive(False)
        box.add(self._next_button)

        self.pack_start(box)

        self._menu_button = Gtk.MenuButton()
        self._menu_button.set_image(Gtk.Image.new_from_icon_name("open-menu-symbolic", Gtk.IconSize.MENU))
        self.pack_end(self._menu_button)
        
        self._chapters_button = Gtk.Button()
        self._chapters_button.set_label("Chapitres")
        self._chapters_button.set_sensitive(False)
        self.pack_end(self._chapters_button)
