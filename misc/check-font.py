#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys
from argparse import ArgumentParser
from multiprocessing import Pool
import extractor, defcon


def check_font(filename):
  print('check %s' % filename)
  ufo = defcon.Font()
  extractor.extractUFO(filename, ufo, doGlyphs=True, doInfo=True, doKerning=True)


def main(argv=None):
  opts = ArgumentParser(description='Check')

  opts.add_argument(
    'fontFiles', metavar='<file>', type=str, nargs='+',
    help='Font files (otf, ttf, woff, woff2, pfa, pfb, ttx)')

  args = opts.parse_args(argv)

  if len(args.fontFiles) == 1:
    check_font(args.fontFiles[0])
  else:
    p = Pool(8)
    p.map(check_font, args.fontFiles)
    p.terminate()


if __name__ == '__main__':
  main()
