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
import fontTools.ttLib.tables._t_r_a_k as t_r_a_k
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
  version = None
  if 'name' in tt:
    nameDict = {}
    for rec in tt['name'].names:
      k = '#%d' % rec.nameID
      value = rec.toUnicode()
      if rec.nameID in _NAME_IDS:
        if _NAME_IDS[rec.nameID] == 'version':
          version = value
        k += ' ' + _NAME_IDS[rec.nameID]
      nameDict[k] = value
    if 'fontId' in nameDict:
      info['id'] = nameDict['fontId']

  if 'postscriptName' in nameDict:
    info['name'] = nameDict['postscriptName']
  elif 'familyName' in nameDict:
    info['name'] = nameDict['familyName'].replace(' ', '')
    if 'subfamilyName' in nameDict:
      info['name'] += '-' + nameDict['subfamilyName'].replace(' ', '')

  if version:
    v = re.split(r'[\s;]+', version)
    if v and len(v) > 0:
      version = v[0]
      if version.lower() == 'version':
        version = v[1]
      try:
        version = '.'.join([str(int(v)) for v in version.split('.')])
      except:
        version = nameDict['version']
    info['version'] = version

  if outputType is not OUTPUT_TYPE_GLYPHLIST:
    if len(nameDict):
      info['names'] = nameDict

    if 'head' in tt:
      NOSET = '%d: SHOULD NOT BE SET'
      head = sstructTableToDict(tt['head'], headFormat)
      if 'macStyle' in head:
        s = []
        v = head['macStyle']
        if isinstance(v, int): # uint16
          if v & 0b0000000000000001: s.append('0: Bold')
          if v & 0b0000000000000010: s.append('1: Italic')
          if v & 0b0000000000000100: s.append('2: Underline')
          if v & 0b0000000000001000: s.append('3: Outline')
          if v & 0b0000000000010000: s.append('4: Shadow')
          if v & 0b0000000000100000: s.append('5: Condensed')
          if v & 0b0000000001000000: s.append('6: Extended')
          # Bits 7–15: Reserved (set to 0)
          if v & 0b0000000010000000: s.append(NOSET % 7)
          if v & 0b0000000100000000: s.append(NOSET % 8)
          if v & 0b0000001000000000: s.append(NOSET % 9)
          if v & 0b0000010000000000: s.append(NOSET % 10)
          if v & 0b0000100000000000: s.append(NOSET % 11)
          if v & 0b0001000000000000: s.append(NOSET % 12)
          if v & 0b0010000000000000: s.append(NOSET % 13)
          if v & 0b0100000000000000: s.append(NOSET % 14)
          if v & 0b1000000000000000: s.append(NOSET % 15)
          head['macStyle_raw'] = head['macStyle']
          head['macStyle'] = s

      v = head['flags'] # uint16
      if isinstance(v, int):
        # https://docs.microsoft.com/en-us/typography/opentype/spec/head
        s = []
        if v & 0b0000000000000001: s.append('0: Baseline at y=0')
        if v & 0b0000000000000010: s.append('1: Left sidebearing point at x=0')
        if v & 0b0000000000000100: s.append('2: Instructions may depend on point size')
        if v & 0b0000000000001000: s.append('3: Force ppem to integer values')
        if v & 0b0000000000010000: s.append('4: Instructions may alter advance width')
        # Bit 5: This bit is not used in OpenType, and should not be set in order to ensure
        # compatible behavior on all platforms. If set, it may result in different behavior
        # for vertical layout in some platforms. (See Apple’s specification for details
        # regarding behavior in Apple platforms.)
        if v & 0b0000000000100000: s.append(NOSET % 5)
        # Bits 6–10 are not used in Opentype and should always be cleared
        if v & 0b0000000001000000: s.append(NOSET % 6)
        if v & 0b0000000010000000: s.append(NOSET % 7)
        if v & 0b0000000100000000: s.append(NOSET % 8)
        if v & 0b0000001000000000: s.append(NOSET % 9)
        if v & 0b0000010000000000: s.append(NOSET % 10)
        if v & 0b0000100000000000: s.append('11: Losslessly optimized')
        if v & 0b0001000000000000: s.append('12: Converted')
        if v & 0b0010000000000000: s.append('13: Optimized for ClearType')
        if v & 0b0100000000000000: s.append('14: Last Resort font')

        # Bit 15 is reserved
        if v & 0b1000000000000000: s.append(NOSET % 15)

        head['flags_raw'] = head['flags']
        head['flags'] = s
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

      fsType = os2.get('fsType')
      if fsType is not None:
        obj = {"raw":fsType}
        # Usage permissions: 0x000F
        perm = fsType & 0x000F
        perms = ""
        if perm == 0:
          perms = "Freely installable & embeddable"
        elif perm == 2:
          perms = "Restricted License embedding"
        elif perm == 4:
          perms = "Preview & Print embedding"
        elif perm == 8:
          perms = "Editable embedding"
        else:
          perms = "<INVALID VALUE %r>" % perm
        obj['perm'] = '0x%04X: %s' % (perm, perms)
        obj['no_subset'] = "no" if fsType & 0x0100 == 0 else "yes"
        obj['bitmap_embed_only'] = "no" if fsType & 0x0200 == 0 else "yes"
        os2['fsType'] = obj

      fsSelection = os2.get('fsSelection')
      if fsSelection is not None:
        # https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fsselection
        # Bit  macStyle bit  Symbolic name
        #   0             1  ITALIC
        #   1                UNDERSCORE
        #   2                NEGATIVE
        #   3                OUTLINED
        #   4                STRIKEOUT
        #   5             0  BOLD
        #   6                REGULAR
        #   7                USE_TYPO_METRICS
        #   8                WWS
        #   9                OBLIQUE
        # 10-15              <reserved>
        s = []
        if fsSelection & 0b0000000000000001: s.append('0: ITALIC')
        if fsSelection & 0b0000000000000010: s.append('1: UNDERSCORE')
        if fsSelection & 0b0000000000000100: s.append('2: NEGATIVE')
        if fsSelection & 0b0000000000001000: s.append('3: OUTLINED')
        if fsSelection & 0b0000000000010000: s.append('4: STRIKEOUT')
        if fsSelection & 0b0000000000100000: s.append('5: BOLD')
        if fsSelection & 0b0000000001000000: s.append('6: REGULAR')
        if fsSelection & 0b0000000010000000: s.append('7: USE_TYPO_METRICS')
        if fsSelection & 0b0000000100000000: s.append('8: WWS')
        if fsSelection & 0b0000001000000000: s.append('9: OBLIQUE')
        os2['fsSelection_raw'] = bin(fsSelection)
        os2['fsSelection'] = s


      info['OS/2'] = os2

    if 'meta' in tt:
      meta = {}
      for k,v in tt['meta'].data.items():
        try:
          v.decode('utf8')
          meta[k] = v
        except:
          meta[k] = 'data:;base64,' + b64encode(v).decode('ascii')
      info['meta'] = meta

    if 'trak' in tt:
      # Apple-specific table, linking size to tracking values.
      # https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6trak.html
      trak = {}
      table = tt['trak']
      for direction in ("horiz", "vert"):
        dataName = direction + "Data"
        trackData = getattr(table, dataName, t_r_a_k.TrackData())
        td = {}
        for k, tableEntry in trackData.__dict__['_map'].items():
          td[k] = { "nameIndex": tableEntry.nameIndex }
          for k2 in tableEntry.keys():
            td[k][str(k2)] = tableEntry[k2]
        trak[dataName] = td
      info['trak'] = trak

    # rest of tables
    for tname in tt.keys():
      if tname not in info:
        info[tname] = "[present but not decoded]"

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

  if (withGlyphs != False or outputType is OUTPUT_TYPE_GLYPHLIST) and withGlyphs != '':
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
