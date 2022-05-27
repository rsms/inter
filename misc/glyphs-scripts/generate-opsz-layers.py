#MenuTitle: Generate opsz brace layers
# -*- coding: utf-8 -*-
import GlyphsApp
import copy

Font = Glyphs.font
selectedLayers = Font.selectedLayers

# Glyphs.font.selection - selected glyphs in "Font" tab
# Glyphs.font.selectedFontMaster

def build_axis_coordinates(g, master):
  coordinates = {}
  for i in range(len(g.parent.axes)):
    axis = g.parent.axes[i]
    if axis.axisTag == "opsz":
      coordinates[axis.axisId] = 72
    else:
      coordinates[axis.axisId] = master.axes[i]
  return coordinates


def process_glyph(g, axes):
  print("processing glyph %r" % g.name)

  existing_opsz_layers = {}
  for layer in g.layers:
    # print("- %s (%r) %r" % (
    #   layer.name, layer.associatedMasterId, layer.attributes['coordinates']))
    if layer.attributes['coordinates']:
      existing_opsz_layers[layer.associatedMasterId] = layer
  # print("existing_opsz_layers %r" % existing_opsz_layers)

  for master in g.parent.masters:
    if not master.name.startswith("Thin"):
      # Only thin uses brace layers for opsz
      continue
    layer = g.layers[master.id]
    # print("%s" % layer.name)
    if master.id in existing_opsz_layers:
      print("skip layer %s with existing opsz brace layer" % layer.name)
      continue

    newLayer = layer.copy()
    # Note: "same name" matters for designspace generation!
    newLayer.name = "opsz"
    newLayer.associatedMasterId = master.id
    newLayer.attributes['coordinates'] = build_axis_coordinates(g, master)
    g.layers.append(newLayer)
    print("layer.guides %r" % layer.guides)
    print("created layer %s (copy of %r)" % (newLayer.name, layer.name))


if Glyphs.font and Glyphs.font.selectedLayers:
  try:
    Glyphs.font.disableUpdateInterface()
    glyphs = set([l.parent for l in Glyphs.font.selectedLayers])
    print(glyphs)
    axes = {}
    for i in range(len(Glyphs.font.axes)):
      axis = Glyphs.font.axes[i]
      axes[axis.axisTag] = {"index":i, "axis":axis}
      # print("%r => %r" % (axis.axisTag, axis.axisId))
    for g in glyphs:
      try:
        g.beginUndo()
        process_glyph(g, axes)
      finally:
        g.endUndo()
  finally:
    Glyphs.font.enableUpdateInterface()
