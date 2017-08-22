#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os
import sys
import argparse
import json
import plistlib
import re
from collections import OrderedDict
from textwrap import TextWrapper
from StringIO import StringIO
from ConfigParser import RawConfigParser
from fontTools import ttLib
from robofab.objects.objectsRF import RFont, OpenFont

# from feaTools import parser as feaParser
# from feaTools.parser import parseFeatures
# from feaTools import FDKSyntaxFeatureWriter
# from fontbuild.features import updateFeature, compileFeatureRE

# Regex matching "default" glyph names, like "uni2043" and "u01C5"
uniNameRe = re.compile(r'^u(?:ni)[0-9A-F]{4,8}$')


def defaultGlyphName(uc):
  return 'uni%04X' % uc

def defaultGlyphName2(uc):
  return 'u%04X' % uc


def isDefaultGlyphName(name):
  return True if uniNameRe.match(name) else False


def isDefaultGlyphNameForUnicode(name, uc):
  return name == defaultGlyphName(uc) or name == defaultGlyphName2(uc)


def getFirstNonDefaultGlyphName(uc, names):
  for name in names:
    if not isDefaultGlyphNameForUnicode(name, uc):
      return name
  return None


def getTTGlyphList(font): # -> { 'Omega': [2126, ...], ... }
  if isinstance(font, str):
    font = ttLib.TTFont(font)

  if not 'cmap' in font:
    raise Exception('missing cmap table')
  
  gl = {}
  bestCodeSubTable = None
  bestCodeSubTableFormat = 0

  for st in font['cmap'].tables:
    if st.platformID == 0: # 0=unicode, 1=mac, 2=(reserved), 3=microsoft
      if st.format > bestCodeSubTableFormat:
        bestCodeSubTable = st
        bestCodeSubTableFormat = st.format

  if bestCodeSubTable is not None:
    for cp, glyphname in bestCodeSubTable.cmap.items():
      if glyphname in gl:
        gl[glyphname].append(cp)
      else:
        gl[glyphname] = [cp]

  return gl, font


def getUFOGlyphList(font): # -> { 'Omega': [2126, ...], ... }
  # Note: font.getCharacterMapping() returns {2126:['Omega', ...], ...}
  gl = {}
  for g in font:
    ucv = g.unicodes
    if len(ucv) > 0:
      gl[g.name] = ucv
  return gl


def appendNames(uc2names, extraUc2names, uc, name, isDestination):
  if uc in uc2names:
    names = uc2names[uc]
    if name not in names:
      names.append(name)
  elif isDestination:
    uc2names[uc] = [name]
  else:
    if uc in extraUc2names:
      names = extraUc2names[uc]
      if name not in names:
        names.append(name)
    else:
      extraUc2names[uc] = [name]


def buildGlyphNames(dstFonts, srcFonts, glyphOrder, fallbackGlyphNames):
  # fallbackGlyphNames: { 2126: 'Omega', ...}
  uc2names = {}       # { 2126: ['Omega', 'Omegagreek', ...], ...}
  extraUc2names = {}  # { 2126: ['Omega', 'Omegagreek', ...], ...}
                      #   -- codepoints in Nth fonts, not found in first font
  name2ucsv = []      # [ { 'Omega': [2126, ...] }, ... ] -- same order as fonts

  fontIndex = 0
  for font in dstFonts + srcFonts:
    gl = None
    if isinstance(font, RFont):
      print('Inspecting', font.info.familyName, font.info.styleName)
      gl = getUFOGlyphList(font)
    else:
      print('Inspecting', font)
      gl, font = getTTGlyphList(font)

    name2ucsv.append(gl)

    isDestination = fontIndex < len(dstFonts)

    for name, unicodes in gl.iteritems():
      # if len(uc2names) > 100: break
      for uc in unicodes:
        appendNames(uc2names, extraUc2names, uc, name, isDestination)
        if isDestination:
          fallbackName = fallbackGlyphNames.get(uc)
          if fallbackName is not None:
            appendNames(uc2names, extraUc2names, uc, fallbackName, isDestination)

    fontIndex += 1

  # for name in glyphOrder:
  #   if len(name) > 7 and name.startswith('uni') and name.find('.') == -1 and name.find('_') == -1:
  #     try:
  #       print('name: %r, %r' % (name, name[3:]))
  #       uc = int(name[3:], 16)
  #       appendNames(uc2names, extraUc2names, uc, name, isDestination=True)
  #     except:
  #       print()
  #       pass

  return uc2names, extraUc2names, name2ucsv


