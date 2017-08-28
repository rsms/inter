#!/usr/bin/env python
# encoding: utf8
#
# Sync glyph shapes between SVG and UFO, creating a bridge between UFO and Figma.
#
from __future__ import print_function
import os, sys, argparse, re, json, plistlib
from math import ceil, floor
from robofab.objects.objectsRF import OpenFont
from collections import OrderedDict
from fontbuild.generateGlyph import generateGlyph

font = None  # RFont
ufopath = ''
effectiveAscender = 0
scale = 0.1
agl = None


def num(s):
  return int(s) if s.find('.') == -1 else float(s)


def parseGlyphComposition(composite):
  c = composite.split("=")
  d = c[1].split("/")
  glyphName = d[0]
  if len(d) == 1:
    offset = [0, 0]
  else:
    offset = [int(i) for i in d[1].split(",")]
  accentString = c[0]
  accents = accentString.split("+")
  baseName = accents.pop(0)
  accentNames = [i.split(":") for i in accents]
  return (glyphName, baseName, accentNames, offset)


def loadGlyphCompositions(filename):  # { glyphName => (baseName, accentNames, offset, rawline) }
  compositions = OrderedDict()
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      if len(line) > 0 and line[0] != '#':
        glyphName, baseName, accentNames, offset = parseGlyphComposition(line)
        compositions[glyphName] = (baseName, accentNames, offset, line)
  return compositions


def loadAGL(filename):  # -> { 2126: 'Omega', ... }
  m = {}
  with open(filename, 'r') as f:
    for line in f:
      # Omega;2126
      # dalethatafpatah;05D3 05B2   # higher-level combinations; ignored
      line = line.strip()
      if len(line) > 0 and line[0] != '#':
        name, uc = tuple([c.strip() for c in line.split(';')])
        if uc.find(' ') == -1:
          # it's a 1:1 mapping
          m[int(uc, 16)] = name
  return m

def decomposeGlyph(font, glyph):
  """Moves the components of a glyph to its outline."""
  if len(glyph.components):
    deepCopyContours(font, glyph, glyph, (0, 0), (1, 1))
    glyph.clearComponents()


def deepCopyContours(font, parent, component, offset, scale):
  """Copy contours to parent from component, including nested components."""

  for nested in component.components:
    deepCopyContours(
      font, parent, font[nested.baseGlyph],
      (offset[0] + nested.offset[0], offset[1] + nested.offset[1]),
      (scale[0] * nested.scale[0], scale[1] * nested.scale[1]))

  if component == parent:
    return
  for contour in component:
    contour = contour.copy()
    contour.scale(scale)
    contour.move(offset)
    parent.appendContour(contour)



def glyphToSVGPath(g, yMul):
  commands = {'move':'M','line':'L','curve':'Y','offcurve':'X','offCurve':'X'}
  svg = ''
  contours = []

  if len(g.components):
    decomposeGlyph(g.getParent(), g)  # mutates g

  if len(g):
    for c in range(len(g)):
      contours.append(g[c])

  for i in range(len(contours)):
    c = contours[i]
    contour = end = ''
    curve = False
    points = c.points
    if points[0].type == 'offCurve':
      points.append(points.pop(0))
    if points[0].type == 'offCurve':
      points.append(points.pop(0))
    for x in range(len(points)):
      p = points[x]
      command = commands[str(p.type)]
      if command == 'X':
        if curve == True:
          command = ''
        else:
          command = 'C'
          curve = True
      if command == 'Y':
        command = ''
        curve = False
      if x == 0:
        command = 'M'
        if p.type == 'curve':
          end = ' %g %g' % (p.x * scale, (p.y * yMul) * scale)
      contour += ' %s%g %g' % (command, p.x * scale, (p.y * yMul) * scale)
    svg += ' ' + contour + end + 'z'

  if font.has_key('__svgsync'):
    font.removeGlyph('__svgsync')
  return svg.strip()


def svgWidth(g):
  box = g.box
  xoffs = box[0]
  width = box[2] - box[0]
  return width, xoffs


