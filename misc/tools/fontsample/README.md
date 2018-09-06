# fontsample

A macOS-specific program for generating a PDF with text sample of a
specific font file.

```
$ make
$ ./fontsample -h
usage: ./fontsample [options] <fontfile>

options:
  -h, -help         Show usage and exit.
  -z, -size <size>  Font size to render. Defaults to 96.
  -t, -text <text>  Text line to render. Defaults to "Rags78 **A**".
  -o <file>         Write output to <file> instead of default filename.
                    Defaults to <fontfile>.pdf. If the provided filename
                    ends with ".png" a PNG is written instead of a PDF.

<fontfile>
  Any font file that macOS can read.
```
