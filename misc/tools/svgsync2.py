#!/usr/bin/env python
# encoding: utf8
#
# Sync glyph shapes between SVG and UFO, creating a bridge between UFO and Figma.
#
import os
import sys
import argparse
import re
from StringIO import StringIO
from hashlib import sha256
from xml.dom.minidom import parseString as xmlparseString
from svgpathtools import svg2paths, parse_path, Path, Line, CubicBezier
from base64 import b64encode

# from robofab.world import world, RFont, RGlyph, OpenFont, NewFont
from robofab.objects.objectsRF import RFont, RGlyph, OpenFont, NewFont, RContour
from robofab.objects.objectsBase import MOVE, LINE, CORNER, CURVE, QCURVE, OFFCURVE

font = None  # RFont
ufopath = ''
svgdir = ''
effectiveAscender = 0


def num(s):
  return int(s) if s.find('.') == -1 else float(s)


def glyphToSVGPath(g, yMul=-1):
  commands = {'move':'M','line':'L','curve':'Y','offcurve':'X','offCurve':'X'}
  svg = ''
  contours = []
  if len(g.components):
    font.newGlyph('__svgsync')
    new = font['__svgsync']
    new.width = g.width
    new.appendGlyph(g)
    new.decompose()
    g = new
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
          end = ' ' + str(p.x) + ' ' + str(p.y * yMul)
      contour += ' ' + command + str(p.x) + ' ' + str(p.y * yMul)
    svg += ' ' + contour + end + 'z'
  if font.has_key('__svgsync'):
    font.removeGlyph('__svgsync')
  return svg.strip()


def vec2(x, y):
  return float(x) + float(y) * 1j


def glyphToPaths(g, yMul=-1):
  paths = []
  contours = []
  yOffs = -font.info.unitsPerEm

  # decompose components
  if len(g.components):
    font.newGlyph('__svgsync')
    ng = font['__svgsync']
    ng.width = g.width
    ng.appendGlyph(g)
    ng.decompose()
    g = ng

  for c in g:
    curve = False
    points = c.points
    path = Path()
    currentPos = 0j
    controlPoints = []

    for x in range(len(points)):
      p = points[x]
      # print 'p#' + str(x) + '.type = ' + repr(p.type)

      if p.type == 'move':
        currentPos = vec2(p.x, (p.y + yOffs) * yMul)
      elif p.type == 'offcurve':
        controlPoints.append(p)
      elif p.type == 'curve':
        pos = vec2(p.x, (p.y + yOffs) * yMul)
        if len(controlPoints) == 2:
          cp1, cp2 = controlPoints
          path.append(CubicBezier(
            currentPos,
            vec2(cp1.x, (cp1.y + yOffs) * yMul),
            vec2(cp2.x, (cp2.y + yOffs) * yMul),
            pos))
        else:
          if len(controlPoints) != 1:
            raise Exception('unexpected number of control points for curve')
          cp = controlPoints[0]
          path.append(QuadraticBezier(currentPos, vec2(cp.x, (cp.y + yOffs) * yMul), pos))
        currentPos = pos
        controlPoints = []
      elif p.type == 'line':
        pos = vec2(p.x, (p.y + yOffs) * yMul)
        path.append(Line(currentPos, pos))
        currentPos = pos

    paths.append(path)

  if font.has_key('__svgsync'):
    font.removeGlyph('__svgsync')

  return paths


def maybeAddMove(contour, x, y, smooth):
  if len(contour.segments) == 0:
    contour.appendSegment(MOVE, [(x, y)], smooth=smooth)



svgPathDataRegEx = re.compile(r'(?:([A-Z])\s*|)([0-9\.\-\+eE]+)')


