#MenuTitle: Copy global guides from roman to italic masters
# -*- coding: utf-8 -*-
import GlyphsApp
import copy

Glyphs.clearLog()
font = Glyphs.font

romanMasters = [m for m in font.masters if m.italicAngle == 0.0]
#print(romanMasters)

def find_matching_roman(im):
  wght = im.axes[0]
  opsz = im.axes[2]
  for rm in romanMasters:
    if wght == rm.axes[0] and opsz == rm.axes[2]:
      return rm

for im in font.masters:
  if im.italicAngle == 0.0:
    continue
  rm = find_matching_roman(im)
  if rm is None:
    raise Exception("rm not found (im=%r)" % im.name)
  print(im.name, '<-', rm.name)
  im.guides = [copy.copy(g) for g in rm.guides]
