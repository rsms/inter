#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib, json
from collections import OrderedDict
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from fontTools import ttLib
from robofab.objects.objectsRF import OpenFont


def getTTCharMap(font): # -> { 2126: 'Omegagreek', ...}
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
      if cp in gl:
        raise Exception('duplicate unicode-to-glyphname mapping: U+%04X => %r and %r' % (
          cp, glyphname, gl[cp]))
      gl[cp] = glyphname

  return gl


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


def getGlyphNameDifferenceMap(srcCharMap, dstCharMap, dstRevCharMap):
  m = {} # { 'Omegagreek': 'Omega', ... }
  for uc, srcName in srcCharMap.iteritems():
    dstNames = dstCharMap.get(uc)
    if dstNames is not None and len(dstNames) > 0:
      if len(dstNames) != 1:
        print('warning: ignoring multi-glyph map for U+%04X in source font' % uc)
      dstName = dstNames[0]
      if srcName != dstName and srcName not in dstRevCharMap:
        # Only include names that differ. also, The `srcName not in dstRevCharMap` condition
        # makes sure that we don't rename glyphs that are already valid.
        m[srcName] = dstName
  return m


def fixupGroups(fontPath, dstGlyphNames, srcToDstMap, dryRun, stats):
  filename = os.path.join(fontPath, 'groups.plist')
  groups = plistlib.readPlist(filename)
  groups2 = {}
  glyphToGroups = {}

  for groupName, glyphNames in groups.iteritems():
    glyphNames2 = []
    for glyphName in glyphNames:
      if glyphName in srcToDstMap:
        gn2 = srcToDstMap[glyphName]
        stats.renamedGlyphs[glyphName] = gn2
        glyphName = gn2
      if glyphName in dstGlyphNames:
        glyphNames2.append(glyphName)
        glyphToGroups[glyphName] = glyphToGroups.get(glyphName, []) + [groupName]
      else:
        stats.removedGlyphs.add(glyphName)
    if len(glyphNames2) > 0:
      groups2[groupName] = glyphNames2
    else:
      stats.removedGroups.add(groupName)

  print('Writing', filename)
  if not dryRun:
    plistlib.writePlist(groups2, filename)

  return groups2, glyphToGroups


def fixupKerning(fontPath, dstGlyphNames, srcToDstMap, groups, glyphToGroups, dryRun, stats):
  filename = os.path.join(fontPath, 'kerning.plist')
  kerning = plistlib.readPlist(filename)
  kerning2 = {}
  groupPairs = {}  # { "lglyphname+lglyphname": ("lgroupname"|"", "rgroupname"|"", 123) }
  # pairs = {} # { "name+name" => 123 }

  for leftName, right in kerning.items():
    leftIsGroup = leftName[0] == '@'
    leftGroupNames = None

    if leftIsGroup:
      # left is a group
      if leftName not in groups:
        # dead group -- skip
        stats.removedGroups.add(leftName)
        continue
      leftGroupNames = groups[leftName]
    else:
      if leftName in srcToDstMap:
        leftName2 = srcToDstMap[leftName]
        stats.renamedGlyphs[leftName] = leftName2
        leftName = leftName2
      if leftName not in dstGlyphNames:
        # dead glyphname -- skip
        stats.removedGlyphs.add(leftName)
        continue

    right2 = {}
    rightGroupNamesAndValues = []
    for rightName, kerningValue in right.iteritems():
      rightIsGroup = rightName[0] == '@'
      if rightIsGroup:
        if leftIsGroup and leftGroupNames is None:
          leftGroupNames = [leftName]
        if rightName in groups:
          right2[rightName] = kerningValue
          rightGroupNamesAndValues.append((groups[rightName], rightName, kerningValue))
        else:
          stats.removedGroups.add(rightName)
      else:
        if rightName in srcToDstMap:
          rightName2 = srcToDstMap[rightName]
          stats.renamedGlyphs[rightName] = rightName2
          rightName = rightName2
        if rightName in dstGlyphNames:
          right2[rightName] = kerningValue
          if leftIsGroup:
            rightGroupNamesAndValues.append(([rightName], '', kerningValue))
        else:
          stats.removedGlyphs.add(rightName)

    if len(right2):
      kerning2[leftName] = right2

      # update groupPairs 
      lgroupname = leftName if rightIsGroup else ''
      if leftIsGroup:
        for lname in leftGroupNames:
          kPrefix = lname + '+'
          for rnames, rgroupname, kernv in rightGroupNamesAndValues:
            for rname in rnames:
              k = kPrefix + rname
              v = (lgroupname, rgroupname, kernv)
              if k in groupPairs:
                raise Exception('duplicate group pair %s: %r and %r' % (k, groupPairs[k], v))
              groupPairs[k] = v

    elif leftIsGroup:
      stats.removedGroups.add(leftName)
    else:
      stats.removedGlyphs.add(leftName)

  # print('groupPairs:', groupPairs)

  # remove individual pairs that are already represented through groups
  kerning = kerning2
  kerning2 = {}
  for leftName, right in kerning.items():
    leftIsGroup = leftName[0] == '@'
    # leftNames = groups[leftName] if leftIsGroup else [leftName]

    if not leftIsGroup:
      right2 = {}
      for rightName, kernVal in right.iteritems():
        rightIsGroup = rightName[0] == '@'
        if not rightIsGroup:
          k = leftName + '+' + rightName
          if k in groupPairs:
            groupPair = groupPairs[k]
            print(('simplify individual pair %r: kern %r (individual) -> %r (group)') % (
                  k, kernVal, groupPair[2]))
            stats.simplifiedKerningPairs.add(k)
          else:
            right2[rightName] = kernVal
        else:
          right2[rightName] = kernVal
    else:
      # TODO, probably
      right2 = right

    kerning2[leftName] = right2

  print('Writing', filename)
  if not dryRun:
    plistlib.writePlist(kerning2, filename)

  return kerning2


