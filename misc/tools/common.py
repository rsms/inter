#!/usr/bin/env python
from __future__ import print_function
import sys, os
from os.path import dirname, abspath, join as pjoin
import subprocess

# patch PYTHONPATH to include $BASEDIR/build/venv/python/site-packages
BASEDIR = abspath(pjoin(dirname(__file__), os.pardir, os.pardir))
VENVDIR = pjoin(BASEDIR, 'build', 'venv')
sys.path.append(pjoin(VENVDIR, 'lib', 'python', 'site-packages'))


_gitHash = None
def getGitHash():
  global _gitHash
  if _gitHash is None:
    _gitHash = ''
    try:
      _gitHash = subprocess.check_output(
        ['git', '-C', BASEDIR, 'rev-parse', '--short', 'HEAD'],
        shell=False
      ).strip()
    except:
      pass
  return _gitHash


_version = None
def getVersion():
  global _version
  if _version is None:
    with open(pjoin(BASEDIR, 'version.txt'), 'r') as f:
      _version = f.read().strip()
  return _version


# update environment to include $VENVDIR/bin
os.environ['PATH'] = os.path.join(VENVDIR, 'bin') + ':' + os.environ['PATH']