def renameStrings(listofstrs, newNames):
  v = []
  for s in listofstrs:
    s2 = newNames.get(s)
    if s2 is not None:
      s = s2
    v.append(s)
  return v


def renameUFOLib(ufoPath, newNames, dryRun=False, print=print):
  filename = os.path.join(ufoPath, 'lib.plist')
  plist = plistlib.readPlist(filename)
  
  glyphOrder = plist.get('public.glyphOrder')
  if glyphOrder is not None:
    plist['public.glyphOrder'] = renameStrings(glyphOrder, newNames)

  roboSort = plist.get('com.typemytype.robofont.sort')
  if roboSort is not None:
    for entry in roboSort:
      if isinstance(entry, dict) and entry.get('type') == 'glyphList':
        asc = entry.get('ascending')
        desc = entry.get('descending')
        if asc is not None:
          entry['ascending'] = renameStrings(asc, newNames)
        if desc is not None:
          entry['descending'] = renameStrings(desc, newNames)

  print('Writing', filename)
  if not dryRun:
    plistlib.writePlist(plist, filename)


def renameUFOGroups(ufoPath, newNames, dryRun=False, print=print):
  filename = os.path.join(ufoPath, 'groups.plist')

  plist = None
  try:
    plist = plistlib.readPlist(filename)
  except:
    return

  didChange = False

  for groupName, glyphNames in plist.items():
    for i in range(len(glyphNames)):
      name = glyphNames[i]
      if name in newNames:
        didChange = True
        glyphNames[i] = newNames[name]

  if didChange:
    print('Writing', filename)
    if not dryRun:
      plistlib.writePlist(plist, filename)


def renameUFOKerning(ufoPath, newNames, dryRun=False, print=print):
  filename = os.path.join(ufoPath, 'kerning.plist')

  plist = None
  try:
    plist = plistlib.readPlist(filename)
  except:
    return

  didChange = False

  newPlist = {}
  for leftName, right in plist.items():
    if leftName in newNames:
      didChange = True
      leftName = newNames[leftName]
    newRight = {}
    for rightName, kernValue in plist.items():
      if rightName in newNames:
        didChange = True
        rightName = newNames[rightName]
      newRight[rightName] = kernValue
    newPlist[leftName] = right

  if didChange:
    print('Writing', filename)
    if not dryRun:
      plistlib.writePlist(newPlist, filename)


def subFeaName(m, newNames, state):
  try:
    int(m[3], 16)
  except:
    return m[0]
  
  name = m[2]

  if name in newNames:
    # print('sub %r => %r' % (m[0], m[1] + newNames[name] + m[4]))
    if name == 'uni0402':
      print('sub %r => %r' % (m[0], m[1] + newNames[name] + m[4]))
    state['didChange'] = True
    return m[1] + newNames[name] + m[4]
  
  return m[0]


FEA_TOK = 'tok'
FEA_SEP = 'sep'
FEA_END = 'end'

