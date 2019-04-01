#!/usr/bin/env python
# encoding: utf8
#
# Generates JSON-encoded information about fonts
#
import os, sys
from os.path import dirname, basename, abspath, relpath, join as pjoin
sys.path.append(abspath(pjoin(dirname(__file__), 'tools')))
import common  # for the side effeects

import argparse
import json
import re
from base64 import b64encode

from fontTools import ttLib
from fontTools.misc import sstruct
from fontTools.ttLib.tables._h_e_a_d import headFormat
from fontTools.ttLib.tables._h_h_e_a import hheaFormat
from fontTools.ttLib.tables._m_a_x_p import maxpFormat_0_5, maxpFormat_1_0_add
from fontTools.ttLib.tables._p_o_s_t import postFormat
from fontTools.ttLib.tables.O_S_2f_2 import OS2_format_1, OS2_format_2, OS2_format_5, panoseFormat
from fontTools.ttLib.tables._m_e_t_a import table__m_e_t_a
# from robofab.world import world, RFont, RGlyph, OpenFont, NewFont
# from robofab.objects.objectsRF import RFont, RGlyph, OpenFont, NewFont, RContour

_NAME_IDS = {}


panoseWeights = [
  'Any', # 0
  'No Fit', # 1
  'Very Light', # 2
  'Light', # 3
  'Thin', # 4
  'Book', # 5
  'Medium', # 6
  'Demi', # 7
  'Bold', # 8
  'Heavy', # 9
  'Black', # 10
  'Extra Black', # 11
]

panoseProportion = [
  'Any', # 0
  'No fit', # 1
  'Old Style/Regular', # 2
  'Modern', # 3
  'Even Width', # 4
  'Extended', # 5
  'Condensed', # 6
  'Very Extended', # 7
  'Very Condensed', # 8
  'Monospaced', # 9
]

os2WidthClass = [
  None,
  'Ultra-condensed', # 1
  'Extra-condensed', # 2
  'Condensed', # 3
  'Semi-condensed', # 4
  'Medium (normal)', # 5
  'Semi-expanded', # 6
  'Expanded', # 7
  'Extra-expanded', # 8
  'Ultra-expanded', # 9
]

os2WeightClass = {
  100: 'Thin',
  200: 'Extra-light (Ultra-light)',
  300: 'Light',
  400: 'Normal (Regular)',
  500: 'Medium',
  600: 'Semi-bold (Demi-bold)',
  700: 'Bold',
  800: 'Extra-bold (Ultra-bold)',
  900: 'Black (Heavy)',
}


def num(s):
  return int(s) if s.find('.') == -1 else float(s)


def tableNamesToDict(table, names):
  t = {}
  for name in names:
    if name.find('reserved') == 0:
      continue
    t[name] = getattr(table, name)
  return t


def sstructTableToDict(table, format):
  _, names, _ = sstruct.getformat(format)
  return tableNamesToDict(table, names)


OUTPUT_TYPE_COMPLETE = 'complete'
OUTPUT_TYPE_GLYPHLIST = 'glyphlist'


GLYPHS_TYPE_UNKNOWN = '?'
GLYPHS_TYPE_TT = 'tt'
GLYPHS_TYPE_CFF = 'cff'

def getGlyphsType(tt):
  if 'CFF ' in tt:
    return GLYPHS_TYPE_CFF
  elif 'glyf' in tt:
    return GLYPHS_TYPE_TT
  return GLYPHS_TYPE_UNKNOWN


