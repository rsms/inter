#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys
from argparse import ArgumentParser
from robofab.objects.objectsRF import OpenFont


dryRun = False

def renameProps(font, renames):
  for g in font:
    for currname, newname in renames:
      if currname in g.lib:
        if newname in g.lib:
          raise Exception('property %r already exist in glyph %r' % (newname, g))
        g.lib[newname] = g.lib[currname]
        del g.lib[currname]


def main():
  argparser = ArgumentParser(
    description='Operate on UFO glyf "lib" properties')

  argparser.add_argument(
    '-dry', dest='dryRun', action='store_const', const=True, default=False,
    help='Do not modify anything, but instead just print what would happen.')

  argparser.add_argument(
    '-m', dest='renameProps', metavar='<currentName>=<newName>[,...]', type=str,
    help='Rename properties')

  argparser.add_argument(
    'fontPaths', metavar='<ufofile>', type=str, nargs='+', help='UFO fonts to update')

  args = argparser.parse_args()
  dryRun = args.dryRun

  renames = []
  if args.renameProps:
    renames = [tuple(s.split('=')) for s in args.renameProps.split(',')]
    # TODO: verify data structure
    print('renaming properties:')
    for rename in renames:
      print('  %r => %r' % rename)

  # Strip trailing slashes from font paths and iterate
  for fontPath in [s.rstrip('/ ') for s in args.fontPaths]:
    font = OpenFont(fontPath)

    if len(renames):
      print('Renaming properties in %s' % fontPath)
      renameProps(font, renames)

    if dryRun:
      print('Saving changes to %s (dry run)' % fontPath)
    if not dryRun:
      print('Saving changes to %s' % fontPath)
      font.save()


if __name__ == '__main__':
  main()
