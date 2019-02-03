#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib, re
from collections import OrderedDict
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont
from fontTools.feaLib.parser import Parser as FeaParser
from fontTools.feaLib.builder import Builder as FeaBuilder
from fontTools.ttLib import TTFont


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


def loadLocalNamesDB(fonts, agl, diacriticComps):
  uc2names = None  # { 2126: ['Omega', ...], ...}
  allNames = set() # set('Omega', ...)

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
      allNames.add(g.name)

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
      allNames.add(glyphName)
    else:
      allNames.add(glyphName)
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



includeRe = re.compile(r'^include\(([^\)]+)\);\s*$')


def loadFeaturesFile(filepath):
  print('read', filepath)
  lines = []
  with open(filepath, 'r') as f:
    for line in f:
      m = includeRe.match(line)
      if m is not None:
        includedFilename = m.group(1)
        includedPath = os.path.normpath(os.path.join(os.path.dirname(filepath), includedFilename))
        lines = lines + loadFeaturesFile(includedPath)
      else:
        lines.append(line)
  return lines


def main():
  argparser = ArgumentParser(description='Fixup features.fea')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    'fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args()
  dryRun = args.dryRun

  agl = loadAGL('src/glyphlist.txt') # { 2126: 'Omega', ... }
  diacriticComps = loadGlyphCompositions('src/diacritics.txt') # {glyphName => (baseName, a, o)}

  # collect glyph names
  fonts = [OpenFont(fontPath) for fontPath in args.fontPaths]
  uc2names, name2ucs, allNames = loadLocalNamesDB(fonts, agl, diacriticComps)

  includeRe = re.compile(r'^include\(([^\)]+)\);\s*$')

  # open features.fea
  featuresLines = loadFeaturesFile(os.path.join(fontPath, 'features.fea'))

  classDefRe = re.compile(r'^@([^\s=]+)\s*=\s*\[([^\]]+)\]\s*;\s*$')
  subRe = re.compile(r'^\s*sub\s+(.+)(\'?)\s+by\s+(.+)\s*;\s*$')
  sub2Re = re.compile(r'^\s*sub\s+([^\[]+)\s+\[\s*([^\]]+)\s*\](\'?)\s+by\s+(.+)\s*;\s*$')
  # sub lmidtilde [uni1ABB uni1ABD uni1ABE]' by uni1ABE.w2;
  # sub lmidtilde uni1ABC' by uni1ABC.w2;
  spacesRe = re.compile(r'[\s\r\n]+')

  classDefs = {}
  featuresLines2 = []

  for line in featuresLines:
    clsM = classDefRe.match(line)
    if clsM is not None:
      clsName = clsM.group(1)
      names = spacesRe.split(clsM.group(2).strip())
      if clsName in classDefs:
        raise Exception('duplicate class definition ' + clsName)
      # print('classdef', clsName, ' '.join(names))
      # print('classdef', clsName)
      names2 = []
      for name in names:
        if name == '-':
          # e.g. A - Z
          names2.append(name)
          continue
        if name[0] != '@':
          canonName = canonicalGlyphName(name, uc2names)
          if canonName != name:
            # print('renaming ' + name + ' -> ' + canonName)
            names2.append(canonName)
          elif name not in allNames:
            print('skipping unknown glyph ' + name)
          else:
            names2.append(name)
        else:
          raise Exception('todo: class-ref ' + name + ' in class-def ' + clsName)
      classDefs[clsName] = names2
      line = '@%s = [ %s ];' % (clsName, ' '.join(names2))
      featuresLines2.append(line)
      continue


    # sub2M = sub2Re.match(line)
    # if sub2M is not None:
    #   findNames1 = spacesRe.split(sub2M.group(1))
    #   findNames2 = spacesRe.split(sub2M.group(2))
    #   apos = sub2M.group(3)
    #   rightName = sub2M.group(4)
    #   print('TODO: sub2', findNames1, findNames2, apos, rightName)
    #   featuresLines2.append(line)
    #   continue


    sub2M = sub2Re.match(line)
    subM = None
    if sub2M is None:
      subM = subRe.match(line)
    if subM is not None or sub2M is not None:
      findNamesStr = ''
      findNamesHasBrackets = False
      findNames = []

      findNamesBStr = ''
      findNamesBHasBrackets = False
      findNamesB = []

      newNamesStr = ''
      newNamesHasBrackets = False
      newNames = []

      apos0 = ''

      if subM is not None:
        findNamesStr = subM.group(1)        
        apos0 = subM.group(2)
        newNamesStr = subM.group(3)
      else: # sub2M
        findNamesStr = sub2M.group(1)
        findNamesBStr = sub2M.group(2)
        apos0 = sub2M.group(3)
        newNamesStr = sub2M.group(4)

      if newNamesStr[0] == '[':
        newNamesHasBrackets = True
        newNamesStr = newNamesStr.strip('[ ]')
      newNames = spacesRe.split(newNamesStr)

      if findNamesStr[0] == '[':
        findNamesHasBrackets = True
        findNamesStr = findNamesStr.strip('[ ]')
      findNames = spacesRe.split(findNamesStr)

      if findNamesBStr != '':
        if findNamesBStr[0] == '[':
          findNamesBHasBrackets = True
          findNamesBStr = findNamesBStr.strip('[ ]')
        findNamesB = spacesRe.split(findNamesBStr)


      names22 = []
      for names in [findNames, findNamesB, newNames]:
        names2 = []
        for name in names:
          if name[0] == '@':
            clsName = name[1:].rstrip("'")
            if clsName not in classDefs:
              raise Exception('sub: missing target class ' + clsName + ' at\n' + line)
            names2.append(name)
          else:
            apos = name[-1] == "'"
            if apos:
              name = name[:-1]
            if name not in allNames:
              canonName = canonicalGlyphName(name, uc2names)
              if canonName != name:
                print('renaming ' + name + ' -> ' + canonName)
                name = canonName
              else:
                raise Exception('TODO: unknown name', name)
                # if we remove names, we also need to remove subs (that become empty), and so on.
            if apos:
              name += "'"
            names2.append(name)
        names22.append(names2)

      findNames2, findNamesB2, newNames2 = names22

      findNamesStr = ' '.join(findNames2)
      if findNamesHasBrackets: findNamesStr = '[' + findNamesStr + ']'

      if findNamesBStr != '':
        findNamesBStr = ' '.join(findNamesB2)
        if findNamesBHasBrackets: findNamesBStr = '[' + findNamesBStr + ']'

      newNamesStr = ' '.join(newNames2)
      if newNamesHasBrackets: newNamesStr = '[' + newNamesStr + ']'

      if subM is not None:
        line = '  sub %s%s by %s;' % (findNamesStr, apos0, newNamesStr)
      else:
      # if subM is None:
        # sub bbar [uni1ABB uni1ABD uni1ABE]' by uni1ABE.w2;
        line = '  sub %s [%s]%s by %s;' % (findNamesStr, findNamesBStr, apos0, newNamesStr)

    featuresLines2.append(line)


  print('Write', featuresFilename)
  if not dryRun:
    with open(featuresFilename + '2', 'w') as f:
      for line in featuresLines2:
        f.write(line + '\n')

    # FeaParser(featuresFilename + '2', allNames).parse()

    # font = TTFont('build/const/Inter-Regular.otf')
    # FeaBuilder(font, featuresFilename + '2').build()





main()