class GlyphInfo:
  def __init__(self, g, name, unicodes, type, glyphTable):
    self._type = type # GLYPHS_TYPE_*
    self._glyphTable = glyphTable

    self.name     = name
    self.width    = g.width
    self.lsb      = g.lsb
    self.unicodes = unicodes

    if g.height is not None:
      self.tsb    = g.tsb
      self.height = g.height
    else:
      self.tsb    = 0
      self.height = 0

    self.numContours = 0
    self.contoursBBox = (0,0,0,0) # xMin, yMin, xMax, yMax
    self.hasHints = False

    if self._type is GLYPHS_TYPE_CFF:
      self._addCFFInfo()
    elif self._type is GLYPHS_TYPE_TT:
      self._addTTInfo()

  def _addTTInfo(self):
    g = self._glyphTable[self.name]
    self.numContours = g.numberOfContours
    if g.numberOfContours:
      self.contoursBBox = (g.xMin,g.xMin,g.xMax,g.yMax)
    self.hasHints = hasattr(g, "program")

  def _addCFFInfo(self):
    # TODO: parse CFF dict tree
    pass

  @classmethod
  def structKeys(cls, type):
    v = [
      'name',
      'unicodes',
      'width',
      'lsb',
      'height',
      'tsb',
      'hasHints',
    ]
    if type is GLYPHS_TYPE_TT:
      v += (
        'numContours',
        'contoursBBox',
      )
    return v

  def structValues(self):
    v = [
      self.name,
      self.unicodes,
      self.width,
      self.lsb,
      self.height,
      self.tsb,
      self.hasHints,
    ]
    if self._type is GLYPHS_TYPE_TT:
      v += (
        self.numContours,
        self.contoursBBox,
      )
    return v


# exported convenience function
def GenGlyphList(font, withGlyphs=None):
  if isinstance(font, str):
    font = ttLib.TTFont(font)
  return genGlyphsInfo(font, OUTPUT_TYPE_GLYPHLIST)


def genGlyphsInfo(tt, outputType, glyphsType=GLYPHS_TYPE_UNKNOWN, glyphsTable=None, withGlyphs=None):
  unicodeMap = {}

  glyphnameFilter = None
  if isinstance(withGlyphs, str):
    glyphnameFilter = withGlyphs.split(',')

  if 'cmap' in tt:
    # https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html
    bestCodeSubTable = None
    bestCodeSubTableFormat = 0
    for st in tt['cmap'].tables:
      if st.platformID == 0: # 0=unicode, 1=mac, 2=(reserved), 3=microsoft
        if st.format > bestCodeSubTableFormat:
          bestCodeSubTable = st
          bestCodeSubTableFormat = st.format
    for cp, glyphname in bestCodeSubTable.cmap.items():
      if glyphname in unicodeMap:
        unicodeMap[glyphname].append(cp)
      else:
        unicodeMap[glyphname] = [cp]

  glyphValues = []

  glyphnames = tt.getGlyphOrder() if glyphnameFilter is None else glyphnameFilter

  if outputType is OUTPUT_TYPE_GLYPHLIST:
    glyphValues = []
    for glyphname in glyphnames:
      v = [glyphname]
      if glyphname in unicodeMap:
        v += unicodeMap[glyphname]
      glyphValues.append(v)
    return glyphValues
  
  glyphset = tt.getGlyphSet(preferCFF=glyphsType is GLYPHS_TYPE_CFF)
  
  for glyphname in glyphnames:
    unicodes = unicodeMap[glyphname] if glyphname in unicodeMap else []
    try:
      g = glyphset[glyphname]
    except KeyError:
      raise Exception('no such glyph "'+glyphname+'"')
    gi = GlyphInfo(g, glyphname, unicodes, glyphsType, glyphsTable)
    glyphValues.append(gi.structValues())

  return {
    'keys': GlyphInfo.structKeys(glyphsType),
    'values': glyphValues,
  }


def copyDictEntry(srcD, srcName, dstD, dstName):
  try:
    dstD[dstName] = srcD[srcName]
  except:
    pass


def addCFFFontInfo(tt, info, cffTable):
  d = cffTable.rawDict

  nameDict = None
  if 'name' not in info:
    nameDict = {}
    info['name'] = nameDict
  else:
    nameDict = info['name']

  copyDictEntry(d, 'Weight', nameDict, 'weight')
  copyDictEntry(d, 'version', nameDict, 'version')


