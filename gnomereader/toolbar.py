#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from gi.repository import Gtk, GObject, Gio, GLib

class ToolBar(GObject.GObject):

    __gsignals__ = {
            'chapter-selected': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_INT, )),
            'zoom-level-changed': (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_INT, )),
        }

    def __init__(self):
        GObject.GObject.__init__(self)
        self._setup_view()

    def _setup_view(self):
        self._ui = Gtk.Builder()
        self._ui.add_from_resource('/org/gnome/Reader/header_bar.ui')
        self.header_bar = self._ui.get_object("header_bar")
        self._open_epub_button = self._ui.get_object("open_epub_button")
        self._navigation_previous_button = self._ui.get_object("navigation_previous_button")
        self._navigation_next_button = self._ui.get_object("navigation_next_button")
        self._settings_button = self._ui.get_object("settings_button")
        self._chapters_button = self._ui.get_object("chapters_button")
        self._window = self.header_bar.get_parent()

        self._ui.add_from_resource('/org/gnome/Reader/chapters_menu.ui')
        self._chapters_popover = self._ui.get_object("chapters_popover")
        self._chapters_box = self._ui.get_object("chapters_box")

        self._ui.add_from_resource('/org/gnome/Reader/settings_menu.ui')
        self.adjustment = self._ui.get_object("zoom_adjustment")
        self._settings_popover = self._ui.get_object("settings_popover")
        self._meta_data_display_button = self._ui.get_object("meta_data_display_button")
        self.adjustment.connect("value-changed", self._emit_zoom_level_changed)

        self._chapters_button.set_popover(self._chapters_popover)
        self._settings_button.set_popover(self._settings_popover)
        self.set_title()

    def set_title(self, title="Reader", subtitle=None):
        self.header_bar.set_title(title)
        self.header_bar.set_subtitle(subtitle)

    def enable_chapters_button(self, state):
        self._chapters_button.set_sensitive(state)

    def enable_settings_button(self, state):
        self._settings_button.set_sensitive(state)

    def populate_chapters_menu(self, chapters_list):
        for i in range(0, len(chapters_list)):
            chapter = chapters_list[i]
            if chapter.title is not None:
                button = Gtk.ModelButton(text=chapter.title)
                button.set_visible(True)
                button.connect("clicked", self._emit_chapter_selected, i)
                self._chapters_box.add(button)

    def _emit_chapter_selected(self, widget, i):
        self.emit('chapter-selected', i)

    def _emit_zoom_level_changed(self, widget):
        self.emit('zoom-level-changed', self.adjustment.get_value())
