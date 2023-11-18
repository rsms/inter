#!/usr/bin/env python
# encoding: utf8
#
# Sync glyph shapes between SVG and UFO, creating a bridge between UFO and Figma.
#
import os, sys
from os.path import dirname, basename, abspath, relpath, join as pjoin
sys.path.append(abspath(pjoin(dirname(__file__), 'tools')))
from common import BASEDIR

import argparse
import json
import plistlib
import re
from collections import OrderedDict
from math import ceil, floor
from defcon import Font
from svg import SVGPathPen
from ufo2ft.filters.decomposeComponents import DecomposeComponentsFilter
from ufo2ft.filters.removeOverlaps import RemoveOverlapsFilter


ufo = None
ufopath = ''
effectiveAscender = 0
scale = 0.1


def num(s):
  return int(s) if s.find('.') == -1 else float(s)


def glyphToSVGPath(g, yMul):
  pen = SVGPathPen(g.getParent(), yMul)
  g.draw(pen)
  return pen.getCommands()


def svgWidth(g):
  bounds = g.bounds  # (xMin, yMin, xMax, yMax)
  if bounds is None:
    return 0, 0
  xMin = bounds[0]
  xMax = bounds[2]
  width = xMax - xMin
  return width, xMin


def glyphToSVG(g):
  width, xoffs = svgWidth(g)

  svg  = '''
<svg id="svg-%(name)s" xmlns="http://www.w3.org/2000/svg" width="%(width)d" height="%(height)d">
<path d="%(glyphSVGPath)s" transform="translate(%(xoffs)g %(yoffs)g) scale(%(scale)g)"/>
</svg>
  ''' % {
    'name': g.name,
    'width': int(ceil(width * scale)),
    'height': int(ceil((effectiveAscender - ufo.info.descender) * scale)),
    'xoffs': -(xoffs * scale),
    'yoffs': effectiveAscender * scale,
    # 'leftMargin': g.leftMargin * scale,
    # 'rightMargin': g.rightMargin * scale,
    'glyphSVGPath': glyphToSVGPath(g, -1),
    # 'ascender': ufo.info.ascender * scale,
    # 'descender': ufo.info.descender * scale,
    # 'baselineOffset': (ufo.info.unitsPerEm + ufo.info.descender) * scale,
    # 'unitsPerEm': ufo.info.unitsPerEm,
    'scale': scale,

    # 'margin': [g.leftMargin * scale, g.rightMargin * scale],
  }

  # (width, advance, left, right)
  info = (width, g.width, g.leftMargin, g.rightMargin)

  return svg.strip(), info


def stat(path):
  try:
    return os.stat(path)
  except OSError as e:
    return None


def writeFile(file, s):
  with open(file, 'w') as f:
    f.write(s)


def writeFileAndMkDirsIfNeeded(file, s):
  try:
    writeFile(file, s)
  except IOError as e:
    if e.errno == 2:
      os.makedirs(os.path.dirname(file))
      writeFile(file, s)



def findGlifFile(glyphname):
  # glyphname.glif
  # glyphname_.glif
  # glyphname__.glif
  # glyphname___.glif
  for underscoreCount in range(0, 5):
    fn = os.path.join(ufopath, 'glyphs', glyphname + ('_' * underscoreCount) + '.glif')
    st = stat(fn)
    if st is not None:
      return fn, st

  if glyphname.find('.') != -1:
    # glyph_.name.glif
    # glyph__.name.glif
    # glyph___.name.glif
    for underscoreCount in range(0, 5):
      nv = glyphname.split('.')
      nv[0] = nv[0] + ('_' * underscoreCount)
      ns = '.'.join(nv)
      fn = os.path.join(ufopath, 'glyphs', ns + '.glif')
      st = stat(fn)
      if st is not None:
        return fn, st

  if glyphname.find('_') != -1:
    # glyph_name.glif
    # glyph_name_.glif
    # glyph_name__.glif
    # glyph__name.glif
    # glyph__name_.glif
    # glyph__name__.glif
    # glyph___name.glif
    # glyph___name_.glif
    # glyph___name__.glif
    for x in range(0, 4):
      for y in range(0, 5):
        ns = glyphname.replace('_', '__' + ('_' * x))
        fn = os.path.join(ufopath, 'glyphs', ns + ('_' * y) + '.glif')
        st = stat(fn)
        if st is not None:
          return fn, st

  return ('', None)


usedSVGNames = set()

def genGlyph(glyphName):
  g = ufo[glyphName]
  return glyphToSVG(g)


def genGlyphIDs(glyphnames):
  nameToIdMap = {}
  idToNameMap = {}
  nextId = 0
  for name in glyphnames:
    nameToIdMap[name] = nextId
    idToNameMap[nextId] = name
    nextId += 1
  return nameToIdMap, idToNameMap