def feaTokenizer(feaText):
  separators = set('; \t\r\n,[]\'"')
  tokStartIndex = -1
  sepStartIndex = -1

  for i in xrange(len(feaText)):
    ch = feaText[i]
    if ch in separators:
      if tokStartIndex != -1:
        yield (FEA_TOK, feaText[tokStartIndex:i])
        tokStartIndex = -1
      if sepStartIndex == -1:
        sepStartIndex = i
    else:
      if sepStartIndex != -1:
        yield (FEA_SEP, feaText[sepStartIndex:i])
        sepStartIndex = -1
      if tokStartIndex == -1:
        tokStartIndex = i

  if sepStartIndex != -1 and tokStartIndex != -1:
    yield (FEA_END, feaText[min(sepStartIndex, tokStartIndex):])
  elif sepStartIndex != -1:
    yield (FEA_END, feaText[sepStartIndex:])
  elif tokStartIndex != -1:
    yield (FEA_END, feaText[tokStartIndex:])
  else:
    yield (FEA_END, '')


def renameUFOFeatures(font, ufoPath, newNames, dryRun=False, print=print):
  filename = os.path.join(ufoPath, 'features.fea')

  feaText = ''
  try:
    with open(filename, 'r') as f:
      feaText = f.read()
  except:
    return

  didChange = False
  feaText2 = ''

  for t, v in feaTokenizer(feaText):
    if t is FEA_TOK and len(v) > 6 and v.startswith('uni'):
      if v in newNames:
        # print('sub', v, newNames[v])
        didChange = True
        v = newNames[v]
    feaText2 += v

  feaText = feaText2

  if didChange:
    print('Writing', filename)
    if not dryRun:
      with open(filename, 'w') as f:
        f.write(feaText)
    print(
      'Important: you need to manually verify that', filename, 'looks okay.',
      'We did an optimistic update which is not perfect.'
    )

  # classes = feaParser.classDefinitionRE.findall(feaText)
  # for precedingMark, className, classContent in classes:
  #   content = feaParser.classContentRE.findall(classContent)
  #   print('class', className, content)

  #   didChange = False
  #   content2 = []
  #   for name in content:
  #     if name in newNames:
  #       didChange = True
  #       content2.append(newNames[name])
  #   if didChange:
  #     print('content2', content2)
  #     feaText = feaParser.classDefinitionRE.sub('', feaText)

  # featureTags = feaParser.feature_findAll_RE.findall(feaText)
  # for precedingMark, featureTag in featureTags:
  #   print('feat', featureTag)


def renameUFODetails(font, ufoPath, newNames, dryRun=False, print=print):
  renameUFOLib(ufoPath, newNames, dryRun, print)
  renameUFOGroups(ufoPath, newNames, dryRun, print)
  renameUFOKerning(ufoPath, newNames, dryRun, print)
  renameUFOFeatures(font, ufoPath, newNames, dryRun, print)


def readLines(filename):
  with open(filename, 'r') as f:
    return f.read().strip().splitlines()


def readGlyphOrderFile(filename):
  names = []
  for line in readLines(filename):
    line = line.lstrip()
    if len(line) > 0 and line[0] != '#':
      names.append(line)
  return names


def renameGlyphOrderFile(filename, newNames, dryRun=False, print=print):
  lines = []
  didRename = False
  for line in readLines(filename):
    line = line.lstrip()
    if len(line) > 0 and line[0] != '#':
      newName = newNames.get(line)
      if newName is not None:
        didRename = True
        line = newName
    lines.append(line)
  if didRename:
    print('Writing', filename)
    if not dryRun:
      with open(filename, 'w') as f:
        f.write('\n'.join(lines))


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


def renameDiacriticsFile(filename, newNames, dryRun=False, print=print):
  lines = []
  didRename = False
  for line in readLines(filename):
    line = line.strip()
    if len(line) > 0 and line[0] != '#':
      glyphName, baseName, accentNames, offset = parseGlyphComposition(line)

      # rename
      glyphName = newNames.get(glyphName, glyphName)
      baseName = newNames.get(baseName, baseName)
      for accentTuple in accentNames:
        accentTuple[0] = newNames.get(accentTuple[0], accentTuple[0])

      line2 = fmtGlyphComposition(glyphName, baseName, accentNames, offset)

      if line != line2:
        line = line2
        didRename = True
        # print(line, '=>', line2)

    lines.append(line)

  if didRename:
    print('Writing', filename)
    if not dryRun:
      with open(filename, 'w') as f:
        f.write('\n'.join(lines))


