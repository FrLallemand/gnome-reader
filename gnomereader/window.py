#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import mimetypes
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, Gio, GLib, Gdk
from gnomereader.toolbar import ToolBar
from gnomereader.viewer import Viewer
from gnomereader.meta_data_view import MetaDataView


class Window(Gtk.ApplicationWindow):
    """
    Application window.

    Handle the window and the views
    """

    def __init__(self, app):
        """
        AppWindow constructor.

        Init AppWindow
        """
        Gtk.ApplicationWindow.__init__(self,
                                       application=app,
                                       title="Reader")
        self.settings = Gtk.Settings().get_default()
        self.set_size_request(400, 600)
        self.set_resizable(True)
        self.set_border_width(1)
        self.connect("key-press-event", self._on_keypress)
        self._create_actions()
        self._setup_view()

    def _on_keypress(self, widget, data):
        if self.stack.get_visible_child_name() == "main_view":
            if Gdk.keyval_name(data.keyval) == "Left":
                self.viewer.go_previous_page()
            if Gdk.keyval_name(data.keyval) == "Right":
                self.viewer.go_next_page()
        else:
            if Gdk.keyval_name(data.keyval) == "Escape":
                self.stack.set_visible_child_name("main_view")
                self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

    def _setup_view(self):
        self.toolbar = ToolBar()
        self.toolbar.connect("chapter-selected", self._select_chapter)
        self.toolbar.connect("zoom-level-changed", self._adjust_zoom_level)

        self.viewer = Viewer(self)
        self.viewer.connect("file-opened", self._on_file_opened)
        self.viewer.connect("page-changed", self._on_page_changed)
        self.viewer.load_page()

        self.meta_data_view = MetaDataView()

        self.set_titlebar(self.toolbar.header_bar)

        scrolled_viewer = Gtk.ScrolledWindow()
        scrolled_viewer.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_viewer.set_overlay_scrolling(True)
        scrolled_viewer.add(self.viewer.web_view)

        scrolled_meta_data = Gtk.ScrolledWindow()
        scrolled_meta_data.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_meta_data.set_overlay_scrolling(True)
        scrolled_meta_data.add(self.meta_data_view.grid)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.stack.set_transition_duration(350)
        self.stack.add_named(scrolled_viewer, "main_view")
        self.stack.add_named(scrolled_meta_data, "meta_data_view")
        self.add(self.stack)

        self.show_all()

    def _create_actions(self):
        open_epub = Gio.SimpleAction.new("open-epub", None)
        open_epub.connect("activate", self._open_epub)
        self.add_action(open_epub)

        chapter_selected = Gio.SimpleAction.new('select-chapter',
                                                GLib.VariantType("i"))
        chapter_selected.connect('activate', self._select_chapter)
        self.add_action(chapter_selected)

        go_next = Gio.SimpleAction.new('go-next', None)
        go_next.connect('activate', self._go_next)
        self.add_action(go_next)

        go_previous = Gio.SimpleAction.new('go-previous', None)
        go_previous.connect('activate', self._go_previous)
        self.add_action(go_previous)

        toggle_night_mode = Gio.SimpleAction.new_stateful("toggle-night-mode",
                                                          None,
                                                          GLib.Variant.new_boolean(False))
        toggle_night_mode.connect("change-state", self._toggle_night_mode)
        self.add_action(toggle_night_mode)

        display_meta_data = Gio.SimpleAction.new("display_meta_data", None)
        display_meta_data.connect("activate", self._display_meta_data)
        self.add_action(display_meta_data)

        view_zoom = Gio.SimpleAction.new("zoom-in", None)
        view_zoom.connect("activate", self._zoom_in)
        self.add_action(view_zoom)

        view_dezoom = Gio.SimpleAction.new("zoom-out", None)
        view_dezoom.connect("activate", self._zoom_out)
        self.add_action(view_dezoom)

    def _adjust_zoom_level(self, widget, user_data):
        self.viewer.add_zoom(user_data)

    def _zoom_in(self, action, state):
        self.toolbar.adjustment.set_value(self.toolbar.adjustment.get_value() +
                                          self.toolbar.adjustment.get_minimum_increment())

    def _zoom_out(self, action, state):
        self.toolbar.adjustment.set_value(self.toolbar.adjustment.get_value() -
                                          self.toolbar.adjustment.get_minimum_increment())

    def _select_chapter(self, widget, user_data):
        self.viewer.go_page(user_data)

    def _toggle_night_mode(self, action, state):
        action.set_state(state)
        self.settings.set_property("gtk-application-prefer-dark-theme", state)
        self.viewer.set_night_mode(state)

    def _display_meta_data(self, action, state):
        if self.stack.get_visible_child_name() == "main_view":
            self.stack.set_visible_child_name("meta_data_view")
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        else:
            self.stack.set_visible_child_name("main_view")
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

    def _on_file_opened(self, widget):
        self.toolbar.populate_chapters_menu(self.viewer.epub.chapters)

    def _on_page_changed(self, widget):
        if self.viewer.epub.is_loaded():
            self.set_focus(self.viewer.web_view)
            self.toolbar.set_title(self.viewer.epub.name,
                                   self.viewer.epub.chapters[self.viewer.position].title)
            if self.viewer.position == self.viewer.last_page:
                self.lookup_action("go-next").set_enabled(False)
            else:
                self.lookup_action("go-next").set_enabled(True)

            if self.viewer.position == self.viewer.first_page:
                self.lookup_action("go-previous").set_enabled(False)
            else:
                self.lookup_action("go-previous").set_enabled(True)

            self.toolbar.enable_chapters_button(True)
            self.lookup_action("display_meta_data").set_enabled(True)
        else:
            self.toolbar.enable_chapters_button(False)
            self.lookup_action("display_meta_data").set_enabled(False)
            self.lookup_action("go-next").set_enabled(False)
            self.lookup_action("go-previous").set_enabled(False)

    def _go_next(self, action, parameter):
        self.viewer.go_next_page()

    def _go_previous(self, action, parameter):
        self.viewer.go_previous_page()

    def _open_epub(self, action, state):
        dialog = Gtk.FileChooserDialog("Choisissez un fichier",
                                       self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        # If mime types for epub doesn't exist, adds it
        if ".epub" not in mimetypes.types_map.keys():
            mimetypes.add_type("application/epub+zip", ".epub")

        filter_epub = Gtk.FileFilter()
        filter_epub.set_name("Epub")
        if os.name == "nt":
            filter_epub.add_pattern("*.epub")
        else:
            filter_epub.add_mime_type("application/epub+zip")

        dialog.set_filter(filter_epub)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.viewer.open(dialog.get_filename())
        dialog.destroy()