def loadJSONCharMap(filename):
  m = None
  if filename == '-':
    m = json.load(sys.stdin)
  else:
    with open(filename, 'r') as f:
      m = json.load(f)
  if not isinstance(m, dict):
    raise Exception('json root is not a dict')
  if len(m) > 0:
    for k, v in m.iteritems():
      if not isinstance(k, int) and not isinstance(k, float):
        raise Exception('json dict key is not a number')
      if not isinstance(v, str):
        raise Exception('json dict value is not a string')
      break
  return m


class Stats:
  def __init__(self):
    self.removedGroups = set()
    self.removedGlyphs = set()
    self.simplifiedKerningPairs = set()
    self.renamedGlyphs = {}


def configFindResFile(config, basedir, name):
  fn = os.path.join(basedir, config.get("res", name))
  if not os.path.isfile(fn):
    basedir = os.path.dirname(basedir)
    fn = os.path.join(basedir, config.get("res", name))
    if not os.path.isfile(fn):
      fn = None
  return fn


def main():
  jsonSchemaDescr = '{[unicode:int]: glyphname:string, ...}'

  argparser = ArgumentParser(
    description='Rename glyphnames in UFO kerning and remove unused groups and glyphnames.')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    '-no-stats', dest='noStats', action='store_const', const=True, default=False,
    help='Do not print statistics at the end.')

  argparser.add_argument(
    '-save-stats', dest='saveStatsPath', metavar='<file>', type=str,
    help='Write detailed statistics to JSON file.')

  argparser.add_argument(
    '-src-json', dest='srcJSONFile', metavar='<file>', type=str,
    help='JSON file to read glyph names from.'+
         ' Expected schema: ' + jsonSchemaDescr + ' (e.g. {2126: "Omega"})')

  argparser.add_argument(
    '-src-font', dest='srcFontFile', metavar='<file>', type=str,
    help='TrueType or OpenType font to read glyph names from.')

  argparser.add_argument(
    'dstFontsPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args()
  dryRun = args.dryRun

  if args.srcJSONFile and args.srcFontFile:
    argparser.error('Both -src-json and -src-font specified -- please provide only one.')

  # Strip trailing slashes from font paths
  args.dstFontsPaths = [s.rstrip('/ ') for s in args.dstFontsPaths]

  # Load source char map
  srcCharMap = None
  if args.srcJSONFile:
    try:
      srcCharMap = loadJSONCharMap(args.srcJSONFile)
    except Exception as err:
      argparser.error('Invalid JSON: Expected schema %s (%s)' % (jsonSchemaDescr, err))
  elif args.srcFontFile:
    srcCharMap = getTTCharMap(args.srcFontFile.rstrip('/ '))  # -> { 2126: 'Omegagreek', ...}
  else:
    argparser.error('No source provided (-src-* argument missing)')
  if len(srcCharMap) == 0:
    print('Empty character map', file=sys.stderr)
    sys.exit(1)

  # Find project source dir
  srcDir = ''
  for dstFontPath in args.dstFontsPaths:
    s = os.path.dirname(dstFontPath)
    if not srcDir:
      srcDir = s
    elif srcDir != s:
      raise Exception('All <ufofile>s must be rooted in the same directory')

  # Load font project config
  # load fontbuild configuration
  config = RawConfigParser(dict_type=OrderedDict)
  configFilename = os.path.join(srcDir, 'fontbuild.cfg')
  config.read(configFilename)
  diacriticsFile = configFindResFile(config, srcDir, 'diacriticfile')

  for dstFontPath in args.dstFontsPaths:
    dstFont = OpenFont(dstFontPath)
    dstCharMap = dstFont.getCharacterMapping() # -> { 2126: [ 'Omega', ...], ...}
    dstRevCharMap = revCharMap(dstCharMap) # { 'Omega': 2126, ...}
    srcToDstMap = getGlyphNameDifferenceMap(srcCharMap, dstCharMap, dstRevCharMap)

    stats = Stats()

    groups, glyphToGroups = fixupGroups(dstFontPath, dstRevCharMap, srcToDstMap, dryRun, stats)
    fixupKerning(dstFontPath, dstRevCharMap, srcToDstMap, groups, glyphToGroups, dryRun, stats)

    # stats
    if args.saveStatsPath or not args.noStats:
      if not args.noStats:
        print('stats for %s:' % dstFontPath)
        print('  Deleted %d groups and %d glyphs.' % (
          len(stats.removedGroups), len(stats.removedGlyphs)))
        print('  Renamed %d glyphs.' % len(stats.renamedGlyphs))
        print('  Simplified %d kerning pairs.' % len(stats.simplifiedKerningPairs))
      if args.saveStatsPath:
        statsObj = {
          'deletedGroups': stats.removedGroups,
          'deletedGlyphs': stats.removedGlyphs,
          'simplifiedKerningPairs': stats.simplifiedKerningPairs,
          'renamedGlyphs': stats.renamedGlyphs,
        }
        f = sys.stdout
        try:
          if args.saveStatsPath != '-':
            f = open(args.saveStatsPath, 'w')
          print('Writing stats to', args.saveStatsPath)
          json.dump(statsObj, sys.stdout, indent=2, separators=(',', ': '))
        finally:
          if f is not sys.stdout:
            f.close()


if __name__ == '__main__':
  main()
