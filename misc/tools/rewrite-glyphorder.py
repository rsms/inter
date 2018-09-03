#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib, json, re
from collections import OrderedDict
from argparse import ArgumentParser
from ConfigParser import RawConfigParser
from fontTools import ttLib
from robofab.objects.objectsRF import OpenFont


# Regex matching "default" glyph names, like "uni2043" and "u01C5"
uniNameRe = re.compile(r'^u(?:ni)([0-9A-F]{4,8})$')


class PList:
  def __init__(self, filename):
    self.filename = filename
    self.plist = None

  def load(self):
    self.plist = plistlib.readPlist(self.filename)

  def save(self):
    if self.plist is not None:
      plistlib.writePlist(self.plist, self.filename)

  def get(self, k, defaultValue=None):
    if self.plist is None:
      self.load()
    return self.plist.get(k, defaultValue)

  def __getitem__(self, k):
    if self.plist is None:
      self.load()
    return self.plist[k]

  def __setitem__(self, k, v):
    if self.plist is None:
      self.load()
    self.plist[k] = v

  def __delitem__(self, k):
    if self.plist is None:
      self.load()
    del self.plist[k]


def parseAGL(filename):  # -> { 2126: 'Omega', ... }
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


def revCharMap(ucToNames):
  # {2126:['Omega','Omegagr']} -> {'Omega':2126, 'Omegagr':2126}
  # {2126:'Omega'} -> {'Omega':2126}
  m = {}
  if len(ucToNames) == 0:
    return m

  lists = True
  for v in ucToNames.itervalues():
    lists = not isinstance(v, str)
    break

  if lists:
    for uc, names in ucToNames.iteritems():
      for name in names:
        m[name] = uc
  else:
    for uc, name in ucToNames.iteritems():
      m[name] = uc
    
  return m


def loadJSONGlyphOrder(jsonFilename):
  gol = None
  if jsonFilename == '-':
    gol = json.load(sys.stdin)
  else:
    with open(jsonFilename, 'r') as f:
      gol = json.load(f)
  if not isinstance(gol, list):
    raise Exception('expected [[string, int|null]')
  if len(gol) > 0:
    for v in gol:
      if not isinstance(v, list):
        raise Exception('expected [[string, int|null]]')
      break
  return gol


def loadTTGlyphOrder(font):
  if isinstance(font, str):
    font = ttLib.TTFont(font)

  if not 'cmap' in font:
    raise Exception('missing cmap table')
  
  bestCodeSubTable = None
  bestCodeSubTableFormat = 0

  for st in font['cmap'].tables:
    if st.platformID == 0: # 0=unicode, 1=mac, 2=(reserved), 3=microsoft
      if st.format > bestCodeSubTableFormat:
        bestCodeSubTable = st
        bestCodeSubTableFormat = st.format

  ucmap = {}
  if bestCodeSubTable is not None:
    for cp, glyphname in bestCodeSubTable.cmap.items():
      ucmap[glyphname] = cp

  gol = []
  for name in font.getGlyphOrder():
    gol.append((name, ucmap.get(name)))

  return gol


def loadSrcGlyphOrder(jsonFilename, fontFilename):  # -> [ ('Omegagreek', 2126|None), ...]
  if jsonFilename:
    return loadJSONGlyphOrder(jsonFilename)
  elif fontFilename:
    return loadTTGlyphOrder(fontFilename.rstrip('/ '))
  return None


def loadUFOGlyphNames(ufoPath):
  font = OpenFont(ufoPath)

  libPlist = PList(os.path.join(ufoPath, 'lib.plist'))  
  orderedNames = libPlist['public.glyphOrder']  # [ 'Omega', ...]
  
  # append any glyphs that are missing in orderedNames
  allNames = set(font.keys())
  for name in orderedNames:
    allNames.discard(name)
  for name in allNames:
    orderedNames.append(name)
  
  ucToNames = font.getCharacterMapping()  # { 2126: [ 'Omega', ...], ...}
  nameToUc = revCharMap(ucToNames) # { 'Omega': 2126, ...}

  gol = OrderedDict()  # OrderedDict{ ('Omega', 2126|None), ...}
  for name in orderedNames:
    gol[name] = nameToUc.get(name)
    # gol.append((name, nameToUc.get(name)))

  return gol, ucToNames, nameToUc, libPlist


