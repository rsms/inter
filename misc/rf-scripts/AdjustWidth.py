#
# This script changes the width of all glyphs by applying a multiplier.
# It keeps the contours centered as glyphs get wider or tighter.
#
from mojo.roboFont import version
from math import ceil, floor

if __name__ == "__main__":
  font = CurrentFont()
  print "Resizing glyph margins for %r" % font

  # how much to add or remove from each glyph's margin
  A = 32

  if font is not None:
    errors = 0  # if >0 then changes are discarded
    for g in font:
      # skip glyphs
      #if g.name in ('c', 'e', 'o', 'r', 'j'):
      # continue

      if g.width < 4:
        print '"%s": ["ignore", "zero-width"],' % (g.name)
        continue

      if g.box is None:
        print '"%s": ["ignore", "empty"],' % (g.name)
        continue

      if g.width % 4 != 0:
        print '"%s": ["error", "misaligned"],' % (g.name)
        errors += 1
        continue

      #if g.leftMargin <= 0 or g.rightMargin <= 0:
      #  print '"%s": ["ignore", "zero-or-negative"],' % (g.name)
      #  continue

      leftMargin = int(max(0, g.leftMargin + A))
      rightMargin = int(max(0, g.rightMargin + A))

      #print '"%s": ["update", %g, %g],' % (g.name, leftMargin, rightMargin)
      if 'interui.spaceadjust' in g.lib:
        g.lib['interui.width-adjustments'].append(A)
      else:
        g.lib['interui.width-adjustments'] = [A]
      # order of assignment is probably important
      g.rightMargin = int(rightMargin)
      g.leftMargin  = int(leftMargin)

    if errors > 0:
        print "Discarding changes because there were errors"
    else:
        font.update()
  else:
    print "No fonts open"

  print "Done"
