# OpenType features

This directory contains most (but not all) OpenType feature code.

- Some features are maintained by the Glyphs application and are stored in the .glyphs file.
- The order of features are defined in the .glyphs file

Each feature file in this directory is automatically wrapped in a `feature {...}` block.
For example, `cv07.fea` contains the following code:

```fea
sub germandbls by germandbls.1;
```

And when the font is compiled, it actually becomes:

```
feature cv07 {
  sub germandbls by germandbls.1;
}
```
