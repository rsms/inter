#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib, re, subprocess
from collections import OrderedDict
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont
from textwrap import TextWrapper
from StringIO import StringIO
import glob
import cleanup_kerning


dryRun = False


def readLines(filename):
  with open(filename, 'r') as f:
    return f.read().strip().splitlines()


def decomposeComponentInstances(font, glyph, componentsToDecompose):
  """Moves the components of a glyph to its outline."""
  if len(glyph.components):
    deepCopyContours(font, glyph, glyph, (0, 0), (1, 1), componentsToDecompose)
    glyph.clearComponents()


def deepCopyContours(font, parent, component, offset, scale, componentsToDecompose):
  """Copy contours to parent from component, including nested components."""
  for nested in component.components:
    if componentsToDecompose is None or nested.baseGlyph in componentsToDecompose:
      deepCopyContours(
        font, parent, font[nested.baseGlyph],
        (offset[0] + nested.offset[0], offset[1] + nested.offset[1]),
        (scale[0] * nested.scale[0], scale[1] * nested.scale[1]),
        None)
      component.removeComponent(nested)
  if component == parent:
    return
  for contour in component:
    contour = contour.copy()
    contour.scale(scale)
    contour.move(offset)
    parent.appendContour(contour)


def addGlyphsForCP(cp, ucmap, glyphnames):
  if cp in ucmap:
    for name in ucmap[cp]:
      glyphnames.append(name)
  # else:
  #   print('no glyph for U+%04X' % cp)


def getGlyphNamesFromArgs(font, ucmap, glyphs):
  glyphnames = []
  for s in glyphs:
    if len(s) > 2 and s[:2] == 'U+':
      p = s.find('-')
      if p != -1:
        # range, e.g. "U+1D0A-1DBC"
        cpStart = int(s[2:p], 16)
        cpEnd = int(s[p+1:], 16)
        for cp in range(cpStart, cpEnd):
          addGlyphsForCP(cp, ucmap, glyphnames)
      else:
        # single code point e.g. "U+1D0A"
        cp = int(s[2:], 16)
        addGlyphsForCP(cp, ucmap, glyphnames)
    else:
      glyphnames.append(s)
  return glyphnames


def updateConfigFile(config, filename, rmnames):
  wrapper = TextWrapper()
  wrapper.width = 80
  wrapper.break_long_words = False
  wrapper.break_on_hyphens = False
  wrap = lambda names: '\n'.join(wrapper.wrap(' '.join(names)))

  didChange = False

  for propertyName, values in config.items('glyphs'):
    glyphNames = values.split()
    propChanged = False
    glyphNames2 = [name for name in glyphNames if name not in rmnames]
    if len(glyphNames2) < len(glyphNames):
      print('[fontbuild.cfg] updating glyphs property', propertyName)
      config.set('glyphs', propertyName, wrap(glyphNames2)+'\n')
      didChange = True

  if didChange:
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


def updateDiacriticsFile(filename, rmnames):
  lines = []
  didChange = False

  for line in readLines(filename):
    line = line.strip()
    if len(line) == 0 or len(line.lstrip()) == 0 or line.lstrip()[0] == '#':
      lines.append(line)
    else:
      glyphName, baseName, accentNames, offset = parseGlyphComposition(line)

      skipLine = False
      if baseName in rmnames:
        skipLine = True
      else:
        for names in accentNames:
          for name in names:
            if name in rmnames:
              skipLine = True
              break

      if not skipLine:
        lines.append(line)
      else:
        print('[diacritics] removing', line.strip())
        didChange = True

  if didChange:
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




