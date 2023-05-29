import sys, argparse, re
from fontTools.designspaceLib import DesignSpaceDocument


WHITESPACE_RE = re.compile(r'\s+')


def remove_whitespace(s):
  return WHITESPACE_RE.sub("", s)


def fixup_instances_text(designspace):
  # makes the "text" (non-display) instances the default ones
  i = len(designspace.instances)
  while i > 0:
    i -= 1
    instance = designspace.instances[i]
    if instance.name.find('Inter Display') != -1:
      del designspace.instances[i]


def fixup_instances_display(designspace):
  # makes the display instances the default ones
  i = len(designspace.instances)
  while i > 0:
    i -= 1
    instance = designspace.instances[i]
    if instance.name.find('Inter Display') != -1:
      if instance.styleName == 'Display':
        instance.styleName = 'Regular'
      else:
        instance.styleName = instance.styleName.replace('Display ', '')
    else:
      del designspace.instances[i]
  # change default opsz value
  for a in designspace.axes:
    if a.tag == "opsz":
      a.default = a.maximum
      break


def fixup_postscript_instance_names(designspace):
  # make sure there are PostScript names assigned (fontmake does not create these)
  psFamilyName = remove_whitespace(designspace.instances[0].familyName)
  for instance in designspace.instances:
    instance.postScriptFontName = psFamilyName + remove_whitespace(instance.styleName)


def main(argv):
  ap = argparse.ArgumentParser(description=
    'Generate designspace file for variable font from generic designspace file')
  ap.add_argument("input_designspace", help="Path to generic designspace file")
  ap.add_argument("output_designspace", help="Path for output designspace file")

  args = ap.parse_args()

  designspace = DesignSpaceDocument.fromfile(args.input_designspace)

  # fixup_instances_text(designspace)
  fixup_instances_display(designspace)

  fixup_postscript_instance_names(designspace)

  designspace.write(args.output_designspace)


if __name__ == '__main__':
  main(sys.argv)
