#!/usr/bin/env python
# encoding: utf8
#
# Grab http://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
#
from __future__ import print_function
import os, sys
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont
from unicode_util import parseUnicodeDataFile, MainCategories as UniMainCategories

lightBlueColor = (0.86, 0.92, 0.97, 1.0)
lightTealColor = (0.8, 0.94, 0.95, 1.0)
lightYellowColor = (0.97, 0.95, 0.83, 1.0)
lightPurpleColor = (0.93, 0.9, 0.98, 1.0)
lightGreyColor = (0.94, 0.94, 0.94, 1.0)
mediumGreyColor = (0.87, 0.87, 0.87, 1.0)
lightGreenColor = (0.89, 0.96, 0.92, 1.0)
mediumGreenColor = (0.77, 0.95, 0.76, 1.0)
lightRedColor = (0.98, 0.89, 0.89, 1.0)
lightOrangeColor = (1.0, 0.89, 0.82, 1.0)
redColor = (1, 0.3, 0.3, 1)

colorsByGlyphName = [
  (set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'), lightBlueColor), # light blue 1
]

colorsByUCMainCategory = {
  # UniMainCategories.Letter: (1, 1, 1, 1),
  UniMainCategories.Mark: lightRedColor,
  UniMainCategories.Punctuation: lightGreyColor,
  UniMainCategories.Format: lightGreyColor,
  UniMainCategories.Number: lightGreenColor,
  UniMainCategories.Symbol: lightTealColor,
  UniMainCategories.Separator: lightPurpleColor,
  UniMainCategories.Control: redColor,
  UniMainCategories.Surrogate: redColor,
  UniMainCategories.PrivateUse: lightYellowColor,
  UniMainCategories.Unassigned: lightYellowColor,
  UniMainCategories.Other: lightOrangeColor,
}


def colorForGlyph(name, unicodes, ucd):
  for nameSet, color in colorsByGlyphName:
    if name in nameSet:
      return color

  for uc in unicodes:
    cp = ucd.get(uc)
    if cp is None:
      continue
    return colorsByUCMainCategory.get(cp.mainCategory)

  if len(unicodes) == 0:
    if name.find('.cn') != -1:
      # pure component
      return mediumGreenColor
    else:
      # precomposed
      return mediumGreyColor

  return None


def main():
  argparser = ArgumentParser(
    description='Set robofont color marks on glyphs based on unicode categories')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    '-ucd', dest='ucdFile', metavar='<file>', type=str,
    help='UnicodeData.txt file from http://www.unicode.org/')

  argparser.add_argument(
    'fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args()
  dryRun = args.dryRun
  markLibKey = 'com.typemytype.robofont.mark'

  ucd = {}
  if args.ucdFile:
    ucd = parseUnicodeDataFile(args.ucdFile)

  for fontPath in args.fontPaths:
    font = OpenFont(fontPath)
    for g in font:
      rgba = colorForGlyph(g.name, g.unicodes, ucd)
      if rgba is None:
        if markLibKey in g.lib:
          del g.lib[markLibKey]
      else:
        g.lib[markLibKey] = [float(n) for n in rgba]

    print('Write', fontPath)
    if not dryRun:
      font.save()


if __name__ == '__main__':
  main()
