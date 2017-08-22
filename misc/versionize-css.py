#!/usr/bin/env python
# encoding: utf8
#
# Updates the "?v=x" in docs/interface.css
#
from __future__ import print_function
import os, sys, re
from collections import OrderedDict
from ConfigParser import RawConfigParser


def main():
  rootDir = os.path.dirname(os.path.dirname(__file__))

  config = RawConfigParser(dict_type=OrderedDict)
  config.read(os.path.join(rootDir, 'src', 'fontbuild.cfg'))
  version = config.get('main', 'version')

  regex = re.compile(r'(url\("[^"]+?v=)([^"]+)("\))')

  cssFileName = os.path.join(rootDir, 'docs', 'interface.css')
  
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
