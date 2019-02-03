#!/usr/bin/env python
from __future__ import print_function
import os, sys, subprocess
from argparse import ArgumentParser
from xml.dom.minidom import parse as xmlParseFile
from collections import OrderedDict


def main():
  opts = ArgumentParser(description='Shows glyph-related changes.')

  opts.add_argument(
    'sinceCommit', metavar='<since-commit>', type=str,
    help='Start commit.')

  opts.add_argument(
    'untilCommit', metavar='<until-commit>', type=str, nargs='?',
    default='HEAD', help='End commit. Defaults to HEAD.')

  opts.add_argument(
    '-markdown', dest='markdown', action='store_const',
    const=True, default=False,
    help='Output text suitable for Markdown (rather than plain text.)')

  a = opts.parse_args()

  rootdir = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir
  ))

  try:
    out = subprocess.check_output(
      [
        'git',
        '-C', rootdir,
        'diff',
        '--name-status',
        a.sinceCommit + '..' + a.untilCommit,
        '--', 'src'
      ],
      shell=False
    ).strip()
  except Exception as e:
    print('Did you forget to `git fetch --tags` perhaps?', file=sys.stderr)
    sys.exit(1)

  ufoPrefix = 'src/Inter-'
  changes = OrderedDict()
  deleted = []

  for line in out.split('\n'):
    changeType, name = line.split('\t')
    if name.startswith(ufoPrefix) and name.endswith('.glif'):
      weight = name[len(ufoPrefix):name.find('.ufo/')]
      filename = os.path.join(rootdir, name)
      try:
        doc = xmlParseFile(filename)
      except:
        deleted.append('%s/%s' % (weight, os.path.basename(name)))
        continue

      g = doc.documentElement
      gname = g.attributes['name'].value
      unicodes = set([
        'U+' + u.attributes['hex'].value
          for u in g.getElementsByTagName('unicode')
      ])

      c = changes.get(gname)
      if c is None:
        c = {
          'unicodes': unicodes,
          'weights': [(weight, changeType)]
        }
        changes[gname] = c
      else:
        c['unicodes'] = c['unicodes'].union(unicodes)
        c['weights'].append((weight, changeType))

  longestName = 0
  names = sorted(changes.keys())

  if not a.markdown:
    # find longest name
    for name in names:
      z = len(name)
      if z > longestName:
        longestName = z

  for name in names:
    c = changes[name]
    weights = [ w[0] for w in c['weights'] ]
    unicodes = c['unicodes']

    if a.markdown:
      unicodess = ''
      if len(unicodes) != 0:
        unicodess = ' %s' % ', '.join(['`%s`' % s for s in unicodes])
      weightss = ' & '.join(weights)
      print('- %s%s _%s_' % (name, unicodess, weightss))
    else:
      unicodess = ''
      if len(unicodes) != 0:
        unicodess = ' (%s)' % ', '.join(unicodes)
      weightss = ' & '.join(weights)
      print('%s%s %s' % (name.ljust(longestName), unicodess, weightss))

  if len(deleted):
    print('\nDeleted files')
    for filename in deleted:
      print('- %s' % filename)


main()