#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib, re
from collections import OrderedDict
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from fontTools import ttLib
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


# def getNameToGroupsMap(groups): # => { glyphName => set(groupName) }
#   nameMap = {}
#   for groupName, glyphNames in groups.iteritems():
#     for glyphName in glyphNames:
#       nameMap.setdefault(glyphName, set()).add(groupName)
#   return nameMap


# def inspectKerning(kerning):
#   leftIndex = {}  # { glyph-name => <ref to plist right-hand side dict> }
#   rightIndex = {} # { glyph-name => [(left-hand-side-name, kernVal), ...] }
#   rightGroupIndex = {} # { group-name => [(left-hand-side-name, kernVal), ...] }
#   for leftName, right in kerning.iteritems():
#     if leftName[0] != '@':
#       leftIndex[leftName] = right
#     for rightName, kernVal in right.iteritems():
#       if rightName[0] != '@':
#         rightIndex.setdefault(rightName, []).append((leftName, kernVal))
#       else:
#         rightGroupIndex.setdefault(rightName, []).append((leftName, kernVal))
#   return leftIndex, rightIndex, rightGroupIndex


class RefTracker:
  def __init__(self):
    self.refs = {}

  def incr(self, name):
    self.refs[name] = self.refs.get(name, 0) + 1

  def decr(self, name): # => bool hasNoRefs
    r = self.refs.get(name)
    
    if r is None:
      raise Exception('decr untracked ref ' + repr(name))
    
    if r < 1:
      raise Exception('decr already zero ref ' + repr(name))
    
    if r == 1:
      del self.refs[name]
      return True

    self.refs[name] = r - 1

  def __contains__(self, name):
    return name in self.refs


def main(argv=None):
  argparser = ArgumentParser(description='Remove unused kerning')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    'fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args(argv)
  dryRun = args.dryRun

  agl = loadAGL('src/glyphlist.txt') # { 2126: 'Omega', ... }
  diacriticComps = loadGlyphCompositions('src/diacritics.txt') # {glyphName => (baseName, a, o)}

  for fontPath in args.fontPaths:
    print(fontPath)

    groupsFilename = os.path.join(fontPath, 'groups.plist')
    kerningFilename = os.path.join(fontPath, 'kerning.plist')

    groups = plistlib.readPlist(groupsFilename)   # { groupName => [glyphName] }
    kerning = plistlib.readPlist(kerningFilename) # { leftName => {rightName => kernVal} }

    font = OpenFont(fontPath)
    uc2names, name2ucs, allNames = loadLocalNamesDB([font], agl, diacriticComps)

    # start with eliminating non-existent glyphs from groups and completely
    # eliminate groups with all-dead glyphs.
    eliminatedGroups = set()
    for groupName, glyphNames in list(groups.items()):
      glyphNames2 = []
      for name in glyphNames:
        if name in allNames:
          glyphNames2.append(name)
        else:
          name2 = canonicalGlyphName(name, uc2names)
          if name2 != name and name2 in allNames:
            print('group: rename glyph', name, '->', name2)
            glyphNames2.append(name2)

      if len(glyphNames2) == 0:
        print('group: eliminate', groupName)
        eliminatedGroups.add(groupName)
        del groups[groupName]
      elif len(glyphNames2) != len(glyphNames):
        print('group: shrink', groupName)
        groups[groupName] = glyphNames2

    # now eliminate kerning
    groupRefs = RefTracker() # tracks group references, so we can eliminate unreachable ones

    for leftName, right in list(kerning.items()):
      leftIsGroup = leftName[0] == '@'

      if leftIsGroup:
        if leftName in eliminatedGroups:
          print('kerning: eliminate LHS', leftName)
          del kerning[leftName]
          continue
        groupRefs.incr(leftName)
      else:
        if leftName not in allNames:
          print('kerning: eliminate LHS', leftName)
          del kerning[leftName]
          continue

      right2 = {}
      for rightName, kernVal in right.iteritems():
        rightIsGroup = rightName[0] == '@'
        if rightIsGroup:
          if rightIsGroup in eliminatedGroups:
            print('kerning: eliminate RHS group', rightName)
          else:
            groupRefs.incr(rightName)
            right2[rightName] = kernVal
        else:
          if rightName not in allNames:
            # maybe an unnamed glyph?
            rightName2 = canonicalGlyphName(rightName, uc2names)
            if rightName2 != rightName:
              print('kerning: rename & update RHS glyph', rightName, '->', rightName2)
              right2[rightName2] = kernVal
            else:
              print('kerning: eliminate RHS glyph', rightName)
          else:
            right2[rightName] = kernVal

      if len(right2) == 0:
        print('kerning: eliminate LHS', leftName)
        del kerning[leftName]
        if leftIsGroup:
          groupRefs.decr(leftName)
      else:
        kerning[leftName] = right2

    # eliminate any unreferenced groups
    for groupName, glyphNames in list(groups.items()):
      if not groupName in groupRefs:
        print('group: eliminate unreferenced group', groupName)
        del groups[groupName]


    # verify that there are no conflicting kerning pairs
    pairs = {} # { key => [...] }
    conflictingPairs = set()

    for leftName, right in kerning.iteritems():
      # expand LHS group -> names
      topLeftName = leftName
      for leftName in groups[leftName] if leftName[0] == '@' else [leftName]:
        if leftName not in allNames:
          raise Exception('unknown LHS glyph name ' + repr(leftName))
        keyPrefix = leftName + '+'
        for rightName, kernVal in right.iteritems():
          # expand RHS group -> names
          topRightName = rightName
          for rightName in groups[rightName] if rightName[0] == '@' else [rightName]:
            if rightName not in allNames:
              raise Exception('unknown RHS glyph name ' + repr(rightName))
            # print(leftName, '+', rightName, '=>', kernVal)
            key = keyPrefix + rightName
            isConflict = key in pairs
            pairs.setdefault(key, []).append(( topLeftName, topRightName, kernVal ))
            if isConflict:
              conflictingPairs.add(key)

    # # resolve pair conflicts by preferring pairs defined via group kerning
    # for key in conflictingPairs:
    #   pairs = pairs[key]
    #   print('kerning: conflicting pairs %r: %r' % (key, pairs))
    #   bestPair = None
    #   redundantPairs = []
    #   for pair in pairs:
    #     leftName, rightName, kernVal = pair
    #     if bestPair is None:
    #       bestPair = pair
    #     else:
    #       bestLeftName, bestRightName, _ = bestPair
    #       bestScore = 0
    #       score = 0
    #       if bestLeftName[0] == '@': bestScore += 1
    #       if bestRightName[0] == '@': bestScore += 1
    #       if leftName[0] == '@': score += 1
    #       if rightName[0] == '@': score += 1
    #       if bestScore == 2:
    #         # doesn't get better than this
    #         break
    #       elif score > bestScore:
    #         redundantPairs.append(bestPair)
    #         bestPair = pair
    #       else:
    #         redundantPairs.append(pair)
    #   print('- keeping', bestPair)
    #   print('- eliminating', redundantPairs)
    #   for redundantPairs


    # # eliminate any unreferenced groups
    # for groupName, glyphNames in list(groups.items()):
    #   if not groupName in groupRefs:
    #     print('group: eliminate unreferenced group', groupName)
    #     del groups[groupName]


    print('Write', groupsFilename)
    if not dryRun:
      plistlib.writePlist(groups, groupsFilename)

    print('Write', kerningFilename)
    if not dryRun:
      plistlib.writePlist(kerning, kerningFilename)

  # [end] for fontPath in args.fontPaths


if __name__ == '__main__':
  main()
