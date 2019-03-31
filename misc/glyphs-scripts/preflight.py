#MenuTitle: Preflight
# -*- coding: utf-8 -*-
__doc__="""
Checks for bad paths and anchors
"""

import AppKit

Glyphs.clearLog()
Glyphs.showMacroWindow()

mainRunLoop = AppKit.NSRunLoop.mainRunLoop()

_lowerCaseGlyphNames = None

def getLowerCaseGlyphNames():
  global _lowerCaseGlyphNames
  if _lowerCaseGlyphNames is None:
    # TODO: split with regexp to allow more than one space as a separator
    _lowerCaseGlyphNames = set(font.classes['Lowercase'].code.strip().split(' '))
  return _lowerCaseGlyphNames

def yieldAppMain():
  mainRunLoop.runMode_beforeDate_(AppKit.NSRunLoopCommonModes, AppKit.NSDate.new())

def headline(titleString):
  print("\n------ %s ------" % titleString.upper())
  
def log(glyphName, layerName, msg):
  if layerName != "":
    print("[glyph] %s \t Layer %s: %s." % ( glyphName, layerName, msg ))
  elif glyphName != "":
    print("[glyph] %s \t - \t %s." % ( glyphName, msg ))
  else:
    print("[info] %s." % ( msg ))

def masterLayersIterator(font):
  for g in font.glyphs:
    for master in font.masters:
      yield g.layers[master.id], g
    yieldAppMain()

def checkForOpenPaths(font):
  headline("Checking for open paths")
  ok = True
  for layer, g in masterLayersIterator(font):
    openPathsFound = 0
    for path in layer.paths:
      if not path.closed:
        openPathsFound += 1
    if openPathsFound > 0:
      ok = False
      log(g.name, layer.name, "%d open path(s) found" % openPathsFound)
  if ok:
    print("OK")


def checkForPathDirections(font):
  headline("Checking for path directions")
  ok = True
  for layer, g in masterLayersIterator(font):
    firstPath = layer.paths[0]
    if firstPath and firstPath.direction != -1:
      ok = False
      if len(layer.paths) > 1:
        msg = "Bad path order or direction."
      else:
        msg = "Bad path direction."
      log(g.name, layer.name, msg)
  if ok:
    print("OK")


def checkForPointsOutOfBounds(font):
  headline("Checking for nodes out of bounds")
  ok = True
  for layer, g in masterLayersIterator(font):
    nodesOutOfBounds = 0
    anchorsOutOfBounds = []

    for path in layer.paths:
      for n in path.nodes:
        if abs(n.x) > 32766 or abs(n.y) > 32766:
          nodesOutOfBounds += 1
    for a in layer.anchors:
      if abs(a.x) > 32766 or abs(a.y) > 32766:
        anchorsOutOfBounds.append(a.name)
    
    if nodesOutOfBounds:
      ok = False
      log(g.name, layer.name, "%d node(s) out of bounds" % nodesOutOfBounds)
    
    if anchorsOutOfBounds:
      ok = False
      log(g.name, layer.name, "%d anchor(s) out of bounds (%r)" % (
        len(anchorsOutOfBounds),
        anchorsOutOfBounds
      ))
  if ok:
    print("OK")
        

def checkUnicode(font):
  headline("Checking Unicodes")
  ok = True

  listOfUnicodes = [ (g.name, g.unicode) for g in font.glyphs if g.unicode != None ]
  numberOfGlyphs = len(listOfUnicodes)

  # glyphsWithoutUnicodes = [ g.name for g in allGlyphs if g.unicode == None ]
  # for gName in glyphsWithoutUnicodes:
  #   log( gName, "", "Warning: No Unicode value set" )

  for i in range(numberOfGlyphs - 1):
    firstGlyph = listOfUnicodes[i]
    for j in range(i+1, numberOfGlyphs):
      secondGlyph = listOfUnicodes[j]
      if firstGlyph[1] == secondGlyph[1]:
        ok = False
        log(
          "%s & %s" % (firstGlyph[0], secondGlyph[0]),
          "-",
          "Both glyphs carry same Unicode value %s" % (firstGlyph[1])
        )
  if ok:
    print("OK")


def checkVerticalMetrics(font):
  headline("Checking vertical metrics")
  ascender = 0
  descender = 0
  capHeight = 0
  lowerCase = getLowerCaseGlyphNames()
  ok = True

  for master in font.masters:
    if ascender == 0:
      ascender = master.ascender
    elif ascender != master.ascender:
      print('ascender varies with masters; vertical metrics must be same in all masters')
      ok = False

    if capHeight == 0:
      capHeight = master.capHeight
    elif capHeight != master.capHeight:
      print('capHeight varies with masters; vertical metrics must be same in all masters')
      ok = False

    if descender == 0:
      descender = master.descender
    elif descender != master.descender:
      print('descender varies with masters; vertical metrics must be same in all masters')
      ok = False

  for master in font.masters:
    for glyph in font.glyphs:
      if not glyph.export or glyph.name not in lowerCase:
        continue

      layer = glyph.layers[master.id]

      # get ymin of current layer
      ymin = layer.bounds.origin.y
      if ymin < descender:
        ok = False
        log(glyph.name, layer.name,
          'Warning: lower than descender (ymin=%r, descender=%r)' % (
          ymin, descender))
  if ok:
    print("OK")


font = Glyphs.font
font.disableUpdateInterface()
try:
  checkForOpenPaths(font)
  checkForPathDirections(font)
  checkForPointsOutOfBounds(font)
  checkUnicode(font)
  checkVerticalMetrics(font)
finally:
  font.enableUpdateInterface()
