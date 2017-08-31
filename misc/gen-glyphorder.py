#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, plistlib
from collections import OrderedDict
from argparse import ArgumentParser


def parseGlyphComposition(composite):
  c = composite.split("=")
  d = c[1].split("/")
  glyphName = d[0]
  if len(d) == 1:
    offset = [0, 0]
  else:
    offset = [int(i) for i in d[1].split(",")]
  accentString = c[0]
  accents = accentString.split("+")
  baseName = accents.pop(0)
  accentNames = [i.split(":") for i in accents]
  return (glyphName, baseName, accentNames, offset)


def loadGlyphCompositions(filename):  # { glyphName => (baseName, accentNames, offset) }
  compositions = OrderedDict()
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if len(line) > 0 and line[0] != '#':
        glyphName, baseName, accentNames, offset = parseGlyphComposition(line)
        compositions[glyphName] = (baseName, accentNames, offset)
  return compositions


def main():
  argparser = ArgumentParser(description='Generate glyph order list from UFO files')
  argparser.add_argument('fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO files')
  args = argparser.parse_args()

  srcdir = os.path.abspath(os.path.join(__file__, '..', '..'))

  nameLists = []
  fontPaths = []

  for fontPath in args.fontPaths:
    if 'regular' or 'Regular' in fontPath:
      fontPaths = [fontPath] + fontPaths
    else:
      fontPaths.append(fontPath)

  for fontPath in fontPaths:
    libPlist = plistlib.readPlist(os.path.join(fontPath, 'lib.plist'))
    if 'public.glyphOrder' in libPlist:
      nameLists.append(libPlist['public.glyphOrder'])

  glyphorderUnion = OrderedDict()

  for names in zip(*nameLists):
    for name in names:
      glyphorderUnion[name] = True

  # add any composed glyphs to the end
  diacriticComps = loadGlyphCompositions(os.path.join(srcdir, 'src', 'diacritics.txt'))
  for name in diacriticComps.keys():
    glyphorderUnion[name] = True

  glyphorderUnionNames = glyphorderUnion.keys()
  print('\n'.join(glyphorderUnionNames))


if __name__ == '__main__':
  main()
