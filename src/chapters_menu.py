#!C:\Python27\python.exe
# -*- encoding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
from define import App

class ChaptersMenu(Gtk.PopoverMenu):
    """
    Handle the popover Menu
    """

    def __init__(self):
        Gtk.PopoverMenu.__init__(self)
        builder = Gtk.Builder()
        builder.add_from_resource("/org/gnome/gnome_reader/chapters_menu.ui")
        self.chapters_box = builder.get_object("chapters_box")
        self.add(self.chapters_box)

    def add_menu_item(self, text, action):
        button = Gtk.ModelButton(text=text, action_name=action)
        button.set_visible(True)
        self.chapters_box.add(button)

    def populate(self):
        def on_chapter_selected(action, user_data, chapter_pos):
            App().window.viewer.jump_to_page(chapter_pos)
            App().window.update()

        for i in range(0, len(App().epub.chapters) - 1):
            chapter = App().epub.chapters[i]
            if chapter.title is not None:
                chapter_selected = Gio.SimpleAction(name='chapter-selected' + chapter.id)
                chapter_selected.connect('activate', on_chapter_selected, i)
                App().window.add_action(chapter_selected)
                self.add_menu_item(chapter.title, 'win.chapter-selected' + chapter.id)
