#
# This script changes the width of all glyphs by applying a multiplier.
# It keeps the contours centered as glyphs get wider or tighter.
#
from mojo.roboFont import version
from math import ceil, floor

if __name__ == "__main__":
  font = CurrentFont()
  print "Resizing glyph margins for %r" % font

  if font is not None:
    for g in font:
      leftMargin = g.leftMargin
      rightMargin = g.rightMargin

      if leftMargin < 0 or rightMargin < 0:
        g.rightMargin = int(max(0, rightMargin))
        g.leftMargin  = int(max(0, leftMargin))
        print("adjust %s" % g.name)

    font.update()
  else:
    print "No fonts open"

  print "Done"