def configFindResFile(config, basedir, name):
  fn = os.path.join(basedir, config.get("res", name))
  if not os.path.isfile(fn):
    basedir = os.path.dirname(basedir)
    fn = os.path.join(basedir, config.get("res", name))
    if not os.path.isfile(fn):
      fn = None
  return fn


def renameConfigFile(config, filename, newNames, dryRun=False, print=print):
  wrapper = TextWrapper()
  wrapper.width = 80
  wrapper.break_long_words = False
  wrapper.break_on_hyphens = False

  wrap = lambda names: '\n'.join(wrapper.wrap(' '.join(names)))

  didRename = False
  for propertyName, values in config.items('glyphs'):
    glyphNames = values.split()
    # print(propertyName, glyphNames)
    propChanged = False
    for name in glyphNames:
      if name in newNames:
        sectionChanged = True
    if sectionChanged:
      config.set('glyphs', propertyName, wrap(glyphNames)+'\n')
      didRename = True

    # config.set(section, option, value)
  if didRename:
    s = StringIO()
    config.write(s)
    s = s.getvalue()
    s = re.sub(r'\n(\w+)\s+=\s*', '\n\\1: ', s, flags=re.M)
    s = re.sub(r'((?:^|\n)\[[^\]]*\])', '\\1\n', s, flags=re.M)
    s = re.sub(r'\n\t\n', '\n\n', s, flags=re.M)
    s = s.strip() + '\n'
    print('Writing', filename)
    if not dryRun:
      with open(filename, 'w') as f:
        f.write(s)


def parseAGL(filename):  # -> { 2126: 'Omega', ... }
  m = {}
  for line in readLines(filename):
    # Omega;2126
    # dalethatafpatah;05D3 05B2   # higher-level combinations; ignored
    line = line.strip()
    if len(line) > 0 and line[0] != '#':
      name, uc = tuple([c.strip() for c in line.split(';')])
      if uc.find(' ') == -1:
        # it's a 1:1 mapping
        m[int(uc, 16)] = name
  return m