def main(argv=sys.argv):
  argparser = ArgumentParser(
    description='Remove glyphs from all UFOs in src dir')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    '-decompose', dest='decompose', action='store_const', const=True, default=False,
    help='When deleting a glyph which is used as a component by another glyph '+
         'which is not being deleted, instead of refusing to delete the glyph, '+
         'decompose the component instances in other glyphs.')

  argparser.add_argument(
    '-ignore-git-state', dest='ignoreGitState', action='store_const', const=True, default=False,
    help='Skip checking with git if there are changes to the target UFO file.')

  argparser.add_argument(
    'glyphs', metavar='<glyph>', type=str, nargs='+',
    help='Glyph to remove. '+
         'Can be a glyphname, '+
         'a Unicode code point formatted as "U+<CP>", '+
         'or a Unicode code point range formatted as "U+<CP>-<CP>"')

  args = argparser.parse_args()
  global dryRun
  dryRun = args.dryRun
  BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
  srcDir = os.path.join(BASEDIR, 'src')

  # check if src font has modifications
  if not args.ignoreGitState:
    gitStatus = subprocess.check_output(
      ['git', '-C', BASEDIR, 'status', '-s', '--',
       os.path.relpath(os.path.abspath(srcDir), BASEDIR) ],
      shell=False)
    gitIsDirty = False
    gitStatusLines = gitStatus.splitlines()
    for line in gitStatusLines:
      if len(line) > 3 and line[:2] != '??':
        gitIsDirty = True
        break
    if gitIsDirty:
      if len(gitStatusLines) > 5:
        gitStatusLines = gitStatusLines[:5] + [' ...']
      print(
        ("%s has uncommitted changes. It's strongly recommended to run this "+
         "script on an unmodified UFO path so to allow \"undoing\" any changes. "+
         "Run with -ignore-git-state to ignore this warning.\n%s") % (
         srcDir, '\n'.join(gitStatusLines)),
        file=sys.stderr)
      sys.exit(1)

  # Find UFO fonts
  fontPaths = glob.glob(os.path.join(srcDir, '*.ufo'))
  if len(fontPaths) == 0:
    print('No UFOs found in', srcDir, file=sys.stderr)
    sys.exit(1)

  rmnamesUnion = set()

  for fontPath in fontPaths:
    relFontPath = os.path.relpath(fontPath, BASEDIR)
    print('Loading glyph data for %s...' % relFontPath)
    font = OpenFont(fontPath)
    ucmap = font.getCharacterMapping()  # { 2126: [ 'Omega', ...], ...}
    cnmap = font.getReverseComponentMapping()  # { 'A' : ['Aacute', 'Aring'], 'acute' : ['Aacute'] ... }

    glyphnames = set(getGlyphNamesFromArgs(font, ucmap, args.glyphs))

    if len(glyphnames) == 0:
      print('None of the glyphs requested exist in', relFontPath, file=sys.stderr)

    print('Preparing to remove %d glyphs — resolving component usage...' % len(glyphnames))

    # Check component usage
    cnConflicts = {}
    for gname in glyphnames:
      cnUses = cnmap.get(gname)
      if cnUses:
        extCnUses = [n for n in cnUses if n not in glyphnames]
        if len(extCnUses) > 0:
          cnConflicts[gname] = extCnUses

    if len(cnConflicts) > 0:
      if args.decompose:
        componentsToDecompose = set()
        for gname in cnConflicts.keys():
          componentsToDecompose.add(gname)
        for gname, dependants in cnConflicts.iteritems():
          print('decomposing %s in %s' % (gname, ', '.join(dependants)))
          for depname in dependants:
            decomposeComponentInstances(font, font[depname], componentsToDecompose)
      else:
        print(
          '\nComponent conflicts.\n\n'+
          'Some glyphs to-be deleted are used as components in other glyphs.\n'+
          'You need to either decompose the components, also delete glyphs\n'+
          'using them, or not delete the glyphs at all.\n', file=sys.stderr)
        for gname, dependants in cnConflicts.iteritems():
          print('%s used by %s' % (gname, ', '.join(dependants)), file=sys.stderr)
        sys.exit(1)

    # find orphaned pure-components
    for gname in glyphnames:
      try:
        g = font[gname]
      except:
        print('no glyph %r in %s' % (gname, relFontPath), file=sys.stderr)
        sys.exit(1)
      useCount = 0
      for cn in g.components:
        usedBy = cnmap.get(cn.baseGlyph)
        if usedBy:
          usedBy = [name for name in usedBy if name not in glyphnames]
          if len(usedBy) == 0:
            cng = font[cn.baseGlyph]
            if len(cng.unicodes) == 0:
              print('Note: pure-component %s orphaned' % cn.baseGlyph)

    # remove glyphs from UFO
    print('Removing %d glyphs' % len(glyphnames))

    libPlistFilename = os.path.join(fontPath, 'lib.plist')
    libPlist = plistlib.readPlist(libPlistFilename)
    
    glyphOrder = libPlist.get('public.glyphOrder')
    if glyphOrder is not None:
      v = [name for name in glyphOrder if name not in glyphnames]
      libPlist['public.glyphOrder'] = v

    roboSort = libPlist.get('com.typemytype.robofont.sort')
    if roboSort is not None:
      for entry in roboSort:
        if isinstance(entry, dict) and entry.get('type') == 'glyphList':
          asc = entry.get('ascending')
          if asc is not None:
            entry['ascending'] = [name for name in asc if name not in glyphnames]
          desc = entry.get('descending')
          if desc is not None:
            entry['descending'] = [name for name in desc if name not in glyphnames]

    for gname in glyphnames:
      font.removeGlyph(gname)
      rmnamesUnion.add(gname)

    if not dryRun:
      print('Writing changes to %s' % relFontPath)
      font.save()
      plistlib.writePlist(libPlist, libPlistFilename)
    else:
      print('Writing changes to %s (dry run)' % relFontPath)

    print('Cleaning up kerning')
    if dryRun:
      cleanup_kerning.main(['-dry', fontPath])
    else:
      cleanup_kerning.main([fontPath])

  # end for fontPath in fontPaths


  # fontbuild config
  config = RawConfigParser(dict_type=OrderedDict)
  configFilename = os.path.join(srcDir, 'fontbuild.cfg')
  config.read(configFilename)
  glyphOrderFile = configFindResFile(config, srcDir, 'glyphorder')
  diacriticsFile = configFindResFile(config, srcDir, 'diacriticfile')

  updateDiacriticsFile(diacriticsFile, rmnamesUnion)
  updateConfigFile(config, configFilename, rmnamesUnion)


  print('\n————————————————————————————————————————————————————\n'+
        'Removed %d glyphs:\n  %s' % (
          len(rmnamesUnion), '\n  '.join(sorted(rmnamesUnion))))

  print('\n————————————————————————————————————————————————————\n\n'+
        'You now need to manually remove any occurances of these glyphs in\n'+
        ' src/features.fea\n'+
        ' %s/features.fea\n' % '/features.fea\n '.join(fontPaths))

  print(('You should also re-generate %s via\n'+
         '`make src/glyphorder.txt` (or misc/misc/gen-glyphorder.py)'
        ) % glyphOrderFile)


if __name__ == '__main__':
  main()
