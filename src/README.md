# Source files

You either edit the .glyphs file OR you edit the UFO files.
Any edits to the .glyphs file will overwrite changes to UFO files,
but not vice versa.

`Inter-UI.glyphs` is the main combined master file.
Editing this and running `make` patches and potentially overwrites changes to
the UFO files and replaces `Inter-UI.desigspace`.

`Inter-UI.desigspace` and `Inter-UI*.ufo` are generated from the .glyphs file
but can be edited themselves. For instance, if you fork this project and
prefer to work with UFOs, you can do that and simply ignore the .glyphs file.

