#!C:\Python27\python.exe
# -*- encoding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Notify', '0.7')
# gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, Gio, GLib, WebKit, Gdk
from epub import Epub
import sys
import os
if(sys.version_info >= (3,0)):
    from urllib.parse import quote
else:
    from urllib import quote


class Viewer(WebKit.WebView):
    def __init__(self):
        WebKit.WebView.__init__(self)
        self.epub = None
        self.position = 0
        self.first_page=0
        self.last_page=0

    def set_epub(self, epub):
        self.epub = epub
        self.first_page=0
        self.last_page=len(self.epub.chapters)-1
    
    def go_next_page(self):
        if self.position<self.last_page:
            self.position += 1
            self.load_page()

    def go_previous_page(self):
        if self.position>self.first_page:
            self.position -= 1
            self.load_page()

    def go_first_page(self):
        self.position = self.first_page
        self.load_page()

    def go_last_page(self):
        self.position = self.last_page
        self.load_page()
            
    def jump_to_page(self, pos):
        if pos<len(self.epub.chapters) and pos>=0:
            self.position = pos
            self.load_page()

    def set_night_mode(self, state):
        settings = self.get_settings()
        night_css = "file://"+quote(os.getcwd()+"/data/night_mode.css")
        if os.name == "nt":
            night_css = "file://"+quote(os.getcwd().replace("\\", "/")+"/data/night_mode.css")
        if state:
            settings.props.user_stylesheet_uri = night_css
        else:
            settings.props.user_stylesheet_uri = ""
        self.reload()

    def add_zoom(self, value):
        if value >= 0:
            self.props.zoom_level = 1.0 + ((value/10)*2)
        else:
            self.props.zoom_level = 1.0 + value/10
        
        

    def load_page(self):
        if self.epub is not None:
            if os.name == "nt":
                self.load_uri("file:///"+self.epub.chapters[self.position].href)
            else:
                self.load_uri("file://"+self.epub.chapters[self.position].href)
        else:
            self.load_uri("about:blank")
        