def genFontInfo(fontpath, outputType, withGlyphs=True):
  tt = ttLib.TTFont(fontpath) # lazy=True
  info = {
    'id': fontpath,
  }

  # for tableName in tt.keys():
  #   print('table', tableName)

  nameDict = {}
  if 'name' in tt:
    nameDict = {}
    for rec in tt['name'].names:
      k = _NAME_IDS[rec.nameID] if rec.nameID in _NAME_IDS else ('#%d' % rec.nameID)
      nameDict[k] = rec.toUnicode()
    if 'fontId' in nameDict:
      info['id'] = nameDict['fontId']

  if 'postscriptName' in nameDict:
    info['name'] = nameDict['postscriptName']
  elif 'familyName' in nameDict:
    info['name'] = nameDict['familyName'].replace(' ', '')
    if 'subfamilyName' in nameDict:
      info['name'] += '-' + nameDict['subfamilyName'].replace(' ', '')

  if 'version' in nameDict:
    version = nameDict['version']
    v = re.split(r'[\s;]+', version)
    if v and len(v) > 0:
      version = v[0]
      if version.lower() == 'version':
        version = v[1]
      version = '.'.join([str(int(v)) for v in version.split('.')])
    info['version'] = version

  if outputType is not OUTPUT_TYPE_GLYPHLIST:
    if len(nameDict):
      info['names'] = nameDict

    if 'head' in tt:
      head = sstructTableToDict(tt['head'], headFormat)
      if 'macStyle' in head:
        s = []
        v = head['macStyle']
        if isinstance(v, int):
          if v & 0b00000001: s.append('Bold')
          if v & 0b00000010: s.append('Italic')
          if v & 0b00000100: s.append('Underline')
          if v & 0b00001000: s.append('Outline')
          if v & 0b00010000: s.append('Shadow')
          if v & 0b00100000: s.append('Condensed')
          if v & 0b01000000: s.append('Extended')
          head['macStyle_raw'] = head['macStyle']
          head['macStyle'] = s
      info['head'] = head

    if 'hhea' in tt:
      info['hhea'] = sstructTableToDict(tt['hhea'], hheaFormat)

    if 'post' in tt:
      info['post'] = sstructTableToDict(tt['post'], postFormat)

    if 'OS/2' in tt:
      t = tt['OS/2']
      os2 = None
      if t.version == 1:
        os2 = sstructTableToDict(t, OS2_format_1)
      elif t.version in (2, 3, 4):
        os2 = sstructTableToDict(t, OS2_format_2)
      elif t.version == 5:
        os2 = sstructTableToDict(t, OS2_format_5)
        os2['usLowerOpticalPointSize'] /= 20
        os2['usUpperOpticalPointSize'] /= 20

      if 'panose' in os2:
        panose = {}
        for k,v in sstructTableToDict(os2['panose'], panoseFormat).items():
          if k[0:1] == 'b' and k[1].isupper():
            k = k[1].lower() + k[2:]
            # bFooBar => fooBar
          if k == 'weight' and isinstance(v, int) and v < len(panoseWeights):
            panose['weightName'] = panoseWeights[v]
          elif k == 'proportion' and isinstance(v, int) and v < len(panoseProportion):
            panose['proportionName'] = panoseProportion[v]
          panose[k] = v
        os2['panose'] = panose

      if 'usWidthClass' in os2:
        v = os2['usWidthClass']
        if isinstance(v, int) and v > 0 and v < len(os2WidthClass):
          os2['usWidthClassName'] = os2WidthClass[v]

      if 'usWeightClass' in os2:
        v = os2['usWeightClass']
        name = os2WeightClass.get(os2['usWeightClass'])
        if name:
          os2['usWeightClassName'] = name

      info['os/2'] = os2

    if 'meta' in tt:
      meta = {}
      for k,v in tt['meta'].data.items():
        try:
          v.decode('utf8')
          meta[k] = v
        except:
          meta[k] = 'data:;base64,' + b64encode(v)
      info['meta'] = meta

    # if 'maxp' in tt:
    #   table = tt['maxp']
    #   _, names, _ = sstruct.getformat(maxpFormat_0_5)
    #   if table.tableVersion != 0x00005000:
    #     _, names_1_0, _ = sstruct.getformat(maxpFormat_1_0_add)
    #     names += names_1_0
    #   info['maxp'] = tableNamesToDict(table, names)

  glyphsType = getGlyphsType(tt)
  glyphsTable = None
  if glyphsType is GLYPHS_TYPE_CFF:
    cff = tt["CFF "].cff
    cffDictIndex = cff.topDictIndex
    if len(cffDictIndex) > 1:
      sys.stderr.write(
        'warning: multi-font CFF table is unsupported. Only reporting first table.\n'
      )
    cffTable = cffDictIndex[0]
    if outputType is not OUTPUT_TYPE_GLYPHLIST:
      addCFFFontInfo(tt, info, cffTable)
  elif glyphsType is GLYPHS_TYPE_TT:
    glyphsTable = tt["glyf"]
  # print('glyphs type:', glyphsType, 'flavor:', tt.flavor, 'sfntVersion:', tt.sfntVersion)

  if (withGlyphs is not False or outputType is OUTPUT_TYPE_GLYPHLIST) and withGlyphs is not '':
    info['glyphs'] = genGlyphsInfo(tt, outputType, glyphsType, glyphsTable, withGlyphs)

  # sys.exit(1)

  return info


