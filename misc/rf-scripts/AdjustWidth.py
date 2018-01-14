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
  A = -8

  if font is not None:
    # first, check for errors and collect glyphs we should adjust
    glyphs = []
    ignored = []
    errors = 0

    for g in font:
      if g.width < 4:
        ignored.append((g.name, 'zero-width'))
        continue

      # if g.box is None:
      #   print '"%s": ["ignore", "empty"],' % (g.name)
      #   continue

      # skip glyphs
      #if g.name in ('c', 'e', 'o', 'r', 'j'):
      # continue

      if g.width % 4 != 0:
        print '"%s": ["error", "misaligned"],' % (g.name)
        errors += 1
        continue

      glyphs.append(g)

    if errors > 0:
      print "Stopping changes because there are errors"
    else:

      print '# Result from AdjustWidth.py with A=%g on %s %s' % (
        A, font.info.familyName, font.info.styleName)
      print '# name => [ (prevLeftMargin, prevRightMargin), (newLeft, newRight) ]'
      print 'resized_glyphs = ['

      for g in glyphs:
        newLeftMargin = int(g.leftMargin + A)
        newRightMargin = int(g.rightMargin + A)

        print '  "%s": [(%g, %g), (%g, %g)],' % (
          g.name, g.leftMargin, g.rightMargin, newLeftMargin, newRightMargin)

        # order of assignment is probably important
        g.rightMargin = int(newRightMargin)
        g.leftMargin  = int(newLeftMargin)

      print '] # resized_glyphs'

      font.update()

      if len(ignored) > 0:
        print ''
        print '# name => [what, reason]'
        print "ignored_glyphs = ["
        for t in ignored:
          print '  "%s": ["ignore", %r],' % t
        print '] # ignored_glyphs'

  else:
    print "No fonts open"

  print "Done"
