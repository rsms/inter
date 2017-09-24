#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib, re
from collections import OrderedDict
from ConfigParser import RawConfigParser
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont
import cleanup_kerning


dryRun = False


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


def main(argv=sys.argv):
  argparser = ArgumentParser(description='Remove glyphs from UFOs')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    '-decompose', dest='decompose', action='store_const', const=True, default=False,
    help='When deleting a glyph which is used as a component by another glyph '+
         'which is not being deleted, instead of refusing to delete the glyph, '+
         'decompose the component instances in other glyphs.')

  argparser.add_argument(
    'fontPath', metavar='<ufopath>', type=str, help='Path to UFO font to modify')

  argparser.add_argument(
    'glyphs', metavar='<glyph>', type=str, nargs='+',
    help='Glyph to remove. '+
         'Can be a glyphname, '+
         'a Unicode code point formatted as "U+<CP>", '+
         'or a Unicode code point range formatted as "U+<CP>-<CP>"')

  args = argparser.parse_args()
  dryRun = args.dryRun

  print('Loading glyph data...')
  font = OpenFont(args.fontPath)
  ucmap = font.getCharacterMapping()  # { 2126: [ 'Omega', ...], ...}
  cnmap = font.getReverseComponentMapping()  # { 'A' : ['Aacute', 'Aring'], 'acute' : ['Aacute'] ... }

  glyphnames = set(getGlyphNamesFromArgs(font, ucmap, args.glyphs))

  if len(glyphnames) == 0:
    print('None of the glyphs requested exist in', args.fontPath)
    return

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
        'using them, or not delete the glyphs at all.\n')
      for gname, dependants in cnConflicts.iteritems():
        print('%s used by %s' % (gname, ', '.join(dependants)))
      sys.exit(1)

  # find orphaned pure-components
  for gname in glyphnames:
    g = font[gname]
    useCount = 0
    for cn in g.components:
      usedBy = cnmap.get(cn.baseGlyph)
      if usedBy:
        usedBy = [name for name in usedBy if name not in glyphnames]
        if len(usedBy) == 0:
          cng = font[cn.baseGlyph]
          if len(cng.unicodes) == 0:
            print('Note: pure-component %s becomes orphaned' % cn.baseGlyph)

  # remove glyphs from UFO
  print('Removing %d glyphs' % len(glyphnames))

  libPlistFilename = os.path.join(args.fontPath, 'lib.plist')
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

  if not dryRun:
    print('Writing changes to %s' % args.fontPath)
    font.save()
    plistlib.writePlist(libPlist, libPlistFilename)
  else:
    print('Writing changes to %s (dry run)' % args.fontPath)

  print('Cleaning up kerning')
  if dryRun:
    cleanup_kerning.main(['-dry', args.fontPath])
  else:
    cleanup_kerning.main([args.fontPath])

  print('\n————————————————————————————————————————————————————\n'+
        'Removed %d glyphs:\n  %s' % (
          len(glyphnames), '\n  '.join(sorted(glyphnames))))

  print('\n————————————————————————————————————————————————————\n\n'+
        'You now need to manually remove any occurances of these glyphs in\n'+
        'src/features.fea and\n'+
        '%s/features.fea\n' % args.fontPath)


if __name__ == '__main__':
  main()
