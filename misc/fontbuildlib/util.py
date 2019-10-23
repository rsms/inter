import sys
import os
import errno
from fontTools.ttLib import TTFont
from os.path import dirname, abspath, join as pjoin

PYVER = sys.version_info[0]
BASEDIR = abspath(pjoin(dirname(__file__), os.pardir, os.pardir))

_enc_kwargs = {}
if PYVER >= 3:
  _enc_kwargs = {'encoding': 'utf-8'}


def readTextFile(filename):
  with open(filename, 'r', **_enc_kwargs) as f:
    return f.read()


def mkdirs(path):
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise  # raises the error again


def loadTTFont(file):
  return TTFont(file, recalcBBoxes=False, recalcTimestamp=False)
