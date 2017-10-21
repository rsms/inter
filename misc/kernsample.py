#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib
from collections import OrderedDict
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont


def mapGroups(groups):  # => { glyphname => set(groupname, ...), ... }
  m = OrderedDict()
  for groupname, glyphnames in groups.iteritems():
    for glyphname in glyphnames:
      m.setdefault(glyphname, set()).add(groupname)
  return m


def _addRightnames(groups, kerning, leftname, rightnames, includeAll=True):
  if leftname in kerning:
    for rightname in kerning[leftname]:
      if rightname[0] == '@':
        for rightname2 in groups[rightname]:
          rightnames.add(rightname2)
          if not includeAll:
            # TODO: in this case, pick the one rightname that has the highest
            # ranking in glyphorder
            break
      else:
        rightnames.add(rightname)


def fmtGlyphname(glyphname, glyph=None):
  if glyph is not None and len(glyphname) == 1 and ord(glyphname[0]) == glyph.unicode:
    # literal, e.g. "A"
    return glyphname
  else:
    # named, e.g. "\Omega"
    return '/' + glyphname + ' '


def samplesForGlyphname(font, groups, groupmap, kerning, glyphname, args):
  leftGlyph = font[glyphname]  # verify it's present
  rightnames = set()

  _addRightnames(groups, kerning, glyphname, rightnames, includeAll=args.includeAllInGroup)

  if glyphname in groupmap:
    for groupname in groupmap[glyphname]:
      _addRightnames(groups, kerning, groupname, rightnames, includeAll=args.includeAllInGroup)

  rightnames = sorted(rightnames)

  out = []
  if args.formatAsUnicode:
    left = '\\u%04X' % leftGlyph.unicode
    for rightname in rightnames:
      if rightname in font:
        rightGlyph = font[rightname]
        if rightGlyph.unicode is not None:
          out.append('%s\\u%04X' % (left, rightGlyph.unicode))
  else:
    left = fmtGlyphname(glyphname, leftGlyph)
    suffix_uc = ''
    suffix_lc = ''
    if args.suffix and len(args.suffix) > 0:
      s = unicode(args.suffix)
      if s[0].isupper():
        suffix_uc = args.suffix
        suffix_lc = args.suffix.lower()
      else:
        suffix_uc = args.suffix.upper()
        suffix_lc = args.suffix
    for rightname in rightnames:
      if rightname in font:
        rightGlyph = None
        if len(rightname) == 1:
          rightGlyph = font[rightname]
        suffix = suffix_lc
        if unicode(rightname[0]).isupper():
          suffix = suffix_uc
        out.append('%s%s%s' % (left, fmtGlyphname(rightname, rightGlyph), suffix))

  print(' '.join(out))




def main():
  argparser = ArgumentParser(
    description='Generate kerning samples by providing the left-hand side glyph')

  argparser.add_argument(
    '-u', dest='formatAsUnicode', action='store_const', const=True, default=False,
    help='Format output as unicode escape sequences instead of glyphnames. ' +
         'E.g. "\\u2126" instead of "\\Omega"')

  argparser.add_argument(
    '-suffix', dest='suffix', metavar='<text>', type=str,
    help='Text to append after each pair')

  argparser.add_argument(
    '-all-in-groups', dest='includeAllInGroup',
    action='store_const', const=True, default=False,
    help='Include all glyphs for groups rather than just the first glyph listed.')

  argparser.add_argument(
    'fontPath', metavar='<ufofile>', type=str, help='UFO font source')

  argparser.add_argument(
    'glyphnames', metavar='<glyphname>', type=str, nargs='+',
    help='Name of glyphs to generate samples for. '+
         'You can also provide a Unicode code point using the syntax "U+XXXX"')

  args = argparser.parse_args()

  font = OpenFont(args.fontPath)

  groupsFilename = os.path.join(args.fontPath, 'groups.plist')
  kerningFilename = os.path.join(args.fontPath, 'kerning.plist')

  groups = plistlib.readPlist(groupsFilename)   # { groupName => [glyphName] }
  kerning = plistlib.readPlist(kerningFilename) # { leftName => {rightName => kernVal} }
  groupmap = mapGroups(groups)

  # expand any unicode codepoints
  glyphnames = []
  for glyphname in args.glyphnames:
    if len(glyphname) > 2 and glyphname[:2] == 'U+':
      cp = int(glyphname[2:], 16)
      ucmap = font.getCharacterMapping()  # { 2126: ['Omega', ...], ...}
      for glyphname2 in ucmap[cp]:
        glyphnames.append(glyphname2)
    else:
      glyphnames.append(glyphname)

  for glyphname in glyphnames:
    samplesForGlyphname(font, groups, groupmap, kerning, glyphname, args)


main()
