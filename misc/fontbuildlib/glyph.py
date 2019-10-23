import re
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from fontTools.pens.reverseContourPen import ReverseContourPen

# Directives are glyph-specific post-processing directives for the compiler.
# A directive is added to the "note" section of a glyph and takes the
# following form:
#
#   !post:DIRECTIVE
#
# Where DIRECTIVE is the name of a known directive.
# This string can appear anywhere in the glyph note.
# Directives are _not_ case sensitive but normalized by str.lower(), meaning
# that e.g. "removeoverlap" == "RemoveOverlap" == "REMOVEOVERLAP".
#
knownDirectives = set([
  'removeoverlap',  # applies overlap removal (boolean union)
])


_findDirectiveRegEx = re.compile(r'\!post:([^ ]+)', re.I | re.U)


def findGlyphDirectives(string): # -> set<string> | None
  directives = set()
  if string and len(string) > 0:
    for directive in _findDirectiveRegEx.findall(string):
      directive = directive.lower()
      if directive in knownDirectives:
        directives.add(directive)
      else:
        print(
          'unknown glyph directive !post:%s in glyph %s' % (directive, g.name),
          file=sys.stderr
        )
  return directives



def composedGlyphIsTrivial(g):
  # A trivial glyph is one that does not use components or where component transformation
  # does not include mirroring (i.e. "flipped").
  if g.components and len(g.components) > 0:
    for c in g.components:
      # has non-trivial transformation? (i.e. scaled)
      # Example of optimally trivial transformation:
      #   (1, 0, 0, 1, 0, 0)  no scale or offset
      # Example of scaled transformation matrix:
      #   (-1.0, 0, 0.3311, 1, 1464.0, 0)  flipped x axis, sheered and offset
      #
      xScale = c.transformation[0]
      yScale = c.transformation[3]
      # If glyph is reflected along x or y axes, it won't slant well.
      if xScale < 0 or yScale < 0:
        return False
  return True



def decomposeGlyphs(ufos, glyphNamesToDecompose):
  for ufo in ufos:
    for glyphname in glyphNamesToDecompose:
      glyph = ufo[glyphname]
      _deepCopyContours(ufo, glyph, glyph, Transform())
      glyph.clearComponents()



def _deepCopyContours(ufo, parent, component, transformation):
  """Copy contours from component to parent, including nested components."""
  for nested in component.components:
    _deepCopyContours(
      ufo,
      parent,
      ufo[nested.baseGlyph],
      transformation.transform(nested.transformation)
    )
  if component != parent:
    pen = TransformPen(parent.getPen(), transformation)
    # if the transformation has a negative determinant, it will reverse
    # the contour direction of the component
    xx, xy, yx, yy = transformation[:4]
    if xx*yy - xy*yx < 0:
      pen = ReverseContourPen(pen)
    component.draw(pen)