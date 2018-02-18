#
# This script changes the width of all glyphs by applying a multiplier.
# It keeps the contours centered as glyphs get wider or tighter.
#
from mojo.roboFont import version
from math import ceil, floor

if __name__ == "__main__":
  font = CurrentFont()
  ignoreGlyphsWithoutContours = True  # like spaces
  print "# Resizing glyph margins for %r" % font

  # how much to add or remove from each glyph's margin
  A = -4

  if font is not None:
    # first, check for errors and collect glyphs we should adjust
    glyphs = []
    glyphNamesToAdjust = set()
    ignored = []
    errors = 0

    for g in font:
      if g.width < 4:
        ignored.append((g.name, 'zero-width'))
        continue

      if ignoreGlyphsWithoutContours and g.box is None:
        # print '"%s": ["ignore", "empty"],' % (g.name)
        ignored.append((g.name, 'empty'))
        continue

      # skip glyphs
      #if g.name in ('c', 'e', 'o', 'r', 'j'):
      # continue

      if g.width % 4 != 0:
        print 'error: %s is misaligned; width = %g (not an even multiple of 4)' % (g.name, g.width)
        errors += 1
        continue

      glyphs.append(g)
      glyphNamesToAdjust.add(g.name)

    if errors > 0:
      print "Stopping changes because there are errors"
    else:

      print '# Result from AdjustWidth.py with A=%g on %s %s' % (
        A, font.info.familyName, font.info.styleName)
      print '# name => [ (prevLeftMargin, prevRightMargin), (newLeft, newRight) ]'
      print 'resized_glyphs = ['

      adjustments = dict()

      onlyGlyphs = None # ['A', 'Lambda']  # DEBUG
      count = 0

      for g in glyphs:
        if onlyGlyphs is not None:
          if not g.name in onlyGlyphs:
            continue
          if len(onlyGlyphs) == count:
            break
          count += 1

        for comp in g.components:
          # adjust offset of any components which are being adjusted
          if comp.baseGlyph in glyphNamesToAdjust:
            # x, y -- counter-balance x offset
            comp.offset = (comp.offset[0] - A, comp.offset[1])

        newLeftMargin = int(g.leftMargin + A)
        newRightMargin = int(g.rightMargin + A)

        print '  "%s": [(%g, %g), (%g, %g)],' % (
          g.name, g.leftMargin, g.rightMargin, newLeftMargin, newRightMargin)

        g.leftMargin  = int(newLeftMargin)
        g.rightMargin = int(newRightMargin)

      print '] # resized_glyphs'

      font.update()

      # if len(ignored) > 0:
      #   print ''
      #   print '# name => [what, reason]'
      #   print "ignored_glyphs = ["
      #   for t in ignored:
      #     print '  "%s": ["ignore", %r],' % t
      #   print '] # ignored_glyphs'

  else:
    print "No fonts open"

  print "Done"
