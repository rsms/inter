#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont
from math import ceil, floor

dryRun = False
numNames = [
  'zero','one','two','three','four','five','six','seven','eight','nine'
]


def main():
  argparser = ArgumentParser(
    description='Generate tabular number glyphs from regular number glyphs')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    'fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts')

  args = argparser.parse_args()
  dryRun = args.dryRun

  # Strip trailing slashes from font paths and iterate
  for fontPath in [s.rstrip('/ ') for s in args.fontPaths]:
    fontName = os.path.basename(fontPath)
    font = OpenFont(fontPath)

    # Find widest glyph
    width = 0
    for name in numNames:
      g = font[name]
      width = max(width, g.width)

    print('[%s] tnums width:' % fontName, width)

    # Create tnum glyphs
    for name in numNames:
      g = font[name]

      tnum = font.newGlyph(name + '.tnum')
      tnum.width = width

      # calculate component x-offset
      xoffs = 0
      if g.width != width:
        print('[%s] gen (adjust width)' % fontName, tnum.name)
        # center shape, ignoring existing margins
        # xMin, yMin, xMax, yMax = g.box
        # graphicWidth = xMax - xMin
        # leftMargin = round((width - graphicWidth) / 2)
        # xoffs = leftMargin - g.leftMargin

        # adjust margins
        widthDelta = width - g.width
        leftMargin  = g.leftMargin + int(floor(widthDelta / 2))
        rightMargin = g.rightMargin + int(ceil(widthDelta / 2))
        xoffs = leftMargin - g.leftMargin
      else:
        print('[%s] gen (same width)' % fontName, tnum.name)

      tnum.appendComponent(name, (xoffs, 0))

    if dryRun:
      print('[%s] save [dry run]' % fontName)
    else:
      print('[%s] save' % fontName)
      font.save()


if __name__ == '__main__':
  main()
