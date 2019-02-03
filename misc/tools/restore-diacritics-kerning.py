#!/usr/bin/env python
# encoding: utf8
# 
# This script was used specifically to re-introduce a bunch of kerning values
# that where lost in an old kerning cleanup that failed to account for
# automatically composed glyphs defined in diacritics.txt.
#
# Steps:
#  1. git diff 10e15297b 10e15297b^ > 10e15297b.diff
#  2. edit 10e15297b.diff and remove the python script add
#  3. fetch copies of kerning.plist and groups.plist from before the loss change
#     bold-groups.plist
#     bold-kerning.plist
#     regular-groups.plist
#     regular-kerning.plist
#  4. run this script
# 
from __future__ import print_function
import os, sys, plistlib, json
from collections import OrderedDict
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from fontTools import ttLib
from robofab.objects.objectsRF import OpenFont


srcFontPaths = ['src/Inter-Regular.ufo', 'src/Inter-Bold.ufo']


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


def loadGlyphCompositions(filename):
  compositions = OrderedDict()
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if len(line) > 0 and line[0] != '#':
        glyphName, baseName, accentNames, offset = parseGlyphComposition(line)
        compositions[glyphName] = (baseName, accentNames, offset)
  return compositions


def loadNamesFromDiff(diffFilename):
  with open(diffFilename, 'r') as f:
    diffLines = [s.strip() for s in f.read().splitlines() if s.startswith('+\t')]
  diffLines = [s for s in diffLines if not s.startswith('<int')]
  namesInDiff = set()
  for s in diffLines:
    if s.startswith('<int') or s.startswith('<arr') or s.startswith('</'):
      continue
    p = s.find('>')
    if p != -1:
      p2 = s.find('<', p+1)
      if p2 != -1:
        name = s[p+1:p2]
        try:
          int(name)
        except:
          if not name.startswith('@'):
            namesInDiff.add(s[p+1:p2])
  return namesInDiff


def loadGroups(filename):
  groups = plistlib.readPlist(filename)
  nameMap = {}  # { glyphName => set(groupName) }
  for groupName, glyphNames in groups.iteritems():
    for glyphName in glyphNames:
      nameMap.setdefault(glyphName, set()).add(groupName)
  return groups, nameMap


def loadKerning(filename):
  kerning = plistlib.readPlist(filename)
  # <dict>
  #   <key>@KERN_LEFT_A</key>
  #   <dict>
  #     <key>@KERN_RIGHT_C</key>
  #     <integer>-96</integer>

  leftIndex = {}  # { glyph-name => <ref to plist right-hand side dict> }
  rightIndex = {} # { glyph-name => [(left-hand-side-name, kernVal), ...] }
  rightGroupIndex = {} # { group-name => [(left-hand-side-name, kernVal), ...] }

  for leftName, right in kerning.iteritems():
    if leftName[0] != '@':
      leftIndex[leftName] = right

    for rightName, kernVal in right.iteritems():
      if rightName[0] != '@':
        rightIndex.setdefault(rightName, []).append((leftName, kernVal))
      else:
        rightGroupIndex.setdefault(rightName, []).append((leftName, kernVal))

  return kerning, leftIndex, rightIndex, rightGroupIndex


def loadAltNamesDB(agl, fontFilename):
  uc2names = {}  # { 2126: ['Omega', ...], ...}
  name2ucs = {}  # { 'Omega': [2126, ...], ...}

  name2ucs, _ = getTTGlyphList(fontFilename)
    # -> { 'Omega': [2126, ...], ... }
  for name, ucs in name2ucs.iteritems():
    for uc in ucs:
      uc2names.setdefault(uc, []).append(name)

  for uc, name in agl.iteritems():
    name2ucs.setdefault(name, []).append(uc)
    uc2names.setdefault(uc, []).append(name)
    # -> { 2126: 'Omega', ... }

  return uc2names, name2ucs


def loadLocalNamesDB(agl, diacriticComps): # { 2126: ['Omega', ...], ...}
  uc2names = None

  for fontPath in srcFontPaths:
    font = OpenFont(fontPath)
    if uc2names is None:
      uc2names = font.getCharacterMapping()  # { 2126: ['Omega', ...], ...}
    else:
      for uc, names in font.getCharacterMapping().iteritems():
        names2 = uc2names.get(uc, [])
        for name in names:
          if name not in names2:
            names2.append(name)
        uc2names[uc] = names2

  # agl { 2126: 'Omega', ...} -> { 'Omega': [2126, ...], ...}
  aglName2Ucs = {}
  for uc, name in agl.iteritems():
    aglName2Ucs.setdefault(name, []).append(uc)

  for glyphName, comp in diacriticComps.iteritems():
    for uc in aglName2Ucs.get(glyphName, []):
      names = uc2names.get(uc, [])
      if glyphName not in names:
        names.append(glyphName)
      uc2names[uc] = names

  name2ucs = {}
  for uc, names in uc2names.iteritems():
    for name in names:
      name2ucs.setdefault(name, set()).add(uc)

  return uc2names, name2ucs


