# gnome-reader 

An epub reader for gnome, using gnome technologies and gtk

Currently in development.

## TODO
* A makefile
* Port to WebKit2 instead of WebKit
* Make a bookmarks system
* Allow to modify and save meta data of an epub
* Find something to display when no epub is selected, instead of "about:blank"
* A fallback solution when the navmap isn't correctly formed in the epub (to display chapters anyway)

## Done
* Extract an epub file and display it
* Use a cache directory
* Add an "Open" button, and shortcut
* Show a list of chapters in epub, allow navigation (with gui and shortcuts)
* Allow to zoom in and out
* Add "About" dialog


## In progress
* Allow to set a night theme (does not alway work currently)
* Use xml, builder and gresources when possible
* Correctly fragment code in easily maintainable files
* Display meta data for the currently open epub

### Ideas
* Allow two disposition : one with scrolled window, one with each chapter separated in pages with the size of the window
* Put navigation button in overlay
* Handle the creation of collections, for epub
* get the list of epub on the user directory with tracker