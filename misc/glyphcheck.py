#!/usr/bin/env python
# encoding: utf8
import sys, argparse
from fontTools import ttLib


def main():
  argparser = argparse.ArgumentParser(description='Check glyph names')

  argparser.add_argument('fontfiles', metavar='<path>', type=str, nargs='+',
                         help='TrueType or OpenType font files')

  args = argparser.parse_args()

  nmissing = 0

  matchnames = set()
  for line in sys.stdin:
    line = line.strip()
    if len(line) > 0 and line[0] != '#':
      for line2 in line.split():
        line2 = line2.strip()
        if len(line2) > 0:
          matchnames.add(line2)

  for fontfile in args.fontfiles:
    font = ttLib.TTFont(fontfile)
    glyphnames = set(font.getGlyphOrder())

    # for name in glyphnames:
    #   if not name in matchnames:
    #     print('%s missing in input' % name)

    for name in matchnames:
      if not name in glyphnames:
        print('%s missing in font' % name)
        nmissing = nmissing + 1


  if nmissing == 0:
    print('all glyphs found')


if __name__ == '__main__':
  main()
