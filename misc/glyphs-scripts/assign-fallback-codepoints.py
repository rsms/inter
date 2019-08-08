#
# Assigns private-use codepoints to glyphs which are not mapped
# to any Unicode codepoints.
#
# This script will ignore glyphs which name starts with "." as well as
# empty glyphs and glyphs which are not exported.
#
import sys
from collections import OrderedDict

DRY_RUN = True

font = Glyphs.font
font.disableUpdateInterface()

def isEmpty(g):
  for master in g.parent.masters:
    layer = g.layers[master.id]
    if layer.bounds is not None and layer.bounds.size.width > 0:
      return False
  return True

try:
  # find next unallocated private-use codepoint
  nextcp = 0xE000
  for g in font.glyphs:
    if g.unicodes is not None:
      for c in [int(c, 16) for c in g.unicodes]:
        if c <= 0xEFFF and c >= nextcp:
          nextcp = c + 1

  print('nextcp: %X' % nextcp)
  if DRY_RUN:
    print('DRY_RUN mode (no actual changes will be made)')
  print('————————————————')

  # for printing
  mappings = OrderedDict()
  longest_gname = 0

  # assign private-use codepoints to glyphs that have no existing unicode mapping
  for g in font.glyphs:
    # only care for glyphs which are being exported (also ignore "special" glyphs)
    if g.export and g.name[0] != '.' and (g.unicodes is None or len(g.unicodes) == 0):
      # error on empty glyphs -- there should be no unmapped empty glyphs
      if isEmpty(g):
        sys.stderr.write('ERR: glyph %r is empty but has no unicode mapping (skipping)\n' % g.name)
        continue
      unicodes = [hex(nextcp).upper()[2:]]
      mappings[g.name] = unicodes[0]
      if len(g.name) > longest_gname:
        longest_gname = len(g.name)
      if not DRY_RUN:
        g.unicodes = unicodes
      nextcp += 1

  # print mappings made
  for gname, cp in mappings.iteritems():
    print('%s  %s' % (gname.ljust(longest_gname), cp))

finally:
  font.enableUpdateInterface()

