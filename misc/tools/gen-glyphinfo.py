#!/usr/bin/env python
# encoding: utf8
#
# Grab http://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
#
import os, sys
from os.path import dirname, basename, abspath, relpath, join as pjoin
sys.path.append(abspath(pjoin(dirname(__file__), 'tools')))
from common import BASEDIR, getVersion, getLocalTimeZoneOffset

import json, re
import time
from argparse import ArgumentParser
from collections import OrderedDict
from configparser import RawConfigParser
from unicode_util import parseUnicodeDataFile
from defcon import Font


def rgbaToCSSColor(r=0, g=0, b=0, a=1):
  R,G,B = int(r * 255), int(g * 255), int(b * 255)
  if a == 1:
    return '#%02x%02x%02x' % (R,G,B)
  else:
    return 'rgba(%d,%d,%d,%g)' % (R,G,B,a)


def unicodeName(cp):
  if cp is not None and len(cp.name):
    if cp.name[0] == '<':
      return '[' + cp.categoryName + ']'
    elif len(cp.name):
      return cp.name
  return None


# YYYY/MM/DD HH:mm:ss => YYYY-MM-DDTHH:mm:ssZ  (local time -> UTC)
def localDateTimeToUTCStr(localstr, pattern='%Y/%m/%d %H:%M:%S'):
  t = time.strptime(localstr, pattern)
  ts = time.mktime(t) - getLocalTimeZoneOffset()
  return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(ts))



def main():
  argparser = ArgumentParser(
    description='Generate info on name, unicodes and color mark for all glyphs')

  argparser.add_argument(
    '-ucd', dest='ucdFile', metavar='<file>', type=str,
    help='UnicodeData.txt file from http://www.unicode.org/')

  argparser.add_argument(
    'fontPath', metavar='<ufofile>', type=str)

  args = argparser.parse_args()
  font = Font(args.fontPath)
  ucd = {}
  if args.ucdFile:
    ucd = parseUnicodeDataFile(args.ucdFile)

  glyphs = []  # contains final glyph data printed as JSON

  for name in font.lib['public.glyphOrder']:
    g = font[name]

    # not exported?
    if 'com.schriftgestaltung.Glyphs.Export' in g.lib:
      if not g.lib['com.schriftgestaltung.Glyphs.Export']:
        continue

    # color
    color = None
    if 'public.markColor' in g.lib:
      rgba = [float(c.strip()) for c in g.lib['public.markColor'].strip().split(',')]
      color = rgbaToCSSColor(*rgba)

    isEmpty = 0
    if not g.bounds or g.bounds[3] == 0:
      isEmpty = 1

    # name, isEmpty, unicode, unicodeName, color
    glyph = None
    ucs = g.unicodes
    if len(ucs):
      for uc in ucs:
        ucName = unicodeName(ucd.get(uc))
        # if not ucName and uc >= 0xE000 and uc <= 0xF8FF:
        #   ucName = '[private use %04X]' % uc

        ucstr = '%04X' % uc
        if color:
          glyph = [name, isEmpty, ucstr, ucName, color]
        elif ucName:
          glyph = [name, isEmpty, ucstr, ucName]
        else:
          glyph = [name, isEmpty, ucstr]
    else:
      if color:
        glyph = [name, isEmpty, None, None, color]
      else:
        glyph = [name, isEmpty]

    glyphs.append(glyph)

  print('{"glyphs":[')
  prefix = '  '
  for g in glyphs:
    print(prefix + json.dumps(g))
    if prefix == '  ':
      prefix = ', '
  print(']}')


if __name__ == '__main__':
  main()