def drawSVGPath(g, d, tr):
  yMul = -1
  xOffs = tr[0]
  yOffs = -(font.info.unitsPerEm - tr[1])

  for pathd in d.split('M'):
    pathd = pathd.strip()
    # print 'pathd', pathd
    if len(pathd) == 0:
      continue
    i = 0
    closePath = False
    if pathd[-1] == 'z':
      closePath = True
      pathd = pathd[0:-1]

    pv = []
    for m in svgPathDataRegEx.finditer('M' + pathd):
      if m.group(1) is not None:
        pv.append(m.group(1) + m.group(2))
      else:
        pv.append(m.group(2))

    initX = 0
    initY = 0

    pen = g.getPen()

    while i < len(pv):
      pd = pv[i]; i += 1
      cmd = pd[0]
      x = num(pd[1:]) + xOffs
      y = (num(pv[i]) + yOffs) * yMul; i += 1

      if cmd == 'M':
        # print cmd, x, y, '/', num(pv[i-2][1:])
        initX = x
        initY = y
        pen.moveTo((x, y))
        continue

      if cmd == 'C':
        # Bezier curve: "C x1 y1, x2 y2, x y"
        x1 = x
        y1 = y
        x2 = num(pv[i]) + xOffs; i += 1
        y2 = (num(pv[i]) + yOffs) * yMul; i += 1
        x  = num(pv[i]) + xOffs; i += 1
        y  = (num(pv[i]) + yOffs) * yMul; i += 1
        pen.curveTo((x1, y1), (x2, y2), (x, y))
        # print cmd, x1, y1, x2, y2, x, y

      elif cmd == 'L':
        pen.lineTo((x, y))

      else:
        raise Exception('unexpected SVG path command %r' % cmd)

    if closePath:
      pen.closePath()
    else:
      pen.endPath()
    # print 'path ended. closePath:', closePath


def glyphToSVG(g, path, hash):
  width = g.width
  height = font.info.unitsPerEm

  d = {
    'name': g.name,
    'width': width,
    'height': effectiveAscender - font.info.descender,
    'effectiveAscender': effectiveAscender,
    'leftMargin': g.leftMargin,
    'rightMargin': g.rightMargin,
    'd': path.d(use_closed_attrib=True),
    'ascender': font.info.ascender,
    'descender': font.info.descender,
    'baselineOffset': height + font.info.descender,
    'unitsPerEm': font.info.unitsPerEm,
    'hash': hash,
  }

  svg  = '''
<svg xmlns="http://www.w3.org/2000/svg" width="%(width)d" height="%(height)d" data-svgsync-hash="%(hash)s">
  <g id="%(name)s">
    <path d="%(d)s" transform="translate(0 %(effectiveAscender)d)" />
    <rect x="0" y="0" width="%(width)d" height="%(height)d" fill="" stroke="black" />
  </g>
</svg>
  ''' % d
  # print svg
  return svg.strip()


def _findPathNodes(n, paths, defs, uses, isDef=False):
  for cn in n.childNodes:
    if cn.nodeName == 'path':
      if isDef:
        defs[cn.getAttribute('id')] = cn
      else:
        paths.append(cn)
    elif cn.nodeName == 'use':
      uses[cn.getAttribute('xlink:href').lstrip('#')] = {'useNode': cn, 'targetNode': None}
    elif cn.nodeName == 'defs':
      _findPathNodes(cn, paths, defs, uses, isDef=True)
    elif not isinstance(cn, basestring) and cn.childNodes and len(cn.childNodes) > 0:
      _findPathNodes(cn, paths, defs, uses, isDef)
  # return translate


def findPathNodes(n, isDef=False):
  paths = []
  defs = {}
  uses = {}
  # <g id="Canvas" transform="translate(-3677 -24988)">
  #  <g id="six 2">
  #   <g id="six">
  #    <g id="Vector">
  #     <use xlink:href="#path0_fill" transform="translate(3886 25729)"/>
  # ...
  # <defs>
  #  <path id="path0_fill" ...
  #
  _findPathNodes(n, paths, defs, uses)

  # flatten uses & defs
  for k in uses.keys():
    dfNode = defs.get(k)
    if dfNode is not None:
      v = uses[k]
      v['targetNode'] = dfNode
      if dfNode.nodeName == 'path':
        useNode = v['useNode']
        useNode.parentNode.replaceChild(dfNode, useNode)
        attrs = useNode.attributes
        for k in attrs.keys():
          if k != 'xlink:href':
            dfNode.setAttribute(k, attrs[k])
        paths.append(dfNode)

    else:
      del defs[k]

  return paths


def nodeTranslation(path, x=0, y=0):
  tr = path.getAttribute('transform')
  if tr is not None:
    if not isinstance(tr, basestring):
      tr = tr.value
    if len(tr) > 0:
      m = re.match(r"translate\s*\(\s*(?P<x>[\-\d\.eE]+)[\s,]*(?P<y>[\-\d\.eE]+)\s*\)", tr)
      if m is not None:
        x += num(m.group('x'))
        y += num(m.group('y'))
      else:
        raise Exception('Unable to handle transform="%s"' % tr)
        # m = re.match(r"matrix\s*\(\s*(?P<a>[\-\d\.eE]+)[\s,]*(?P<b>[\-\d\.eE]+)[\s,]*(?P<c>[\-\d\.eE]+)[\s,]*(?P<d>[\-\d\.eE]+)[\s,]*(?P<e>[\-\d\.eE]+)[\s,]*(?P<f>[\-\d\.eE]+)[\s,]*", tr)
        # if m is not None:
        #   a, b, c = num(m.group('a')), num(m.group('b')), num(m.group('c'))
        #   d, e, f = num(m.group('d')), num(m.group('e')), num(m.group('f'))
        #   # matrix -1 0 0 -1 -660.719 31947
        #   print 'matrix', a, b, c, d, e, f
        # # matrix(-1 0 -0 -1 -2553 31943)
  pn = path.parentNode
  if pn is not None and pn.nodeName != '#document':
    x, y = nodeTranslation(pn, x, y)
  return (x, y)


