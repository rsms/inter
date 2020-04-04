#MenuTitle: Assign fallback codepoints
# -*- coding: utf-8 -*-
__doc__="""
Assigns private-use codepoints to glyphs which are not mapped
to any Unicode codepoints.

This script will ignore glyphs:
- glyphs which are not exported
- glyphs which name starts with "."
- glyphs which name ends with ".case"
- empty glyphs
"""
import sys
from collections import OrderedDict

DRY_RUN = False

font = Glyphs.font
font.disableUpdateInterface()


def isEmpty(g):
  for master in g.parent.masters:
    layer = g.layers[master.id]
    if layer.bounds is not None and layer.bounds.size.width > 0:
      return False
  return True


def includeGlyph(g):
  if not g.export:
    return False
  if g.name[0] == '.':
    return False
  if g.name.endswith(".case"):
    return False
  # finally, return true if the glyph has no codepoint assigned
  return g.unicodes is None or len(g.unicodes) == 0


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
    if includeGlyph(g):
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

