#!/usr/bin/env python
# encoding: utf8
#
# Updates the "?v=x" in files:
# - docs/inter.css
# - docs/inter-ui.css
# - docs/_includes/preload-font-files.html
#
import os, sys, re
from os.path import dirname, basename, abspath, relpath, join as pjoin
sys.path.append(abspath(pjoin(dirname(__file__), 'tools')))
from common import BASEDIR, getVersion

version = getVersion()


def updateCSSFile(filename):
  regex = re.compile(r'(url\("[^"]+?v=)([^"]+)("\))')
  with open(filename, 'r') as f:
    s = f.read()
  s = regex.sub(lambda m: '%s%s%s' % (m.group(1), version, m.group(3)), s)
  with open(filename, 'w') as f:
    f.write(s)


def updateHTMLFile(filename):
  regex = re.compile(r'(href="[^"]+?v=)([^"]+)(")')
  with open(filename, 'r') as f:
    s = f.read()
  s = regex.sub(lambda m: '%s%s%s' % (m.group(1), version, m.group(3)), s)
  with open(filename, 'w') as f:
    f.write(s)


updateCSSFile(pjoin(BASEDIR, 'misc', 'dist', 'inter.css'))
updateHTMLFile(pjoin(BASEDIR, 'docs', '_includes', 'preload-font-files.html'))

# Note: The website CSS file uses Jekyll variables to add ?v= so don't need this anymore.
# updateCSSFile(pjoin(BASEDIR, 'docs', 'inter.css'))
# updateCSSFile(pjoin(BASEDIR, 'docs', 'inter-ui.css'))
