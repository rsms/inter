#!/usr/bin/env python
from __future__ import print_function
import sys, os
from os.path import dirname, abspath, join as pjoin
import subprocess
import time

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


_local_tz_offs = None
def getLocalTimeZoneOffset():  # in seconds from UTC
  # seriously ugly hack to get timezone offset in Python
  global _local_tz_offs
  if _local_tz_offs is None:
    tzname = time.strftime("%Z", time.localtime())
    s = time.strftime('%z', time.strptime(tzname, '%Z'))
    i = 0
    neg = False
    if s[0] == '-':
      neg = True
      i = 1
    elif s[0] == '+':
      i = 1
    h = int(s[i:i+2])
    m = int(s[i+2:])
    _local_tz_offs = ((h * 60) + m) * 60
    if neg:
      _local_tz_offs = -_local_tz_offs
  return _local_tz_offs


# update environment to include $VENVDIR/bin
os.environ['PATH'] = os.path.join(VENVDIR, 'bin') + ':' + os.environ['PATH']
