#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, GObject


class MetaDataView(GObject.GObject):

    def __init__(self):
        GObject.GObject.__init__(self)
        self._ui = Gtk.Builder()
        self._ui.add_from_resource("/org/gnome/Reader/meta_data_view.ui")
        self._description = self._ui.get_object("description_text")
        self.grid = self._ui.get_object("meta_data_grid")
        self._author_box = self._ui.get_object("author_box")
