#MenuTitle: Fixup Vertical Metrics
# -*- coding: utf-8 -*-

font = Glyphs.font
caps = set(font.classes['Uppercase'].code.strip().split(' '))
lowercase = set(font.classes['Lowercase'].code.strip().split(' '))

print(font)

mainMaxDescent = 0
mainMaxDescentGlyph = ""
maxDescent = 0
mainMaxAscent = 0
mainMaxAscentGlyph = ""
maxAscent = 0
typoAscender = 0
typoDescender = 0

for master in font.masters:
  ta = max(master.ascender, master.capHeight)
  if typoAscender == 0:
    typoAscender = ta
  elif typoAscender != ta:
    raise Error('ascender or capHeight varies with masters; vertical metrics must be same in all masters')

  td = master.descender
  if typoDescender == 0:
    typoDescender = td
  elif typoDescender != td:
    raise Error('descender or capHeight varies with masters; vertical metrics must be same in all masters')

  for glyph in font.glyphs:
    if not glyph.export:
      continue

    layer = glyph.layers[master.id]

    # get descender of current layer
    descent = layer.bounds.origin.y
    
    # get ascender of current layer
    ascent = layer.bounds.size.height + descent  

    # if descent/ascent of current layer is greater than previous max descents/ascents, update the max descent/ascent
    if descent <= maxDescent:
      maxDescent = descent
      maxDescentGlyph = glyph.name
      
    if ascent >= maxAscent:
      maxAscent = ascent
      maxAscentGlyph = glyph.name

    # get descender of current layer
    descent = layer.bounds.origin.y
        
    # get ascender of current layer (total height of layer, subtracting value of descender)
    ascent = layer.bounds.size.height + descent

    # get maximums of only letters in list vars, for typo and hhea values
    if glyph.name in caps and ascent >= mainMaxAscent:
      mainMaxAscent = ascent
      mainMaxAscentGlyph = glyph.name

    if glyph.name in lowercase and descent <= mainMaxDescent:
      # if descent/ascent of current layer is greater than previous max descents/ascents, update the max descent/ascent
      mainMaxDescent = descent
      mainMaxDescentGlyph = glyph.name
      

# check values for sanity
# print(maxDescentGlyph, maxDescent, maxAscentGlyph, maxAscent)

# make lineGap so that the total of `ascent + descent + lineGap` equals 120% of UPM size
# UPM = font.upm
# totalSize = maxAscent + abs(maxDescent)
# lineGap = int((UPM * 1.2)) - totalSize
# print(UPM, UPM * 1.2, totalSize, lineGap)

## use highest/lowest points to set custom parameters for winAscent and winDescent
## following vertical metric schema from https://github.com/googlefonts/gf-docs/tree/master/VerticalMetrics

font.customParameters["Use Typo Metrics"] = True

# ascenderDelta = max(abs(typoAscender), abs(mainMaxAscent)) - min(abs(typoAscender), abs(mainMaxAscent))
descenderDelta = max(typoDescender, mainMaxDescent) - min(typoDescender, mainMaxDescent)

if descenderDelta == 0:
  print('descenderDelta is zero -- no change')
else:
  print('descenderDelta:', descenderDelta)

  for master in font.masters:

    # Win Ascent/Descent = Font bbox yMax/yMin
    master.customParameters["winAscent"] = maxAscent
    master.customParameters["winDescent"] = abs(maxDescent)

    # no/zero line gap
    # if "typoLineGap" in master.customParameters:
    #   del master.customParameters["typoLineGap"]
    # if "hheaLineGap" in master.customParameters:
    #   del master.customParameters["hheaLineGap"]
    master.customParameters["typoLineGap"] = 0
    master.customParameters["hheaLineGap"] = 0

    master.customParameters["typoDescender"] = typoDescender - descenderDelta
    master.customParameters["hheaDescender"] = typoDescender - descenderDelta

    master.customParameters["typoAscender"] = typoAscender + descenderDelta
    master.customParameters["hheaAscender"] = typoAscender + descenderDelta
