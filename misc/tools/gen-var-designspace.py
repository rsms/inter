import sys, argparse, re
from fontTools.designspaceLib import DesignSpaceDocument


WHITESPACE_RE = re.compile(r'\s+')


def remove_whitespace(s):
  return WHITESPACE_RE.sub("", s)


def fixup_names(instance_or_source):
  instance_or_source.name = instance_or_source.name.replace(' Display', '')
  if instance_or_source.styleName == 'Display':
    instance_or_source.styleName = 'Regular'
  else:
    instance_or_source.styleName = instance_or_source.styleName.replace('Display ', '')


def fixup_instance(designspace, instance):
  fixup_names(instance)

  # note: these must match name ID 25 "Variations PostScript Name Prefix"
  # which in turn must be unique for the roman vs italic fonts.
  # If you change this, also update bake-vf.py to match.
  # See https://github.com/rsms/inter/issues/577
  isItalic = "Italic" in instance.styleName
  psStyle = remove_whitespace(instance.styleName)
  if isItalic:
    psStyle = psStyle.replace('Italic','')
    if psStyle == '':
      instance.postScriptFontName = 'InterVariableItalic'
    else:
      instance.postScriptFontName = 'InterVariableItalic-' + psStyle
  else:
    if psStyle == 'Regular':
      instance.postScriptFontName = 'InterVariable'
    else:
      instance.postScriptFontName = 'InterVariable-' + psStyle

  instance.styleMapFamilyName = instance.styleMapFamilyName.replace(' Display', '')

  # remove WWSFamilyName and WWSSubfamilyName properties
  if 'com.schriftgestaltung.properties' in instance.lib:
    del instance.lib['com.schriftgestaltung.properties']

  if 'com.schriftgestaltung.customParameters' in instance.lib:
    customParameters = instance.lib['com.schriftgestaltung.customParameters']
    i = len(customParameters)
    while i > 0:
      i -= 1
      if customParameters[i][0] == 'Has WWS Names':
        del customParameters[i]


def fixup_instances(designspace):
  USE_DISPLAY_AS_DEFAULT = False
  i = len(designspace.instances)
  while i > 0:
    i -= 1
    instance = designspace.instances[i]
    if USE_DISPLAY_AS_DEFAULT:
      if instance.name.find('Inter Display') != -1:
        fixup_instance(designspace, instance)
      else:
        del designspace.instances[i]
    else:
      if instance.name.find('Inter Display') == -1:
        fixup_instance(designspace, instance)
      else:
        del designspace.instances[i]


# def fixup_axes_defaults(designspace):
#   for a in designspace.axes:
#     if a.tag == "opsz":
#       a.default = a.maximum
#       break


def fixup_sources(designspace):
  i = len(designspace.sources)
  while i > 0:
    i -= 1
    source = designspace.sources[i]
    if source.name.find('Inter Display') != -1:
      fixup_names(source)
    else:
      source.name = source.name + ' Text'
      if source.styleName == 'Regular':
        source.styleName = 'Text'
      else:
        source.styleName = 'Text ' + source.styleName


def main(argv):
  ap = argparse.ArgumentParser(description=
    'Generate designspace file for variable font from generic designspace file')
  ap.add_argument("input_designspace", help="Path to generic designspace file")
  ap.add_argument("output_designspace", help="Path for output designspace file")

  args = ap.parse_args()

  designspace = DesignSpaceDocument.fromfile(args.input_designspace)

  fixup_instances(designspace)
  # fixup_axes_defaults(designspace)
  fixup_sources(designspace)

  designspace.write(args.output_designspace)


if __name__ == '__main__':
  main(sys.argv)
