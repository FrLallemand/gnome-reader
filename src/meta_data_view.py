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

class MetaDataView():
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_resource("/org/gnome/gnome_reader/meta_data_view.ui")
        self.description = self.builder.get_object("description_text")
        self.grid = self.builder.get_object("meta_data_grid")
        self.author_box = self.builder.get_object("author_box")
