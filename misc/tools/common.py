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

PYVER = sys.version_info[0]


_enc_kwargs = {}
if PYVER >= 3:
  _enc_kwargs = {'encoding': 'utf-8'}


# Returns (output :str, success :bool)
def execproc(*args):
  p = subprocess.run(
    args,
    shell=False,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    **_enc_kwargs
  )
  return (p.stdout.strip(), p.returncode == 0)


def readTextFile(filename):
  with open(filename, 'r', **_enc_kwargs) as f:
    return f.read()


_gitHash = None
_gitHashErrs = []
def getGitHash():  # returns tuple (hash :string, errors :string[])
  global _gitHash
  if _gitHash is None:
    _gitHash = ''
    args = ['git', '-C', BASEDIR, 'rev-parse', '--short', 'HEAD']
    try:
      _gitHash = subprocess.check_output(args, stderr=subprocess.STDOUT, **_enc_kwargs).strip()
    except:
      _gitHashErrs.append(sys.exc_info()[0])
      try:
        # git rev-parse --short HEAD > githash.txt
        _gitHash = readTextFile(pjoin(BASEDIR, 'githash.txt')).strip()
      except:
        _gitHashErrs.append(sys.exc_info()[0])
  return (_gitHash, _gitHashErrs)


_version = None
def getVersion():
  global _version
  if _version is None:
    _version = readTextFile(pjoin(BASEDIR, 'version.txt')).strip()
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
