#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import gi
import sys
if(sys.version_info >= (3,0)):
    from urllib.parse import quote
else:
    from urllib import quote
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import GObject, WebKit
from gnomereader.epub import Epub


class Viewer(GObject.GObject):

    __gsignals__ = {
        'file-opened': (GObject.SignalFlags.RUN_FIRST,
                        None,
                        ()),
        'page-changed': (GObject.SignalFlags.RUN_FIRST,
                         None,
                         ()),
    }

    def __init__(self, parent_window):
        GObject.GObject.__init__(self)
        self._window = parent_window
        self.position = 0
        self._setup_view()
        self.epub = Epub()
        self.first_page = 0
        self.last_page = 0

    def _setup_view(self):
        self.web_view = WebKit.WebView()

    def open(self, file):
        self.epub.set_file_path(file)
        self.epub.extract()
        self.epub.prepare()
        self.last_page = len(self.epub.chapters) - 1
        self.emit("file-opened")
        self.go_first_page()

    def go_first_page(self):
        self.position = 0
        self.load_page()

    def go_last_page(self):
        self.position = self.last_page
        self.load_page()

    def go_page(self, value):
        self.position = value
        self.load_page()

    def go_next_page(self):
        if self.position < self.last_page:
            self.position += 1
            self.load_page()

    def go_previous_page(self):
        if self.position > self.first_page:
            self.position -= 1
            self.load_page()

    def add_zoom(self, value):
        if value >= 0:
            self.web_view.props.zoom_level = 1.0 + ((value/10.0)*2)
        else:
            self.web_view.props.zoom_level = 1.0 + value/10.0

    def set_night_mode(self, state):
        settings = self.web_view.get_settings()
        night_css = "file://"+quote(os.getcwd()+"/data/night_mode.css")
        if os.name == "nt":
            night_css = "file://"+quote(os.getcwd().replace("\\", "/")+"/data/night_mode.css")
        if state:
            settings.props.user_stylesheet_uri = night_css
        else:
            settings.props.user_stylesheet_uri = ""
        self.web_view.reload()

    def load_page(self):
        if self.epub.is_loaded():
            if os.name == "nt":
                self.web_view.load_uri("file:///"+self.epub.chapters[self.position].href)
            else:
                self.web_view.load_uri("file://"+self.epub.chapters[self.position].href)
        else:
            self.web_view.load_uri("about:blank")

        self.emit("page-changed")
