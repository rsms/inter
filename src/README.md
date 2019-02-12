# Source files

The main source file is `Inter.glyphs`, but you can easily generate
UFOs and work with those instead, if you're using a font editor that does
not support .glyphs files.

For more details on how to work with these source files and how to build
font files from them, see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Generating designspace and UFO files

```
make designspace
```

This will generate all masters as UFO files in this (`src`) directory as well
as accompanying designspace files.

You can now forget about the .glyphs file and simply work with the UFO and
designspace files, and keep building using `make`.

Note that UFO and designspace files are automatically generated as part of
the build process, so in practice you can simply run `make` and those files
will be generated for you.