def genKerningInfo(ufo, glyphnames, nameToIdMap):
  kerning = ufo.kerning

  # load groups
  filename = os.path.join(ufo.path, 'groups.plist')
  groups = None
  with open(filename, 'rb') as f:
    groups = plistlib.load(f)

  pairs = []
  for kt in kerning.keys():
    v = kerning[kt]
    leftname, rightname = kt
    leftnames = []
    rightnames = []

    if leftname.startswith(u'public.kern'):
      leftnames = groups[leftname]
    else:
      leftnames = [leftname]

    if rightname.startswith(u'public.kern'):
      rightnames = groups[rightname]
    else:
      rightnames = [rightname]

    for lname in leftnames:
      for rname in rightnames:
        lnameId = nameToIdMap.get(lname)
        rnameId = nameToIdMap.get(rname)
        if lnameId is not None and rnameId is not None:
          pairs.append([lnameId, rnameId, v])

  # print('pairs: %r' % pairs)
  return pairs


def fmtJsonDict(d):
  keys = sorted(d.keys())
  s = '{'
  delim = '\n'
  delimNth = ',\n'
  for k in keys:
    v = d[k]
    s += delim + json.dumps(str(k)) + ':' + json.dumps(v)
    delim = delimNth
  return s + '}'


def fmtJsonList(d):
  s = '['
  delim = '\n'
  delimNth = ',\n'
  for t in kerning:
    s += delim + json.dumps(t, separators=(',',':'))
    delim = delimNth
  return s + ']'

# ————————————————————————————————————————————————————————————————————————
# main

argparser = argparse.ArgumentParser(description='Generate SVG glyphs from UFO')

argparser.add_argument('-scale', dest='scale', metavar='<scale>', type=str,
  default='',
  help='Scale glyph. Should be a number in the range (0-1]. Defaults to %g' % scale)

argparser.add_argument('ufopath', metavar='<ufopath>', type=str,
                       help='Path to UFO packages')

argparser.add_argument('jsonfile', metavar='<jsonfile>', type=str,
                       help='Output JSON file')
argparser.add_argument('htmlfile', metavar='<htmlfile>', type=str,
                       help='Path to HTML file to patch')

argparser.add_argument('glyphs', metavar='<glyphname>', type=str, nargs='*',
                       help='Only generate specific glyphs.')


args = argparser.parse_args()
srcDir = os.path.join(BASEDIR, 'src')
deleteNames = set(['.notdef', '.null'])

if len(args.scale):
  scale = float(args.scale)

ufopath = args.ufopath.rstrip('/')

ufo = Font(ufopath)
effectiveAscender = max(ufo.info.ascender, ufo.info.unitsPerEm)

glyphnames = args.glyphs if len(args.glyphs) else ufo.keys()
glyphnameSet = set(glyphnames)

glyphnames = [gn for gn in glyphnames if gn not in deleteNames]
glyphnames.sort()

nameToIdMap, idToNameMap = genGlyphIDs(glyphnames)

print('generating kerning pair data')
kerning = genKerningInfo(ufo, glyphnames, nameToIdMap)


print('preprocessing glyphs')
filters = [
  DecomposeComponentsFilter(),
  RemoveOverlapsFilter(backend=RemoveOverlapsFilter.Backend.SKIA_PATHOPS),
]
glyphSet = {g.name: g for g in ufo}
for func in filters:
  func(ufo, glyphSet)

print('generating SVGs and metrics data')

# print('\n'.join(ufo.keys()))
# sys.exit(0)


glyphMetrics = {}

# jsonLines = []
svgLines = []
for glyphname in glyphnames:
  generateFrom = None
  svg, metrics = genGlyph(glyphname)
  # metrics: (width, advance, left, right)
  glyphMetrics[nameToIdMap[glyphname]] = metrics
  svgLines.append(svg.replace('\n', ''))

# print('{\n' + ',\n'.join(jsonLines) + '\n}')

svgtext = '\n'.join(svgLines)
# print(svgtext)

html = u''
with open(args.htmlfile, 'r', encoding="utf-8") as f:
  html = f.read()

startMarker = u'<div id="svgs">'
startPos = html.find(startMarker)

endMarker = u'</div><!--END-SVGS'
endPos = html.find(endMarker, startPos + len(startMarker))

relfilename = os.path.relpath(args.htmlfile, os.getcwd())

if startPos == -1 or endPos == -1:
  msg = 'Could not find `<div id="svgs">...</div><!--END-SVGS` in %s'
  print(msg % relfilename, file=sys.stderr)
  sys.exit(1)

metaJson = '{\n'
metaJson += '"nameids":' + fmtJsonDict(idToNameMap) + ',\n'
metaJson += '"metrics":' + fmtJsonDict(glyphMetrics) + ',\n'
metaJson += '"kerning":' + fmtJsonList(kerning) + '\n'
metaJson += '}'
# metaHtml = '<script>var fontMetaData = ' + metaJson + ';</script>'

html = html[:startPos + len(startMarker)] + '\n' + svgtext + '\n' + html[endPos:]

print('write', relfilename)
with open(args.htmlfile, 'w', encoding="utf-8") as f:
  f.write(html)

# JSON
jsonFilenameRel = os.path.relpath(args.jsonfile, os.getcwd())
print('write', jsonFilenameRel)
with open(args.jsonfile, 'w', encoding="utf-8") as f:
  f.write(metaJson)

metaJson