def saveUFOGlyphOrder(libPlist, orderedNames, dryRun):
  libPlist['public.glyphOrder'] = orderedNames

  roboSort = libPlist.get('com.typemytype.robofont.sort')
  if roboSort is not None:
    # lib['com.typemytype.robofont.sort'] has schema
    # [ { type: "glyphList", ascending: [glyphname, ...] }, ...]
    for i in range(len(roboSort)):
      ent = roboSort[i]
      if isinstance(ent, dict) and ent.get('type') == 'glyphList':
        roboSort[i] = {'type':'glyphList', 'ascending':orderedNames}
        break

  print('Writing', libPlist.filename)
  if not dryRun:
    libPlist.save()


def getConfigResFile(config, basedir, name):
  fn = os.path.join(basedir, config.get("res", name))
  if not os.path.isfile(fn):
    basedir = os.path.dirname(basedir)
    fn = os.path.join(basedir, config.get("res", name))
    if not os.path.isfile(fn):
      fn = None
  return fn


def main():
  argparser = ArgumentParser(description='Rewrite glyph order of UFO fonts')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    '-src-json', dest='srcJSONFile', metavar='<file>', type=str,
    help='JSON file to read glyph order from.' +
         ' Should be a list e.g. [["Omega", 2126], [".notdef", null], ...]')

  argparser.add_argument(
    '-src-font', dest='srcFontFile', metavar='<file>', type=str,
    help='TrueType or OpenType font to read glyph order from.')

  argparser.add_argument(
    '-out', dest='outFile', metavar='<file>', type=str,
    help='Write each name per line to <file>')

  argparser.add_argument(
    'dstFontsPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args()
  dryRun = args.dryRun

  if args.srcJSONFile and args.srcFontFile:
    argparser.error('Both -src-json and -src-font specified -- please provide only one.')

  srcGol = loadSrcGlyphOrder(args.srcJSONFile, args.srcFontFile)
  if srcGol is None:
    argparser.error('No source provided (-src-* argument missing)')

  # Load Adobe Glyph List database
  srcDir = os.path.dirname(args.dstFontsPaths[0])
  config = RawConfigParser(dict_type=OrderedDict)
  config.read(os.path.join(srcDir, 'fontbuild.cfg'))
  aglUcToName = parseAGL(getConfigResFile(config, srcDir, 'agl_glyphlistfile'))
  aglNameToUc = revCharMap(aglUcToName)

  glyphorderUnion = OrderedDict()

  for dstFontPath in args.dstFontsPaths:
    glyphOrder, ucToNames, nameToUc, libPlist = loadUFOGlyphNames(dstFontPath)

    newGol = OrderedDict()
    for name, uc in srcGol:

      if uc is None:
        # if there's no unicode associated, derive from name if possible
        m = uniNameRe.match(name)
        if m:
          try:
            uc = int(m.group(1), 16)
          except:
            pass
        if uc is None:
          uc = aglNameToUc.get(name)

      # has same glyph mapped to same unicode
      names = ucToNames.get(uc)
      if names is not None:
        for name in names:
          # print('U  %s  U+%04X' % (name, uc))
          newGol[name] = uc
        continue
      
      # has same name in dst?
      uc2 = glyphOrder.get(name)
      if uc2 is not None:
        # print('N  %s  U+%04X' % (name, uc2))
        newGol[name] = uc2
        continue

      # Try AGL[uc] -> name == name
      if uc is not None:
        name2 = aglUcToName.get(uc)
        if name2 is not None:
          uc2 = glyphOrder.get(name2)
          if uc2 is not None:
            # print('A  %s  U+%04X' % (name2, uc2))
            newGol[name2] = uc2
            continue
      
      # else: ignore glyph name in srcGol not found in target
      # if uc is None:
      #   print('x  %s  -' % name)
      # else:
      #   print('x  %s  U+%04X' % (name, uc))


    # add remaining glyphs from original glyph order
    for name, uc in glyphOrder.iteritems():
      if name not in newGol:
        # print('E  %s  U+%04X' % (name, uc))
        newGol[name] = uc

    orderedNames = []
    for name in newGol.iterkeys():
      orderedNames.append(name)
      glyphorderUnion[name] = True

    saveUFOGlyphOrder(libPlist, orderedNames, dryRun)

  if args.outFile:
    print('Write', args.outFile)
    glyphorderUnionNames = glyphorderUnion.keys()
    if not dryRun:
      with open(args.outFile, 'w') as f:
        f.write('\n'.join(glyphorderUnionNames) + '\n')


if __name__ == '__main__':
  main()
