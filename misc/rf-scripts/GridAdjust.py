#
# This script changes the width of any glyph which width is not an even multiple of 256.
# For glyphs that are updated, the shape(s) inside the glyph are centered as well.
#
from mojo.roboFont import version
from math import ceil, floor

if __name__ == "__main__":
  font = CurrentFont()
  print "Fitting glyphs to EM grid at 256 %r" % font

  # Strategy to use for centering a glyph when resizing its EM:
  #   "center"          Ignore existing margins and center in EM at on integer units.
  #   "adjust-margins"  Attempt to retain existing margins w/o centering inside EM.
  centeringStrategy = 'center'

  if font is not None:
    for g in font:
      # only consider adjusting the listed glyphs
      # if g.unicode not in (0x212B, 0x005A, 0x0387):
      #   continue

      if g.width < 2:
        # ignore zero width glyph
        # print 'ignoring %r -- zero width' % g
        continue

      if g.width % 256 == 0:
        # ignore already aligned glyph
        # print 'ignoring %r -- already aligned' % g
        continue

      width = g.width
      if g.rightMargin < 128:
        width = ceil(width / 256) * 256
      else:
        width = round(width / 256) * 256

      # center glyph in EM
      leftMargin = g.leftMargin
      rightMargin = g.rightMargin

      if centeringStrategy == 'adjust-margins':
        # Adjust margins to place the glyph in the center while retaining original
        # left/right margins.
        widthDelta = width - g.width
        leftMargin  = g.leftMargin + int(floor(widthDelta / 2))
        rightMargin = g.rightMargin + int(ceil(widthDelta / 2))
      elif centeringStrategy == 'center':
        # Read g.box (effective bounds of the glyph) and truly center the
        # glyph, but we could run the risk of losing some intentionally-left or right
        # aligned glyph, e.g. "|x  |" -> "|  x  |"
        if g.box is not None:
          xMin, yMin, xMax, yMax = g.box
          graphicWidth = xMax - xMin
          leftMargin = round((width - graphicWidth) / 2)
      else:
        print 'Unexpected centeringStrategy value'
        break

      # log message
      uniname = ''
      if g.unicode is not None:
        uniname = ' U+%04X' % g.unicode
      print 'Adjusting "%s"%s from %g to %g' % (g.name, uniname, g.width, width)

      # write changes to glyph
      g.lib['interface.gridadjust.original'] = repr({
        "rightMargin": g.rightMargin,
        "leftMargin": g.leftMargin,
        "width": g.width,
      })

      # order of assignment is probably important
      g.rightMargin = int(rightMargin)
      g.leftMargin  = int(leftMargin)
      g.width       = int(width)

    font.update()
  else:
    print "No fonts open"

  print "Done"
