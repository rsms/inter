from fontTools.otlLib.builder import buildStatTable


# [from OpenType spec on STAT, flags]
# If set, it indicates that the axis value represents the “normal” value
# for the axis and may be omitted when composing name strings.
OT_ELIDABLE_AXIS_VALUE_NAME = 0x0002

def rebuildStatTable(font, designspace):
  if not 'fvar' in font:
    raise Exception('missing fvar table in font')
  axes = [dict(tag=a.axisTag, name=a.axisNameID) for a in font['fvar'].axes]
  locations = None
  if len(axes) > 1:
    # TODO: Compute locations automatically.
    # Currently specific to Inter w/ hard-coded values.
    locations = [
      { 'name': 'Regular', 'location': { 'wght': 400, 'slnt': 0 },
        'flags': OT_ELIDABLE_AXIS_VALUE_NAME },
      { 'name': 'Italic', 'location': { 'wght': 400, 'slnt': -10.0 } },
    ]
  axisTagToName = dict()
  for axis in designspace.axes:
    axisTagToName[axis.tag] = axis.name
  weightAxisName = axisTagToName['wght']
  slantAxisName = axisTagToName.get('slnt', 'Slant')
  weightAxis = None
  for a in axes:
    if a['tag'] == 'wght':
      weightAxis = a
      break
  weightValues = []
  for instance in designspace.instances:
    for axisName, value in instance.location.items():
      if axisName == slantAxisName:
        # skip italic/oblique/slant
        continue
      weightValue = {
        'name':  instance.styleName,
        'value': instance.location[weightAxisName],
      }
      if weightValue['value'] == 400:
        weightValue['flags'] = OT_ELIDABLE_AXIS_VALUE_NAME
      weightValues.append(weightValue)
  weightAxis['values'] = weightValues

  # axisNameToTag = dict()
  # for axis in designspace.axes:
  #   axisNameToTag[axis.name] = axis.tag
  # locations = []
  # for instance in designspace.instances:
  #   location = dict()
  #   for axisName, value in instance.location.items():
  #     tag = axisNameToTag[axisName]
  #     location[tag] = value
  #   loc = { 'name': instance.styleName, 'location': location }
  #   if instance.styleName == "Regular":
  #     loc['flags'] = OT_ELIDABLE_AXIS_VALUE_NAME
  #   locations.append(loc)

  buildStatTable(font, axes, locations)