def glyphToSVG(g):
  width, xoffs = svgWidth(g)

  svg  = '''
<svg id="svg-%(name)s" xmlns="http://www.w3.org/2000/svg" width="%(width)d" height="%(height)d">
<path d="%(glyphSVGPath)s" transform="translate(%(xoffs)g %(yoffs)g)"/>
</svg>
  ''' % {
    'name': g.name,
    'width': int(ceil(width * scale)),
    'height': int(ceil((effectiveAscender - font.info.descender) * scale)),
    'xoffs': -(xoffs * scale),
    'yoffs': effectiveAscender * scale,
    # 'leftMargin': g.leftMargin * scale,
    # 'rightMargin': g.rightMargin * scale,
    'glyphSVGPath': glyphToSVGPath(g, -1),
    # 'ascender': font.info.ascender * scale,
    # 'descender': font.info.descender * scale,
    # 'baselineOffset': (font.info.unitsPerEm + font.info.descender) * scale,
    # 'unitsPerEm': font.info.unitsPerEm,

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

def genGlyph(glyphName, generateFrom, force):
  # generateFrom = (baseName, accentNames, offset, rawline)
  if generateFrom is not None:
    generateGlyph(font, generateFrom[3], agl)

  g = font.getGlyph(glyphName)

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


def genKerningInfo(font, glyphnames, nameToIdMap):
  kerning = font.kerning

  # load groups
  filename = os.path.join(font.path, 'groups.plist')
  groups = plistlib.readPlist(filename)

  pairs = []
  for kt in kerning.keys():
    v = kerning[kt]
    leftname, rightname = kt
    leftnames = []
    rightnames = []

    if leftname[0] == '@':
      leftnames = groups[leftname]
    else:
      leftnames = [leftname]

    if rightname[0] == '@':
      rightnames = groups[rightname]
    else:
      rightnames = [rightname]

    for lname in leftnames:
      for rname in rightnames:
        lnameId = nameToIdMap[lname]
        rnameId = nameToIdMap[rname]
        # print('%r' % [lnameId, rnameId, v])
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

argparser.add_argument(
  '-f', '-force', dest='force', action='store_const', const=True, default=False,
  help='Generate glyphs even though they appear to be up-to date.')

argparser.add_argument('ufopath', metavar='<ufopath>', type=str,
                       help='Path to UFO packages')

argparser.add_argument('glyphs', metavar='<glyphname>', type=str, nargs='*',
                       help='Only generate specific glyphs.')


args = argparser.parse_args()

if len(args.scale):
  scale = float(args.scale)

ufopath = args.ufopath.rstrip('/')

font = OpenFont(ufopath)
effectiveAscender = max(font.info.ascender, font.info.unitsPerEm)

srcdir = os.path.abspath(os.path.join(__file__, '..', '..'))

# print('\n'.join(font.keys()))
# sys.exit(0)

agl = loadAGL(os.path.join(srcdir, 'src', 'glyphlist.txt')) # { 2126: 'Omega', ... }

ignoreGlyphs = set(['.notdef', '.null'])
glyphnames = args.glyphs if len(args.glyphs) else font.keys()
glyphnameSet = set(glyphnames)
generatedGlyphNames = set()

diacriticComps = loadGlyphCompositions(os.path.join(srcdir, 'src', 'diacritics.txt'))
for glyphName, comp in diacriticComps.iteritems():
  if glyphName not in glyphnameSet:
    generatedGlyphNames.add(glyphName)
    glyphnames.append(glyphName)
    glyphnameSet.add(glyphName)

glyphnames = [gn for gn in glyphnames if gn not in ignoreGlyphs]
glyphnames.sort()

nameToIdMap, idToNameMap = genGlyphIDs(glyphnames)

glyphMetrics = {}

# jsonLines = []
svgLines = []
for glyphname in glyphnames:
  generateFrom = None
  if glyphname in generatedGlyphNames:
    generateFrom = diacriticComps[glyphname]
  svg, metrics = genGlyph(glyphname, generateFrom, force=args.force)
  # metrics: (width, advance, left, right)
  glyphMetrics[nameToIdMap[glyphname]] = metrics
  svgLines.append(svg.replace('\n', ''))

# print('{\n' + ',\n'.join(jsonLines) + '\n}')

svgtext = '\n'.join(svgLines)
# print(svgtext)

glyphsHtmlFilename = os.path.join(srcdir, 'docs', 'glyphs', 'index.html')

html = ''
with open(glyphsHtmlFilename, 'r') as f:
  html = f.read()

startMarker = '<div id="svgs">'
startPos = html.find(startMarker)

endMarker = '</div><!--END-SVGS'
endPos = html.find(endMarker, startPos + len(startMarker))

relfilename = os.path.relpath(glyphsHtmlFilename, os.getcwd())

if startPos == -1 or endPos == -1:
  msg = 'Could not find `<div id="svgs">...</div><!--END-SVGS` in %s'
  print(msg % relfilename, file=sys.stderr)
  sys.exit(1)

for name in glyphnames:
  if name == 'zero.tnum.slash':
    print('FOUND zero.tnum.slash')

kerning = genKerningInfo(font, glyphnames, nameToIdMap)
metaJson = '{\n'
metaJson += '"nameids":' + fmtJsonDict(idToNameMap) + ',\n'
metaJson += '"metrics":' + fmtJsonDict(glyphMetrics) + ',\n'
metaJson += '"kerning":' + fmtJsonList(kerning) + '\n'
metaJson += '}'
# metaHtml = '<script>var fontMetaData = ' + metaJson + ';</script>'

html = html[:startPos + len(startMarker)] + '\n' + svgtext + '\n' + html[endPos:]

print('write', relfilename)
with open(glyphsHtmlFilename, 'w') as f:
  f.write(html)

# JSON
jsonFilename = os.path.join(srcdir, 'docs', 'glyphs', 'metrics.json')
jsonFilenameRel = os.path.relpath(jsonFilename, os.getcwd())
print('write', jsonFilenameRel)
with open(jsonFilename, 'w') as f:
  f.write(metaJson)

metaJson