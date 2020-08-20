from fontTools.otlLib.builder import buildStatTable


# [from OpenType spec on STAT, flags]
# If set, it indicates that the axis value represents the “normal” value
# for the axis and may be omitted when composing name strings.
OT_ELIDABLE_AXIS_VALUE_NAME = 0x0002

def rebuildStatTable(font, designspace):
  #
  # Changing this code? See discussion at https://github.com/rsms/inter/issues/308
  #
  if not 'fvar' in font:
    raise Exception('missing fvar table in font')
  axes = [dict(tag=a.axisTag, name=a.axisNameID) for a in font['fvar'].axes]

  # isMultiAxis is true when compiling the multi-axis VF,
  # false when compiling e.g. Inter-roman.var.ttf
  isMultiAxis = False
  if len(axes) > 1:
    isMultiAxis = True

  axisTagToName = dict()
  for axis in designspace.axes:
    axisTagToName[axis.tag] = axis.name

  weightAxisName = axisTagToName['wght']
  slantAxisName = axisTagToName.get('slnt', 'Slant')
  regularWeightValueEntry = None

  weightValues = []
  slantValues = []
  extremeSlantValue = 0
  for instance in designspace.instances:
    weightValue = instance.location[weightAxisName]
    slantValue = instance.location.get(slantAxisName, 0)
    if slantValue != 0:
      # slanted (we only make one entry: "Italic")
      if isMultiAxis and weightValue == 400:
        extremeSlantValue = slantValue
        slantValues.append({
          'name': instance.styleName,
          'value': slantValue,
        })
    else:
      # upright
      v = {
        'name': instance.styleName,
        'value': weightValue,
      }
      if weightValue == 400:
        v['flags'] = OT_ELIDABLE_AXIS_VALUE_NAME
        v['linkedValue'] = 700  # style link to "Bold"
        regularWeightValueEntry = v
      weightValues.append(v)

  # "Regular" entry for the slant axis, linked with the "Italic" entry
  if isMultiAxis:
    slantValues.append({
      'name': regularWeightValueEntry['name'],
      'value': 0,
      'flags': OT_ELIDABLE_AXIS_VALUE_NAME,
      'linkedValue': extremeSlantValue,
    })

  for a in axes:
    tag = a['tag']
    if tag == 'wght':
      a['values'] = weightValues
    elif tag == 'slnt' and len(slantValues) > 0:
      a['values'] = slantValues

  buildStatTable(font, axes)

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
