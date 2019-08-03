#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, plistlib
from collections import OrderedDict
from argparse import ArgumentParser
from defcon import Font

RIGHT = 1
LEFT = 2


def mapGroups(groups):  # => { glyphname => set(groupname, ...), ... }
  m = OrderedDict()
  for groupname, glyphnames in groups.iteritems():
    for glyphname in glyphnames:
      m.setdefault(glyphname, set()).add(groupname)
  return m


def fmtGlyphname(glyphname, glyph=None):
  if glyph is not None and len(glyphname) == 1 and ord(glyphname[0]) == glyph.unicode:
    # literal, e.g. "A"
    return glyphname
  else:
    # named, e.g. "\Omega"
    return '/' + glyphname + ' '


def printPairs(font, baseSide, baseSideGlyph, otherSideNames, args):
  out = []
  if args.formatAsUnicode:
    base = '\\u%04X' % baseSideGlyph.unicode
    for otherName in otherSideNames:
      if otherName in font:
        otherGlyph = font[otherName]
        if otherGlyph.unicode is not None:
          if baseSide == LEFT:
            out.append('%s\\u%04X' % (base, otherGlyph.unicode))
          else:
            out.append('\\u%04X%s' % (otherGlyph.unicode, base))
  else:
    base = fmtGlyphname(baseSideGlyph.name, baseSideGlyph)
    prefix_uc = ''
    prefix_lc = ''
    suffix_uc = ''
    suffix_lc = ''

    if args.noPrefixAutocase:
      prefix_uc = args.prefix
      prefix_lc = args.prefix
      suffix_uc = args.suffix
      suffix_lc = args.suffix
    else:
      if args.prefix and len(args.prefix) > 0:
        s = unicode(args.prefix)
        if s[0].isupper():
          prefix_uc = args.prefix
          prefix_lc = args.prefix.lower()
        else:
          prefix_uc = args.prefix.upper()
          prefix_lc = args.prefix

      if args.suffix and len(args.suffix) > 0:
        s = unicode(args.suffix)
        if s[0].isupper():
          suffix_uc = args.suffix
          suffix_lc = args.suffix.lower()
        else:
          suffix_uc = args.suffix.upper()
          suffix_lc = args.suffix

    for otherName in otherSideNames:
      if otherName in font:
        otherGlyph = None
        if len(otherName) == 1:
          otherGlyph = font[otherName]
        prefix = prefix_lc
        suffix = suffix_lc
        if unicode(otherName[0]).isupper():
          prefix = prefix_uc
          suffix = suffix_uc
        if baseSide == LEFT:
          out.append('%s%s%s%s' % (
            prefix, base, fmtGlyphname(otherName, otherGlyph), suffix
          ))
        else:
          out.append('%s%s%s%s' % (
            prefix, fmtGlyphname(otherName, otherGlyph), base, suffix
          ))

  print(' '.join(out))


def samplesForGlyphnameR(font, groups, groupmap, kerning, glyphname, args):
  rightGlyph = font[glyphname]
  includeAll = args.includeAllInGroup
  leftnames = set()

  _addLeftnames(groups, kerning, glyphname, leftnames, includeAll)

  if glyphname in groupmap:
    for groupname in groupmap[glyphname]:
      if groupname.find('_RIGHT_') != -1:
        _addLeftnames(groups, kerning, groupname, leftnames, includeAll)

  leftnames = sorted(leftnames)
  printPairs(font, RIGHT, rightGlyph, leftnames, args)


def _addLeftnames(groups, kerning, glyphname, leftnames, includeAll=True):
  # kerning : { leftName => {rightName => kernVal} }
  for leftname, kern in kerning.iteritems():
    if glyphname in kern:
      if leftname[0] == '@':
        for leftname2 in groups[leftname]:
          leftnames.add(leftname2)
          if not includeAll:
            # TODO: in this case, pick the one leftname that has the highest
            # ranking in glyphorder
            break
      else:
        leftnames.add(leftname)


def samplesForGlyphnameL(font, groups, groupmap, kerning, glyphname, args):
  leftGlyph = font[glyphname]
  includeAll = args.includeAllInGroup
  rightnames = set()

  _addRightnames(groups, kerning, glyphname, rightnames, includeAll)

  if glyphname in groupmap:
    for groupname in groupmap[glyphname]:
      if groupname.find('_LEFT_') != -1 or groupname.find('_RIGHT_') == -1:
        _addRightnames(groups, kerning, groupname, rightnames, includeAll)

  rightnames = sorted(rightnames)
  printPairs(font, LEFT, leftGlyph, rightnames, args)


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


def main():
  argparser = ArgumentParser(
    description='Generate kerning samples by providing the left-hand side glyph')

  argparser.add_argument(
    '-u', dest='formatAsUnicode', action='store_const', const=True, default=False,
    help='Format output as unicode escape sequences instead of glyphnames. ' +
         'E.g. "\\u2126" instead of "\\Omega"')

  argparser.add_argument(
    '-prefix', dest='prefix', metavar='<text>', type=str,
    help='Text to append before each pair')

  argparser.add_argument(
    '-suffix', dest='suffix', metavar='<text>', type=str,
    help='Text to append after each pair')

  argparser.add_argument(
    '-no-prefix-autocase', dest='noPrefixAutocase',
    action='store_const', const=True, default=False,
    help='Do not convert -prefix and -suffix to match case')

  argparser.add_argument(
    '-all-in-groups', dest='includeAllInGroup',
    action='store_const', const=True, default=False,
    help='Include all glyphs for groups rather than just the first glyph listed.')

  argparser.add_argument(
    '-left', dest='asLeft',
    action='store_const', const=True, default=False,
    help='Only include pairs where the glyphnames are on the left side.')

  argparser.add_argument(
    '-right', dest='asRight',
    action='store_const', const=True, default=False,
    help='Only include pairs where the glyphnames are on the right side.'+
    ' When neither -left or -right is provided, include all pairs.')

  argparser.add_argument(
    'fontPath', metavar='<ufofile>', type=str, help='UFO font source')

  argparser.add_argument(
    'glyphnames', metavar='<glyphname>', type=str, nargs='+',
    help='Name of glyphs to generate samples for. '+
         'You can also provide a Unicode code point using the syntax "U+XXXX"')

  args = argparser.parse_args()

  font = Font(args.fontPath)

  groupsFilename = os.path.join(args.fontPath, 'groups.plist')
  kerningFilename = os.path.join(args.fontPath, 'kerning.plist')

  groups = plistlib.readPlist(groupsFilename)   # { groupName => [glyphName] }
  kerning = plistlib.readPlist(kerningFilename) # { leftName => {rightName => kernVal} }
  groupmap = mapGroups(groups) # { glyphname => set(groupname, ...), ... }

  if not args.asLeft and not args.asRight:
    args.asLeft = True
    args.asRight = True

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
    if args.asLeft:
      samplesForGlyphnameL(font, groups, groupmap, kerning, glyphname, args)
    if args.asRight:
      samplesForGlyphnameR(font, groups, groupmap, kerning, glyphname, args)


main()
