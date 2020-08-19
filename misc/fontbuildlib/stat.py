# from fontTools.designspaceLib import DesignSpaceDocument
# from fontTools.ttLib.tables import otTables as ot
# from fontTools.ttLib import ttFont
from fontTools.otlLib.builder import buildStatTable

def rebuildStatTable(font, designspace):
  if not 'fvar' in font:
    raise Exception('missing fvar table in font')

  axes = [dict(tag=a.axisTag, name=a.axisNameID) for a in font['fvar'].axes]
  # axes = []
  # for a in statTable.DesignAxisRecord.Axis:
  #   axes.append({ 'tag': a.AxisTag, 'name': a.AxisNameID, 'ordering': a.AxisOrdering })

  axisNameToTag = dict()
  for axis in designspace.axes:
    axisNameToTag[axis.name] = axis.tag

  locations = []
  for instance in designspace.instances:
    location = dict()
    for axisName, value in instance.location.items():
      tag = axisNameToTag[axisName]
      location[tag] = value
    locations.append({ 'name': instance.styleName, 'location': location })

  buildStatTable(font, axes, locations)


# font = ttFont.TTFont("build/fonts/var/Inter.var.ttf")
# designspace = DesignSpaceDocument.fromfile('build/ufo/inter.designspace')
# rebuildStatTable(font, designspace)
# print("write build/tmp/Inter.var-patched.ttf")
# font.save("build/tmp/Inter.var-patched.ttf")
