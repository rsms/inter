#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib, re
from collections import OrderedDict
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont


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


def fmtGlyphComposition(glyphName, baseName, accentNames, offset):
  # glyphName   = 'uni03D3'
  # baseName    = 'uni03D2'
  # accentNames = [['tonos', 'top'], ['acute', 'top']]
  # offset      = [100, 0]
  # => "uni03D2+tonos:top+acute:top=uni03D3/100,0"
  s = baseName
  for accentNameTuple in accentNames:
    s += '+' + accentNameTuple[0]
    if len(accentNameTuple) > 1:
      s += ':' + accentNameTuple[1]
  s += '=' + glyphName
  if offset[0] != 0 or offset[1] != 0:
    s += '/%d,%d' % tuple(offset)
  return s


def loadGlyphCompositions(filename):  # { glyphName => (baseName, accentNames, offset) }
  compositions = OrderedDict()
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if len(line) > 0 and line[0] != '#':
        glyphName, baseName, accentNames, offset = parseGlyphComposition(line)
        compositions[glyphName] = (baseName, accentNames, offset)
  return compositions


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


def loadFontGlyphs(font):
  uc2names = {}  # { 2126: ['Omega', ...], ...}
  name2ucs = {}  # { 'Omega': [2126, ...], '.notdef': [], ...}
  for g in font:
    name = g.name
    ucs = g.unicodes
    name2ucs[name] = ucs
    for uc in ucs:
      names = uc2names.setdefault(uc, [])
      if name not in names:
        names.append(name)
  return uc2names, name2ucs


def main():
  argparser = ArgumentParser(description='Fixup diacritic names')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    'fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts')

  args = argparser.parse_args()
  dryRun = args.dryRun

  uc2names = {}
  name2ucs = {}

  for fontPath in args.fontPaths:
    font = OpenFont(fontPath)
    _uc2names, _name2ucs = loadFontGlyphs(font)
    for uc, _names in _uc2names.iteritems():
      names = uc2names.setdefault(uc, [])
      for name in _names:
        if name not in names:
          names.append(name)
    for name, _ucs in _name2ucs.iteritems():
      ucs = name2ucs.setdefault(name, [])
      for uc in _ucs:
        if uc not in ucs:
          ucs.append(uc)

  agl = loadAGL('src/glyphlist.txt') # { 2126: 'Omega', ... }

  diacriticsFilename = 'src/diacritics.txt'
  diacriticComps = loadGlyphCompositions(diacriticsFilename) # {glyphName => (baseName, a, o)}

  for glyphName, comp in list(diacriticComps.items()):
    if glyphName not in name2ucs:
      uc = unicodeForDefaultGlyphName(glyphName)
      if uc is not None:
        aglName = agl.get(uc)
        if aglName is not None:
          if aglName in diacriticComps:
            raise Exception('composing same glyph with different names:', aglName, glyphName)
          print('rename', glyphName, '->', aglName, '(U+%04X)' % uc)
          del diacriticComps[glyphName]
          diacriticComps[aglName] = comp

  lines = []
  for glyphName, comp in diacriticComps.iteritems():
    lines.append(fmtGlyphComposition(glyphName, *comp))
  # print('\n'.join(lines))
  print('Write', diacriticsFilename)
  if not dryRun:
    with open(diacriticsFilename, 'w') as f:
      for line in lines:
        f.write(line + '\n')




main()
