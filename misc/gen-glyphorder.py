#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, plistlib, sys
from collections import OrderedDict
from argparse import ArgumentParser
from ConfigParser import RawConfigParser


BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


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

  srcDir = os.path.join(BASEDIR, 'src')

  # load fontbuild config
  config = RawConfigParser(dict_type=OrderedDict)
  config.read(os.path.join(srcDir, 'fontbuild.cfg'))
  deleteNames = set(config.get('glyphs', 'delete').split())

  fontPaths = []
  for fontPath in args.fontPaths:
    if 'regular' or 'Regular' in fontPath:
      fontPaths = [fontPath] + fontPaths
    else:
      fontPaths.append(fontPath)

  fontPath0 = args.fontPaths[0]
  libPlist = plistlib.readPlist(os.path.join(fontPath, 'lib.plist'))
  glyphOrder = libPlist['public.glyphOrder']
  glyphNameSet = set(glyphOrder)

  nameLists = []
  indexOffset = 0
  index = -1

  for fontPath in fontPaths[1:]:
    libPlist = plistlib.readPlist(os.path.join(fontPath, 'lib.plist'))
    if 'public.glyphOrder' in libPlist:
      names = libPlist['public.glyphOrder']
      numInserted = 0
      for i in range(len(names)):
        name = names[i]
        if name not in glyphNameSet:
          if i > 0 and names[i-1] in glyphNameSet:
            # find position of prev glyph
            index = glyphOrder.index(names[i-1]) + 1
          elif index != -1:
            index += 1
          else:
            index = min(len(glyphOrder), i - indexOffset)

          glyphOrder.insert(index, name)
          numInserted += 1
          glyphNameSet.add(name)

      indexOffset += numInserted

  # add any composed glyphs to the end
  diacriticComps = loadGlyphCompositions(os.path.join(srcDir, 'diacritics.txt'))
  for name in diacriticComps.keys():
    if name not in glyphNameSet:
      glyphOrder.append(name)

  # filter out deleted glyphs
  glyphOrder = [n for n in glyphOrder if n not in deleteNames]

  print('\n'.join(glyphOrder))


if __name__ == '__main__':
  main()
