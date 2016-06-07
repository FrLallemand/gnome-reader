#!C:\Python27\python.exe
# -*- encoding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Notify', '0.7')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, Gio, GLib, WebKit, Gdk
from epub import Epub
from viewer import Viewer
from header import Header
from define import App
import sys
import os
import platform
import mimetypes

class AppWindow(Gtk.ApplicationWindow):

    def __init__(self, app, title):
        #super(Gtk.ApplicationWindow, self).__init__(*args, **kwargs)
        Gtk.ApplicationWindow.__init__(self, application=app, title=title)
        base_path = os.path.abspath(os.path.dirname(__file__))
        resource = Gio.resource_load(base_path + "/../data/gnome_reader.gresource")
        Gio.resources_register(resource)
        self.builder = Gtk.Builder()

        self.set_default_size(400, 600)
        self.set_resizable(True)
        self.set_border_width(0)

        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)


        self.settings = Gtk.Settings().get_default()
        self.builder.add_from_resource("/org/gnome/gnome_reader/header_bar.ui")

        self.header = self.builder.get_object("header_bar")
        self.menu_button = self.builder.get_object("menu_button")
        self.open_epub_button = self.builder.get_object("open_epub_button")
        self.navigation_previous_button = self.builder.get_object("navigation_previous_button")
        self.navigation_next_button = self.builder.get_object("navigation_next_button")
        self.chapters_button = self.builder.get_object("chapters_button")

        self._create_actions()
        self.connect("key-press-event", self.on_keypress)

        self.set_titlebar(self.header)

        self.viewer = Viewer()
        self.viewer.load_page()

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_overlay_scrolling(True)
        scrolled.add(self.viewer)



        self.builder.add_from_resource("/org/gnome/gnome_reader/meta_data_view.ui")

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
        self.stack.set_transition_duration(350)
        self.stack.add_named(scrolled, "main_view")
        self.stack.add_named(self.builder.get_object("meta_data_grid"), "meta_data_view")
        self.add(self.stack)

        #Maybe add navigation button in overlay, in a future version ?
        #overlay = Gtk.Overlay()
        #overlay.add(scrolled)
        #self.add(overlay)
        #overlay.add_overlay(self.revealer)

        if self.settings.get_property("gtk-application-prefer-dark-theme"):
            self.viewer.set_night_mode(True)

        self.builder.add_from_resource("/org/gnome/gnome_reader/popover_menu.ui")
        popover = self.builder.get_object("popover_menu")
        self.menu_button.set_popover(popover)
        self.scale = self.builder.get_object("zoom_level_scale")
        self.scale.connect("value-changed", self._on_scale_value_changed)
        self.adjustment = self.builder.get_object("zoom_adjustment")
        self.meta_data_display_button = self.builder.get_object("meta_data_display_button")

        self.builder.add_from_resource("/org/gnome/gnome_reader/chapters_menu.ui")
        self.chapters_menu = self.builder.get_object("chapters_menu")
        self.chapters_box = self.builder.get_object("chapters_box")
        self.chapters_button.set_popover(self.chapters_menu)

        self.update()

        self.show_all()

    def _create_actions(self):
        open_epub = Gio.SimpleAction.new("open_epub", None)
        open_epub.connect("activate", self._open_epub)
        self.add_action(open_epub)

        go_previous_or_next = Gio.SimpleAction.new("go_previous_or_next", GLib.VariantType.new('s'))
        go_previous_or_next.connect("activate", self.go_previous_or_next)
        self.add_action(go_previous_or_next)

        go_chapter = Gio.SimpleAction.new("go_previous_or_next", GLib.VariantType.new('s'))
        go_chapter.connect("activate", self.go_previous_or_next)
        self.add_action(go_chapter)

        toggle_night_mode = Gio.SimpleAction.new_stateful("toggle_night_mode", None, GLib.Variant.new_boolean(False))
        toggle_night_mode.connect("change-state", self._toggle_night_mode)
        self.add_action(toggle_night_mode)

        view_zoom = Gio.SimpleAction.new("view_zoom", None)
        view_zoom.connect("activate", self._view_zoom)
        self.add_action(view_zoom)

        view_dezoom = Gio.SimpleAction.new("view_dezoom", None)
        view_dezoom.connect("activate", self._view_dezoom)
        self.add_action(view_dezoom)

        display_meta_data = Gio.SimpleAction.new("display_meta_data", None)
        display_meta_data.connect("activate", self._display_meta_data)
        self.add_action(display_meta_data)

    def _display_meta_data(self, action, state):
        if self.stack.get_visible_child_name() == "main_view":
            self.change_view("meta_data_view")
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
        else:
            self.change_view("main_view")
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)

    def change_view(self, name):
        self.stack.set_visible_child_name(name)


    def _toggle_night_mode(self, action, state):
        action.set_state(state)
        self.settings.set_property("gtk-application-prefer-dark-theme", state)
        self.viewer.set_night_mode(state)

    def _populate_chapters_menu(self):
        def on_chapter_selected(action, user_data, chapter_pos):
            self.viewer_jump(chapter_pos)
        for i in range(0, len(App().epub.chapters)-1):
            chapter = App().epub.chapters[i]
            if chapter.title is not None:
                chapter_selected = Gio.SimpleAction(name='chapter-selected'+chapter.id)
                chapter_selected.connect('activate', on_chapter_selected, i)
                self.add_action(chapter_selected)
                button = Gtk.ModelButton(text=chapter.title, action_name='win.chapter-selected'+chapter.id)
                button.set_visible(True)
                self.chapters_box.add(button)

    def _view_zoom(self, action, state):
        self.adjustment.set_value(self.adjustment.get_value()+self.adjustment.get_minimum_increment())
        self.viewer.add_zoom(self.adjustment.get_value())

    def _view_dezoom(self, action, state):
        self.adjustment.set_value(self.adjustment.get_value()-self.adjustment.get_minimum_increment())
        self.viewer.add_zoom(self.adjustment.get_value())

    def  _on_scale_value_changed(self, widget):
        self.viewer.add_zoom(widget.get_value())

    def _open_epub(self, action, state):
        dialog = Gtk.FileChooserDialog("Choisissez un fichier",
                                       self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        #If mime types for epub doesn't exist, adds it
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
            App().epub.set_file_path(dialog.get_filename())
            App().epub.extract()
            App().epub.prepare()
            self.viewer.setup_view()
            self.viewer_navigate("start")
            self._populate_chapters_menu()
        dialog.destroy()

    def update(self):
        if App().epub.is_loaded():
            title = App().epub.chapters[self.viewer.position].title
            if title is None:
                title = ""
            self.set_focus(self.viewer)
            titlebar = self.get_titlebar()
            titlebar.set_title(App().epub.name)
            titlebar.set_subtitle(title)
            if self.viewer.position == self.viewer.last_page:
                self.navigation_next_button.set_sensitive(False)
            else:
                self.navigation_next_button.set_sensitive(True)

            if self.viewer.position == self.viewer.first_page:
                self.navigation_previous_button.set_sensitive(False)
            else:
                self.navigation_previous_button.set_sensitive(True)

            self.chapters_button.set_sensitive(True)
            self.meta_data_display_button.set_sensitive(True)

        else:
            self.chapters_button.set_sensitive(False)
            self.navigation_previous_button.set_sensitive(False)
            self.navigation_next_button.set_sensitive(False)
            self.meta_data_display_button.set_sensitive(False)

        #titlebar._chapters_button.set_sensitive(True)

    def viewer_navigate(self, code):
        if code == "next":
            self.viewer.go_next_page()
        if code == "previous":
            self.viewer.go_previous_page()
        if code == "start":
            self.viewer.go_first_page()
        if code == "last":
            self.viewer.go_last_page()
        self.update()

    def viewer_jump(self, page_number):
        self.viewer.jump_to_page(page_number)
        self.update()

    def go_previous_or_next(self, action, parameter):
        self.viewer_navigate(parameter.get_string())

    def on_keypress(self, widget, data):
        keyval = ""
        if self.stack.get_visible_child_name() == "main_view":
            if Gdk.keyval_name(data.keyval) == "Left":
                keyval = "previous"
            if Gdk.keyval_name(data.keyval) == "Right":
                keyval = "next"

            self.viewer_navigate(keyval)
        else:
            if Gdk.keyval_name(data.keyval) == "Escape":
                self.change_view("main_view")

class Application(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self,
                                application_id='org.gnome.gnome-reader',
                                flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.window = None
        self.epub = None
        GLib.set_application_name('gnome-reader')
        GLib.set_prgname('gnome-reader')

        self.register(None)
        if self.get_is_remote():
            Gdk.notify_startup_complete()


    def do_startup(self):
        Gtk.Application.do_startup(self)

        menu = Gio.Menu()

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)
        menu.append("About", 'app.about')

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        menu.append("Quit", 'app.quit')

        self.set_accels_for_action("win.view_zoom", ["<Control>plus"])
        self.set_accels_for_action("win.view_dezoom", ["<Control>minus"])
        self.set_accels_for_action("win.open_epub", ["<Control>o"])

        self.set_app_menu(menu)

        self.epub = Epub()

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(self, "Main Window")
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()

        if options.contains("test"):
            # This is printed on the main instance
            print("Test argument recieved")

        self.activate()
        return 0


    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(authors=["François Lallemand", "Quentin Ladeveze"],
                                       copyright="EMPTYYYYYYY",
                                       program_name="Gnome-reader",
                                       version="0.0.3",
                                       license="GPL v3",
                                       license_type=Gtk.License.GPL_3_0,
                                       transient_for=self.window,
                                       modal=True)
        about_dialog.present()


    def on_quit(self, action, param):
        self.quit()


if __name__ == "__main__":
    appli = Application()
    appli.run(sys.argv)
