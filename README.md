# Interface

Interface is a typeface specially designed for user interfaces, with excellent ligibility at small sizes.

![Sample](docs/res/sample.png)

### [⬇︎ Download the latest release](https://github.com/rsms/interface/releases)

After downloading the zip from above:

1. Double-click the downloaded zip file to unpack or open it.
2. Follow the instructions in "install-mac.txt" or "install-win.txt", depending
   on what operating system you're using.


## Design

Interface is similar to Roboto, San Francisco, Akkurat, Asap, Lucida Grande and other "UI" typefaces. Some trade-offs were made in order to make this typeface work really well at small sizes:

- Currently not suitable for very large sizes because of some small-scale glyph optimizations (like "pits" and "traps") that help rasterization at small sizes but stand out and interfere at large sizes.
- Rasterized at sizes below 12px, some stems—like the horizontal center of "E", "F", or vertical center of "m"—are drawn with two semi-opaque pixels instead of one solid. This is because we "prioritize" (optimize for) higher-denisty rasterizations. If we move these stems to an off-center position—so that they can be drawn sharply at e.g. 11px—text will be less legible at higher resolutions.

Current font styles:

- Regular — master
  - Italic
- Bold — master
  - BoldItalic
- Medium — derived from Regular and Bold by mixing
  - MediumItalic
- Black — derived from Regular and Bold by mixing
  - BlackItalic

Future versions will hopefully include lighter weights.


### Font metrics

This font was originally designed to work at a specific size: 11px. Thus, the Units per [EM](https://en.wikipedia.org/wiki/Em_(typography)) (UPM) is defined in such a way that a power-of-two multiple of one EM unit ends up at an integer value compared to a pixel. Most fonts are designed with a UPM of either 1000 or 2048. Because of this we picked a value that is as high as possible but also as close as possible to one of those common values (since it's reasonable to assume that some layout engines and rasterizers are optimized for those value magnitudes.) We ended up picking a UPM of 2816 which equates to exactly 256 units per pixel when rasterized for size 11pt at 1x scale. This also means that when rasterized at power-of-two scales (like 2x and 4x) the number of EM units corresponding to a pixel is an integer (128 units for 2x, 64 for 4x, and so on.)

However, as the project progressed and the typeface was put into use, it quickly
bacame clear that for anything longer than a short word, it was actually hard to
read the almost monotonically-spaced letters.

A second major revision was create where the previously-strict rule of geometry being even multiples of 256 was relaxed and now the rule is "try to stick with 128x, if you can't, stick with 64x and if you can't do that either, never go below 16x." This means that Interface is now much more variable in pace than it used to be, making it work better at higher resolutions and work much better in longer text, but losing some contrast and sharpness at small sizes.

![Metrics](docs/res/metrics.png)

The glyphs are designed based on this "plan"; most stems and lines will be positioned at EM units that are even multiples of 128, and in a few cases they are at even multiples of 64 or as low as 16.

Metrics:

- UPM:        2816
- Descender:  -640
- x-height:   1536
- Cap height: 2048
- Ascender:   2688

Translating between EM units and pixels:

- Rasterized at 11px: 1px = 256 units
- Rasterized at 22px: 1px = 128 units
- Rasterized at 44px: 1px =  64 units

There's a Figma workspace for glyphs, with configured metrics: ["Interface glyphs"](https://www.figma.com/file/RtScFU5NETY3j9E0yOmnW4gv/Interface-glyphs)


## See also

- [Contributing](CONTRIBUTING.md)
- [SIL Open Font License](LICENSE.txt)