def glyphUpdateFromSVG(g, svgCode):
  doc = xmlparseString(svgCode)
  svg = doc.documentElement
  paths = findPathNodes(svg)
  if len(paths) == 0:
    raise Exception('no <path> found in SVG')
  path = paths[0]
  if len(paths) != 1:
    for p in paths:
      id = p.getAttribute('id')
      if id is not None and id.find('stroke') == -1:
        path = p
        break

  tr = nodeTranslation(path)
  d = path.getAttribute('d')
  g.clearContours()
  drawSVGPath(g, d, tr)


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


def findSvgSyncHashInSVG(svgCode):
  # with open(svgFile, 'r') as f:
  # svgCode = f.readline(512)
  r = re.compile(r'^\s*<svg[^>]+data-svgsync-hash="([^"]*)".+')
  m = r.match(svgCode)
  if m is not None:
    return m.group(1)
  return None


def computeSVGHashFromSVG(g):
  # h = sha256()
  return 'abc123'


def encodePath(o, path):
  o.write(path.d())


def hashPaths(paths):
  h = sha256()
  for path in paths:
    h.update(path.d()+';')
  return b64encode(h.digest(), '-_')


def svgGetPaths(svgCode):
  doc = xmlparseString(svgCode)
  svg = doc.documentElement
  paths = findPathNodes(svg)
  isFigmaSVG = svgCode.find('Figma</desc>') != -1

  if len(paths) == 0:
    return paths, (0,0)
  
  paths2 = []
  for path in paths:
    id = path.getAttribute('id')
    if not isFigmaSVG or (id is None or id.find('stroke') == -1):
      tr = nodeTranslation(path)
      d = path.getAttribute('d')
      paths2.append((d, tr))

  return paths2, isFigmaSVG


def translatePath(path, trX, trY):
  pass


def parseSVG(svgFile):
  svgCode = None
  with open(svgFile, 'r') as f:
    svgCode = f.read()

  existingSvgHash = findSvgSyncHashInSVG(svgCode)
  print 'hash in SVG file:', existingSvgHash

  svgPathDefs, isFigmaSVG = svgGetPaths(svgCode)
  paths = []
  for pathDef, tr in svgPathDefs:
    print 'pathDef:', pathDef, 'tr:', tr
    path = parse_path(pathDef)
    if tr[0] != 0 or tr[1] != 0:
      path = path.translated(vec2(*tr))
    paths.append(path)

  return paths, existingSvgHash


def syncGlyphUFOToSVG(g, glyphFile, svgFile, mtime, hasSvgFile):
  # # Let's print out the first path object and the color it was in the SVG
  # # We'll see it is composed of two CubicBezier objects and, in the SVG file it
  # # came from, it was red
  # paths, attributes, svg_attributes = svg2paths(svgFile, return_svg_attributes=True)
  # print('svg_attributes:', repr(svg_attributes))
  # # redpath = paths[0]
  # # redpath_attribs = attributes[0]
  # print(paths)
  # print(attributes)
  # wsvg(paths, attributes=attributes, svg_attributes=svg_attributes, filename=svgFile + '-x.svg')

  # existingSVGHash = readSVGHash(svgFile)
  svgPaths = None
  existingSVGHash = None
  if hasSvgFile:
    svgPaths, existingSVGHash = parseSVG(svgFile)
    print 'existingSVGHash:', existingSVGHash
    print 'svgPaths:\n', '\n'.join([p.d() for p in svgPaths])
    svgHash = hashPaths(svgPaths)
    print 'hash(SVG-glyph) =>', svgHash

  # computedSVGHash = computeSVGHashFromSVG(svgFile)
  # print 'computeSVGHashFromSVG:', computedSVGHash

  ufoPaths = glyphToPaths(g)
  print 'ufoPaths:\n', '\n'.join([p.d() for p in ufoPaths])
  ufoGlyphHash = hashPaths(ufoPaths)
  print 'hash(UFO-glyph) =>', ufoGlyphHash

  # svg = glyphToSVG(g, ufoGlyphHash)

  # with open('/Users/rsms/src/interface/_local/svgPaths.txt', 'w') as f:
  #   f.write(svgPaths[0].d())
  # with open('/Users/rsms/src/interface/_local/ufoPaths.txt', 'w') as f:
  #   f.write(ufoPaths[0].d())
  # print svgPaths[0].d() == ufoPaths[0].d()

  # svgHash = hashPaths()
  # print 'hash(UFO-glyph) =>', pathHash

  sys.exit(1)
  if pathHash == existingSVGHash:
    return (None, 0) # did not change

  svg = glyphToSVG(g, pathHash)
  sys.exit(1)

  writeFileAndMkDirsIfNeeded(svgFile, svg)
  os.utime(svgFile, (mtime, mtime))
  print 'svgsync write', svgFile

  g.lib['svgsync.hash'] = pathHash
  return (glyphFile, mtime)


