#!/usr/bin/env python
# encoding: utf8
#
# Updates the "?v=x" in docs/inter-ui.css
#
from __future__ import print_function

import os, sys
from os.path import dirname, basename, abspath, relpath, join as pjoin
sys.path.append(abspath(pjoin(dirname(__file__), 'tools')))
from common import BASEDIR, getVersion

import re


def main():
  version = getVersion()
  regex = re.compile(r'(url\("[^"]+?v=)([^"]+)("\))')
  cssFileName = pjoin(BASEDIR, 'docs', 'inter-ui.css')

  s = ''
  with open(cssFileName, 'r') as f:
    s = f.read()

  s = regex.sub(
    lambda m: '%s%s%s' % (m.group(1), version, m.group(3)),
    s
  )

  with open(cssFileName, 'w') as f:
    f.write(s)

if __name__ == '__main__':
  main()
