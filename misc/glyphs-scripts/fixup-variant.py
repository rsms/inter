# Helper for making variants of a glyph.
# 
# e.g. we have 10 glyphs based on "I" and we now want to
# create an alternate "I" called "I.1".
# 
# 1. We first make our I.1 manually
# 2. Next we generate all other glyphs:
#      Idieresisacute=Idieresisacute.1
#      Istroke=Istroke.1
#      Itildebelow=Itildebelow.1
#      Igrave=Igrave.1
#      Iacute=Iacute.1
#      Icircumflex=Icircumflex.1
#      Itilde=Itilde.1
#      Imacron=Imacron.1
#      Ibreve=Ibreve.1
#      Iogonek=Iogonek.1
#    Which we paset into the "create glyphs" window
# 3. We now have 10 new glyphs.
# 4. Select all those new glyphs
# 5. Open the macro window
# 6. Paste this script and modify `prevcn` and `newcn`
# 7. Run it
# 
prevcn = "I"   # component to find and replace
newcn = "I.1"  # replacement component

font = Glyphs.font
font.disableUpdateInterface()
try:
  for layer in font.selectedLayers:
    g = None
    if isinstance(layer, GSGlyph):
      g = layer
    else:
      g = layer.parent
    print(g)
    g.beginUndo()
    try:
      for master in font.masters:
        layer = g.layers[master.id]
        print(layer)
        if len(layer.components) != 1:
          print("not a single component %s" % layer)
          continue
        layer.components[0].decompose()
        for c in layer.components:
          if c.name == prevcn:
            print("replace %s with %s" % (prevcn, newcn))
            c.name = newcn
    finally:
      g.endUndo()
finally:
  font.enableUpdateInterface()

