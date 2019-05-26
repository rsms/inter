#
# Selects all glyphs which are empty
#
import sys

def isEmpty(g):
  for master in g.parent.masters:
    layer = g.layers[master.id]
    if layer.bounds is not None and layer.bounds.size.width > 0:
      return False
  return True

font = Glyphs.font
font.disableUpdateInterface()
try:
  font.selection = [g for g in font.glyphs if isEmpty(g)]
finally:
  font.enableUpdateInterface()