def main():
  argparser = argparse.ArgumentParser(description='Enrich UFO glyphnames')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    '-list-missing', dest='listMissing', action='store_const', const=True, default=False,
    help='List glyphs with unicodes found in source files but missing in any of the target UFOs.')

  argparser.add_argument(
    '-list-unnamed', dest='listUnnamed', action='store_const', const=True, default=False,
    help="List glyphs with unicodes in target UFOs that don't have symbolic names.")

  argparser.add_argument(
    '-backfill-agl', dest='backfillWithAgl', action='store_const', const=True, default=False,
    help="Use glyphnames from Adobe Glyph List for any glyphs that no names in any of"+
         " the input font files")

  argparser.add_argument(
    '-src', dest='srcFonts', metavar='<fontfile>', type=str, nargs='*',
    help='TrueType, OpenType or UFO fonts to gather glyph info from. '+
         'Names found in earlier-listed fonts are prioritized over later listings.')

  argparser.add_argument(
    'dstFonts', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args()

  # Load UFO fonts
  dstFonts = []
  dstFontPaths = {} # keyed by RFont object
  srcDir = None
  for fn in args.dstFonts:
    fn = fn.rstrip('/')
    font = OpenFont(fn)
    dstFonts.append(font)
    dstFontPaths[font] = fn
    srcDir2 = os.path.dirname(fn)
    if srcDir is None:
      srcDir = srcDir2
    elif srcDir != srcDir2:
      raise Exception('All <ufofile>s must be rooted in same directory')

  # load fontbuild configuration
  config = RawConfigParser(dict_type=OrderedDict)
  configFilename = os.path.join(srcDir, 'fontbuild.cfg')
  config.read(configFilename)
  glyphOrderFile = configFindResFile(config, srcDir, 'glyphorder')
  diacriticsFile = configFindResFile(config, srcDir, 'diacriticfile')
  glyphOrder = readGlyphOrderFile(glyphOrderFile)
  
  fallbackGlyphNames = {}  # { 2126: 'Omega', ... }
  if args.backfillWithAgl:
    fallbackGlyphNames = parseAGL(configFindResFile(config, srcDir, 'agl_glyphlistfile'))
  
  # find glyph names
  uc2names, extraUc2names, name2ucsv = buildGlyphNames(
    dstFonts,
    args.srcFonts,
    glyphOrder,
    fallbackGlyphNames
  )
  # Note: name2ucsv has same order as parameters to buildGlyphNames

  if args.listMissing:
    print('# Missing glyphs: (found in -src but not in any <ufofile>)')
    for uc, names in extraUc2names.iteritems():
      print('U+%04X\t%s' % (uc, ', '.join(names)))
    return

  elif args.listUnnamed:
    print('# Unnamed glyphs:')
    unnamed = set()
    for name in glyphOrder:
      if len(name) > 7 and name.startswith('uni'):
        unnamed.add(name)
    for gl in name2ucsv[:len(dstFonts)]:
      for name, ucs in gl.iteritems():
        for uc in ucs:
          if isDefaultGlyphNameForUnicode(name, uc):
            unnamed.add(name)
            break
    for name in unnamed:
      print(name)
    return

  printDry = lambda *args: print(*args)
  if args.dryRun:
    printDry = lambda *args: print('[dry-run]', *args)
  
  newNames = {}
  renameGlyphsQueue = {} # keyed by RFont object

  for font in dstFonts:
    renameGlyphsQueue[font] = {}

  for uc, names in uc2names.iteritems():
    if len(names) < 2:
      continue
    dstGlyphName = names[0]
    if isDefaultGlyphNameForUnicode(dstGlyphName, uc):
      newGlyphName = getFirstNonDefaultGlyphName(uc, names[1:])
      # if newGlyphName is None:
      #   # if we found no symbolic name, check in fallback list
      #   newGlyphName = fallbackGlyphNames.get(uc)
      #   if newGlyphName is not None:
      #     printDry('Using fallback %s' % newGlyphName)
      if newGlyphName is not None:
        printDry('Rename %s -> %s' % (dstGlyphName, newGlyphName))
        for font in dstFonts:
          if dstGlyphName in font:
            renameGlyphsQueue[font][dstGlyphName] = newGlyphName
        newNames[dstGlyphName] = newGlyphName

  if len(newNames) == 0:
    printDry('No changes')
    return

  # rename component instances
  for font in dstFonts:
    componentMap = font.getReverseComponentMapping()
    for currName, newName in renameGlyphsQueue[font].iteritems():
      for depName in componentMap.get(currName, []):
        depG = font[depName]
        for c in depG.components:
          if c.baseGlyph == currName:
            c.baseGlyph = newName
            c.setChanged()

  # rename glyphs
  for font in dstFonts:
    for currName, newName in renameGlyphsQueue[font].iteritems():
      font[currName].name = newName

  # save fonts and update font data
  for font in dstFonts:
    fontPath = dstFontPaths[font]
    printDry('Saving %d glyphs in %s' % (len(newNames), fontPath))
    if not args.dryRun:
      font.save()
    renameUFODetails(font, fontPath, newNames, dryRun=args.dryRun, print=printDry)

  # update resource files
  renameGlyphOrderFile(glyphOrderFile, newNames, dryRun=args.dryRun, print=printDry)
  renameDiacriticsFile(diacriticsFile, newNames, dryRun=args.dryRun, print=printDry)
  renameConfigFile(config, configFilename, newNames, dryRun=args.dryRun, print=printDry)


if __name__ == '__main__':
  main()