def syncGlyphSVGToUFO(glyphname, svgFile):
  print glyphname + ': SVG -> UFO'
  sys.exit(1)
  svg = ''
  with open(svgFile, 'r') as f:
    svg = f.read()
  g = font.getGlyph(glyphname)
  glyphUpdateFromSVG(g, svg)


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


def syncGlyph(glyphname, createSVG=False):  # => (glyphname, mtime) or (None, 0) if noop
  glyphFile, glyphStat = findGlifFile(glyphname)

  svgFile = os.path.join(svgdir, glyphname + '.svg')
  svgStat = stat(svgFile)

  if glyphStat is None and svgStat is None:
    raise Exception("glyph %r doesn't exist in UFO or SVG directory" % glyphname)

  c = cmp(
    0 if glyphStat is None else glyphStat.st_mtime,
    0 if svgStat is None else svgStat.st_mtime
  )

  g = font.getGlyph(glyphname)
  ufoPathHash = g.lib['svgsync.hash'] if 'svgsync.hash' in g.lib else None
  print '[syncGlyph] g.lib["svgsync.hash"] =', ufoPathHash

  c = 1 # XXX DEBUG

  if c < 0:
    syncGlyphSVGToUFO(glyphname, svgFile)
    return (glyphFile, svgStat.st_mtime) # glif file in UFO change + it's new mtime
  elif c > 0 and (svgStat is not None or createSVG):
    print glyphname + ': UFO -> SVG'
    return syncGlyphUFOToSVG(
      g,
      glyphFile,
      svgFile,
      glyphStat.st_mtime,
      hasSvgFile=svgStat is not None
    )

  return (None, 0) # UFO did not change


# ————————————————————————————————————————————————————————————————————————
# main

argparser = argparse.ArgumentParser(description='Convert UFO glyphs to SVG')

argparser.add_argument('--svgdir', dest='svgdir', metavar='<dir>', type=str,
                       default='',
                       help='Write SVG files to <dir>. If not specified, SVG files are' +
                       ' written to: {dirname(<ufopath>)/svg/<familyname>/<style>')

argparser.add_argument('ufopath', metavar='<ufopath>', type=str,
                       help='Path to UFO packages')

argparser.add_argument('glyphs', metavar='<glyphname>', type=str, nargs='*',
                       help='Glyphs to convert. Converts all if none specified.')

args = argparser.parse_args()

ufopath = args.ufopath.rstrip('/')

font = OpenFont(ufopath)
effectiveAscender = max(font.info.ascender, font.info.unitsPerEm)

svgdir = args.svgdir
if len(svgdir) == 0:
  svgdir = os.path.join(
    os.path.dirname(ufopath),
    'svg',
    font.info.familyName,
    font.info.styleName
  )

print 'svgsync sync %s (%s)' % (font.info.familyName, font.info.styleName)

createSVGs = len(args.glyphs) > 0
glyphnames = args.glyphs if len(args.glyphs) else font.keys()

modifiedGlifFiles = []
for glyphname in glyphnames:
  glyphFile, mtime = syncGlyph(glyphname, createSVG=createSVGs)
  if glyphFile is not None:
    modifiedGlifFiles.append((glyphFile, mtime))

if len(modifiedGlifFiles) > 0:
  font.save()
  for glyphFile, mtime in modifiedGlifFiles:
    os.utime(glyphFile, (mtime, mtime))
    print 'svgsync write', glyphFile

