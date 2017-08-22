#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys
from collections import OrderedDict
from ConfigParser import RawConfigParser


def main():
  srcDir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
  config = RawConfigParser(dict_type=OrderedDict)
  config.read(os.path.join(srcDir, 'fontbuild.cfg'))
  sys.stdout.write(config.get('main', 'version'))

if __name__ == '__main__':
  main()
