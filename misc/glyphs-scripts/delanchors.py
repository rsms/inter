delanchors = ['top_dd', 'top0315', 'bottom_dd']
font = Glyphs.font
font.disableUpdateInterface()
try:
  for g in font.glyphs:
    g.beginUndo()
    try:
      for master in font.masters:
        layer = g.layers[master.id]
        for aname in delanchors:
          try:
            del(layer.anchors[aname])
            print("del %s in %s", aname, g.name)
          except:
            pass
    finally:
      g.endUndo()
finally:
  font.enableUpdateInterface()
