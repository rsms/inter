#!/usr/bin/env python
# encoding: utf8
#
# Grab http://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
#
from __future__ import print_function
import os, sys, json, re
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont
from collections import OrderedDict
from unicode_util import parseUnicodeDataFile


# Regex matching "default" glyph names, like "uni2043" and "u01C5"
uniNameRe = re.compile(r'^u(?:ni)([0-9A-F]{4,8})$')


def unicodeForDefaultGlyphName(glyphName):
  m = uniNameRe.match(glyphName)
  if m is not None:
    try:
      return int(m.group(1), 16)
    except:
      pass
  return None


def loadAGL(filename):  # -> { 2126: 'Omega', ... }
  m = {}
  with open(filename, 'r') as f:
    for line in f:
      # Omega;2126
      # dalethatafpatah;05D3 05B2   # higher-level combinations; ignored
      line = line.strip()
      if len(line) > 0 and line[0] != '#':
        name, uc = tuple([c.strip() for c in line.split(';')])
        if uc.find(' ') == -1:
          # it's a 1:1 mapping
          m[int(uc, 16)] = name
  return m


def loadLocalNamesDB(fonts, agl, diacriticComps):
  uc2names = None  # { 2126: ['Omega', ...], ...}
  allNames = OrderedDict() # {'Omega':True, ...}

  for font in fonts:
    _uc2names = font.getCharacterMapping()  # { 2126: ['Omega', ...], ...}
    if uc2names is None:
      uc2names = _uc2names
    else:
      for uc, _names in _uc2names.iteritems():
        names = uc2names.setdefault(uc, [])
        for name in _names:
          if name not in names:
            names.append(name)
    for g in font:
      allNames.setdefault(g.name, True)

  # agl { 2126: 'Omega', ...} -> { 'Omega': [2126, ...], ...}
  aglName2Ucs = {}
  for uc, name in agl.iteritems():
    aglName2Ucs.setdefault(name, []).append(uc)

  for glyphName, comp in diacriticComps.iteritems():
    aglUCs = aglName2Ucs.get(glyphName)
    if aglUCs is None:
      uc = unicodeForDefaultGlyphName(glyphName)
      if uc is not None:
        glyphName2 = agl.get(uc)
        if glyphName2 is not None:
          glyphName = glyphName2
        names = uc2names.setdefault(uc, [])
        if glyphName not in names:
          names.append(glyphName)
      allNames.setdefault(glyphName, True)
    else:
      allNames.setdefault(glyphName, True)
      for uc in aglUCs:
        names = uc2names.get(uc, [])
        if glyphName not in names:
          names.append(glyphName)
        uc2names[uc] = names

  name2ucs = {}  # { 'Omega': [2126, ...], ...}
  for uc, names in uc2names.iteritems():
    for name in names:
      name2ucs.setdefault(name, set()).add(uc)

  return uc2names, name2ucs, allNames


def canonicalGlyphName(glyphName, uc2names):
  uc = unicodeForDefaultGlyphName(glyphName)
  if uc is not None:
    names = uc2names.get(uc)
    if names is not None and len(names) > 0:
      return names[0]
  return glyphName


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


def rgbaToCSSColor(r=0, g=0, b=0, a=1):
  R,G,B = int(r * 255), int(g * 255), int(b * 255)
  if a == 1:
    return '#%02x%02x%02x' % (R,G,B)
  else:
    return 'rgba(%d,%d,%d,%f)' % (R,G,B,a)


def unicodeName(cp):
  if cp is not None and len(cp.name):
    if cp.name[0] == '<':
      return '[' + cp.categoryName + ']'
    elif len(cp.name):
      return cp.name
  return None


def main():
  argparser = ArgumentParser(
    description='Generate info on name, unicodes and color mark for all glyphs')

  argparser.add_argument(
    '-ucd', dest='ucdFile', metavar='<file>', type=str,
    help='UnicodeData.txt file from http://www.unicode.org/')

  argparser.add_argument(
    'fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args()
  markLibKey = 'com.typemytype.robofont.mark'

  fontPaths = []
  for fontPath in args.fontPaths:
    fontPath = fontPath.rstrip('/ ')
    if 'regular' or 'Regular' in fontPath:
      fontPaths = [fontPath] + fontPaths
    else:
      fontPaths.append(fontPath)

  fonts = [OpenFont(fontPath) for fontPath in args.fontPaths]

  agl = loadAGL('src/glyphlist.txt') # { 2126: 'Omega', ... }
  diacriticComps = loadGlyphCompositions('src/diacritics.txt')
  uc2names, name2ucs, allNames = loadLocalNamesDB(fonts, agl, diacriticComps)

  ucd = {}
  if args.ucdFile:
    ucd = parseUnicodeDataFile(args.ucdFile)

  glyphorder = OrderedDict()
  with open(os.path.join(os.path.dirname(args.fontPaths[0]), 'glyphorder.txt'), 'r') as f:
    for name in f.read().splitlines():
      if len(name) and name[0] != '#':
        glyphorder[name] = True

  for name in diacriticComps.iterkeys():
    glyphorder[name] = True

  glyphNames = glyphorder.keys()
  visitedGlyphNames = set()
  glyphs = []

  for font in fonts:
    for name, v in glyphorder.iteritems():
      if name in visitedGlyphNames:
        continue

      g = None
      ucs = []
      try:
        g = font[name]
        ucs = g.unicodes
      except:
        ucs = name2ucs.get(name)
        if ucs is None:
          continue

      color = None
      if g is not None and markLibKey in g.lib:
        # TODO: translate from (r,g,b,a) to #RRGGBB (skip A)
        rgba = g.lib[markLibKey]
        if isinstance(rgba, list) or isinstance(rgba, tuple):
          color = rgbaToCSSColor(*rgba)
      elif name in diacriticComps:
        color = '<derived>'

      # name[, unicode[, unicodeName[, color]]]
      if len(ucs):
        for uc in ucs:
          ucName = unicodeName(ucd.get(uc))

          if not ucName and uc >= 0xE000 and uc <= 0xF8FF:
            ucName = '[private use %04X]' % uc

          if color:
            glyph = [name, uc, ucName, color]
          elif ucName:
            glyph = [name, uc, ucName]
          else:
            glyph = [name, uc]
          glyphs.append(glyph)
      else:
        glyph = [name, None, None, color] if color else [name]
        glyphs.append(glyph)

      visitedGlyphNames.add(name)

  print('{"glyphs":[')
  prefix = '  '
  for g in glyphs:
    print(prefix + json.dumps(g))
    if prefix == '  ':
      prefix = ', '
  print(']}')


if __name__ == '__main__':
  main()