# ————————————————————————————————————————————————————————————————————————
# main

def main():
  argparser = argparse.ArgumentParser(description='Generate JSON describing fonts')

  argparser.add_argument('-out', dest='outfile', metavar='<file>', type=str,
                         help='Write JSON to <file>. Writes to stdout if not specified')

  argparser.add_argument('-pretty', dest='prettyJson', action='store_const',
                         const=True, default=False,
                         help='Generate pretty JSON with linebreaks and indentation')

  argparser.add_argument('-with-all-glyphs', dest='withGlyphs', action='store_const',
                         const=True, default=False,
                         help='Include glyph information on all glyphs.')

  argparser.add_argument('-with-glyphs', dest='withGlyphs', metavar='glyphname[,glyphname ...]',
                         type=str,
                         help='Include glyph information on specific glyphs')

  argparser.add_argument('-as-glyphlist', dest='asGlyphList',
                         action='store_const', const=True, default=False,
                         help='Only generate a list of glyphs and their unicode mappings.')

  argparser.add_argument('fontpaths', metavar='<path>', type=str, nargs='+',
                         help='TrueType or OpenType font files')

  args = argparser.parse_args()

  fonts = []
  outputType = OUTPUT_TYPE_COMPLETE
  if args.asGlyphList:
    outputType = OUTPUT_TYPE_GLYPHLIST

  n = 0
  for fontpath in args.fontpaths:
    if n > 0:
      # workaround for a bug in fontTools.misc.sstruct where it keeps a global
      # internal cache that mixes up values for different fonts.
      reload(sstruct)
    font = genFontInfo(fontpath, outputType=outputType, withGlyphs=args.withGlyphs)
    fonts.append(font)
    n += 1

  ostream = sys.stdout
  if args.outfile is not None:
    ostream = open(args.outfile, 'w')


  if args.prettyJson:
    json.dump(fonts, ostream, sort_keys=True, indent=2, separators=(',', ': '))
    sys.stdout.write('\n')
  else:
    json.dump(fonts, ostream, separators=(',', ':'))


  if ostream is not sys.stdout:
    ostream.close()



# "name" table name identifiers
_NAME_IDS = {
  # TrueType & OpenType
   0: 'copyright',
   1: 'familyName',
   2: 'subfamilyName',
   3: 'fontId',
   4: 'fullName',
   5: 'version', # e.g. 'Version <number>.<number>'
   6: 'postscriptName',
   7: 'trademark',
   8: 'manufacturerName',
   9: 'designer',
  10: 'description',
  11: 'vendorURL',
  12: 'designerURL',
  13: 'licenseDescription',
  14: 'licenseURL',
  15: 'RESERVED',
  16: 'typoFamilyName',
  17: 'typoSubfamilyName',
  18: 'macCompatibleFullName', # Mac only (FOND)
  19: 'sampleText',

  # OpenType
  20: 'postScriptCIDName',
  21: 'wwsFamilyName',
  22: 'wwsSubfamilyName',
  23: 'lightBackgoundPalette',
  24: 'darkBackgoundPalette',
  25: 'variationsPostScriptNamePrefix',

  # 26-255: Reserved for future expansion
  # 256-32767: Font-specific names (layout features and settings, variations, track names, etc.)
}

if __name__ == '__main__':
  main()
