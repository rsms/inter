#MenuTitle: Round Kerning of current master
# encoding: utf-8
import GlyphsApp

__doc__="""
Rounds kerning of the currently selected master to integer values
and drops any kerning smaller than 4.
"""

font = Glyphs.font
master_id = font.selectedFontMaster.id
MIN_VALUE = 4
to_be_removed = []  # [(L,R) ...]

try:
  Glyphs.font.disableUpdateInterface()
  for left, r_dict in font.kerning[master_id].items():
    if not left.startswith('@'):
      left = font.glyphForId_(left).name
    for right, value in r_dict.items():
      if not right.startswith('@'):
        right = font.glyphForId_(right).name
      value2 = float(int(value)) # floor()
      if abs(value2) < MIN_VALUE:
        to_be_removed.append((left, right))
      elif value2 != value:
        font.setKerningForPair(master_id, left, right, value2)

  for left, right in to_be_removed:
    print("removing pair (%s, %s)" % (left, right))
    font.removeKerningForPair(master_id, left, right)
finally:
  Glyphs.font.enableUpdateInterface()