def _canonicalGlyphName(name, localName2ucs, localUc2Names, altName2ucs):
  ucs = localName2ucs.get(name)
  if ucs:
    return name, list(ucs)[0]
  ucs = altName2ucs.get(name)
  if ucs:
    for uc in ucs:
      localNames = localUc2Names.get(uc)
      if localNames and len(localNames):
        return localNames[0], uc
  return None, None


def main():
  argparser = ArgumentParser(description='Restore lost kerning')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    'srcFont', metavar='<fontfile>', type=str,
    help='TrueType, OpenType or UFO fonts to gather glyph info from')

  argparser.add_argument(
    'diffFile', metavar='<diffile>', type=str, help='Diff file')

  args = argparser.parse_args()

  dryRun = args.dryRun

  agl = parseAGL('src/glyphlist.txt')
  diacriticComps = loadGlyphCompositions('src/diacritics.txt')

  altUc2names, altName2ucs = loadAltNamesDB(agl, args.srcFont)
  localUc2Names, localName2ucs = loadLocalNamesDB(agl, diacriticComps)

  canonicalGlyphName = lambda name: _canonicalGlyphName(
    name, localName2ucs, localUc2Names, altName2ucs)

  deletedNames = loadNamesFromDiff(args.diffFile)  # 10e15297b.diff
  deletedDiacriticNames = OrderedDict()

  for glyphName, comp in diacriticComps.iteritems():
    if glyphName in deletedNames:
      deletedDiacriticNames[glyphName] = comp


  for fontPath in srcFontPaths:
    addedGroupNames = set()

    oldFilenamePrefix = 'regular'
    if fontPath.find('Bold') != -1:
      oldFilenamePrefix = 'bold'
    oldGroups, oldNameToGroups = loadGroups(
      oldFilenamePrefix + '-groups.plist')
    oldKerning, oldLIndex, oldRIndex, oldRGroupIndex = loadKerning(
      oldFilenamePrefix + '-kerning.plist')
      # lIndex : { name => <ref to plist right-hand side dict> }
      # rIndex : { name => [(left-hand-side-name, kernVal), ...] }

    currGroupFilename = os.path.join(fontPath, 'groups.plist')
    currKerningFilename = os.path.join(fontPath, 'kerning.plist')
    currGroups, currNameToGroups = loadGroups(currGroupFilename)
    currKerning, currLIndex, currRIndex, currRGroupIndex = loadKerning(currKerningFilename)

    for glyphName, comp in deletedDiacriticNames.iteritems():
      oldGroupMemberships = oldNameToGroups.get(glyphName)
      localGlyphName, localUc = canonicalGlyphName(glyphName)

      # if glyphName != 'dcaron':
      #   continue # XXX DEBUG

      if localGlyphName is None:
        # glyph does no longer exist -- ignore
        print('[IGNORE]', glyphName)
        continue

      if oldGroupMemberships:
        # print('group', localGlyphName,
        #   '=>', localUc,
        #   'in old group:', oldGroupMemberships, ', curr group:', currGroupMemberships)
        for oldGroupName in oldGroupMemberships:
          currGroup = currGroups.get(oldGroupName) # None|[glyphname, ...]
          # print('GM ', localGlyphName, oldGroupName, len(currGroup) if currGroup else 0)
          if currGroup is not None:
            if localGlyphName not in currGroup:
              # print('[UPDATE group]', oldGroupName, 'append', localGlyphName)
              currGroup.append(localGlyphName)
          else:
            # group does not currently exist
            if currNameToGroups.get(localGlyphName):
              raise Exception('TODO: case where glyph is in some current groups, but not the' +
                              'original-named group')
            print('[ADD group]', oldGroupName, '=> [', localGlyphName, ']')
            currGroups[oldGroupName] = [localGlyphName]
            addedGroupNames.add(oldGroupName)
            # if oldGroupName in oldKerning:
            #   print('TODO: effects of oldGroupName being in oldKerning:',
            #     oldKerning[oldGroupName])
            if oldGroupName in oldRGroupIndex:
              print('TODO: effects of oldGroupName being in oldRGroupIndex:',
                oldRGroupIndex[oldGroupName])

      else: # if not oldGroupMemberships
        ucs = localName2ucs.get(glyphName)
        if not ucs:
          raise Exception(
            'TODO non-group, non-local name ' + glyphName + ' -- lookup in alt names')

        asLeft = oldLIndex.get(glyphName)
        atRightOf = oldRIndex.get(glyphName)

        # print('individual', glyphName,
        #   '=>', ', '.join([str(uc) for uc in ucs]),
        #   '\n as left:', asLeft is not None,
        #   '\n at right of:', atRightOf is not None)

        if asLeft:
          currKern = currKerning.get(localGlyphName)
          if currKern is None:
            rightValues = {}
            for rightName, kernValue in asLeft.iteritems():
              if rightName[0] == '@':
                currGroup = currGroups.get(rightName)
                if currGroup and localGlyphName not in currGroup:
                  rightValues[rightName] = kernValue
              else:
                localName, localUc = canonicalGlyphName(rightName)
                if localName:
                  rightValues[localName] = kernValue
            if len(rightValues) > 0:
              print('[ADD currKerning]', localGlyphName, '=>', rightValues)
              currKerning[localGlyphName] = rightValues

        if atRightOf:
          for parentLeftName, kernVal in atRightOf:
            # print('atRightOf:', parentLeftName, kernVal)
            if parentLeftName[0] == '@':
              if parentLeftName in currGroups:
                k = currKerning.get(parentLeftName)
                if k:
                  if localGlyphName not in k:
                    print('[UPDATE currKerning g]',
                      parentLeftName, '+= {', localGlyphName, ':', kernVal, '}')
                    k[localGlyphName] = kernVal
                else:
                  print('TODO: left-group is NOT in currKerning; left-group', parentLeftName)
            else:
              localParentLeftGlyphName, _ = canonicalGlyphName(parentLeftName)
              if localParentLeftGlyphName:
                k = currKerning.get(localParentLeftGlyphName)
                if k:
                  if localGlyphName not in k:
                    print('[UPDATE currKerning i]',
                      localParentLeftGlyphName, '+= {', localGlyphName, ':', kernVal, '}')
                    k[localGlyphName] = kernVal
                else:
                  print('[ADD currKerning i]',
                      localParentLeftGlyphName, '=> {', localGlyphName, ':', kernVal, '}')
                  currKerning[localParentLeftGlyphName] = {localGlyphName: kernVal}


    for groupName in addedGroupNames:
      print('————————————————————————————————————————————')
      print('re-introduce group', groupName, 'to kerning')
      
      oldRKern = oldKerning.get(groupName)
      if oldRKern is not None:
        newRKern = {}
        for oldRightName, kernVal in oldRKern.iteritems():
          if oldRightName[0] == '@':
            if oldRightName in currGroups:
              newRKern[oldRightName] = kernVal
            else:
              # Note: (oldRightName in addedGroupNames) should always be False here
              # as we would have added it to currGroups already.
              print('[DROP group]', oldRightName, kernVal)
              if oldRightName in currGroups:
                del currGroups[oldRightName]
          else:
            localGlyphName, _ = canonicalGlyphName(oldRightName)
            if localGlyphName:
              newRKern[localGlyphName] = kernVal
              print('localGlyphName', localGlyphName)

        if len(newRKern):
          print('[ADD currKerning g]', groupName, newRKern)
          currKerning[groupName] = newRKern

      # oldRGroupIndex : { group-name => [(left-hand-side-name, kernVal), ...] }
      oldLKern = oldRGroupIndex.get(groupName)
      if oldLKern:
        for oldRightName, kernVal in oldLKern:
          if oldRightName[0] == '@':
            if oldRightName in currGroups:
              k = currKerning.get(oldRightName)
              if k is not None:
                print('[UPDATE kerning g]', oldRightName, '+= {', groupName, ':', kernVal, '}')
                k[groupName] = kernVal
              else:
                currKerning[oldRightName] = {groupName: kernVal}
                print('[ADD kerning g]', oldRightName, '= {', groupName, ':', kernVal, '}')
          else:
            localGlyphName, _ = canonicalGlyphName(oldRightName)
            if localGlyphName:
              k = currKerning.get(localGlyphName)
              if k is not None:
                print('[UPDATE kerning i]', localGlyphName, '+= {', groupName, ':', kernVal, '}')
                k[groupName] = kernVal
              else:
                currKerning[localGlyphName] = {groupName: kernVal}
                print('[ADD kerning i]', localGlyphName, '= {', groupName, ':', kernVal, '}')


    print('Write', currGroupFilename)
    if not dryRun:
      plistlib.writePlist(currGroups, currGroupFilename)

    print('Write', currKerningFilename)
    if not dryRun:
      plistlib.writePlist(currKerning, currKerningFilename)

    # end: for fontPath

main()
