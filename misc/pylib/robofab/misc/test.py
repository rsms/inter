"""
doc test requires fontTools to compare and defon to make the test font.
"""

import random
from fontTools.pens.basePen import BasePen

from fontTools.misc import arrayTools
from fontTools.misc import bezierTools

import robofab.misc.arrayTools as noNumpyArrayTools
import robofab.misc.bezierTools as noNumpyBezierTools


def drawMoveTo(pen, maxBox):
    pen.moveTo((maxBox*random.random(), maxBox*random.random()))
    
def drawLineTo(pen, maxBox):
    pen.lineTo((maxBox*random.random(), maxBox*random.random()))

def drawCurveTo(pen, maxBox):
    pen.curveTo((maxBox*random.random(), maxBox*random.random()),
                (maxBox*random.random(), maxBox*random.random()),
                (maxBox*random.random(), maxBox*random.random()))

def drawClosePath(pen):
    pen.closePath()

def createRandomFont():
    from defcon import Font
    
    maxGlyphs = 1000
    maxContours = 10
    maxSegments = 10
    maxBox = 700
    drawCallbacks = [drawLineTo, drawCurveTo]
    f = Font()
    for i in range(maxGlyphs):
        name = "%s" %i
        f.newGlyph(name)
        g = f[name]
        g.width = maxBox
        pen = g.getPen()
        for c in range(maxContours):
            drawMoveTo(pen, maxBox)
            for s in range(maxSegments):            
                random.choice(drawCallbacks)(pen, maxBox)
            drawClosePath(pen)
    return f

class BoundsPen(BasePen):
    
    def __init__(self, glyphSet, at, bt):
        BasePen.__init__(self, glyphSet)
        self.bounds = None
        self._start = None
        self._arrayTools = at
        self._bezierTools = bt
    
    def _moveTo(self, pt):
        self._start = pt
    
    def _addMoveTo(self):
        if self._start is None:
            return
        bounds = self.bounds
        if bounds:
            self.bounds = self._arrayTools.updateBounds(bounds, self._start)
        else:
            x, y = self._start
            self.bounds = (x, y, x, y)
        self._start = None

    def _lineTo(self, pt):
        self._addMoveTo()
        self.bounds = self._arrayTools.updateBounds(self.bounds, pt)

    def _curveToOne(self, bcp1, bcp2, pt):
        self._addMoveTo()
        bounds = self.bounds
        bounds = self._arrayTools.updateBounds(bounds, pt)
        if not self._arrayTools.pointInRect(bcp1, bounds) or not self._arrayTools.pointInRect(bcp2, bounds):
            bounds = self._arrayTools.unionRect(bounds, self._bezierTools.calcCubicBounds(
                    self._getCurrentPoint(), bcp1, bcp2, pt))
        self.bounds = bounds

    def _qCurveToOne(self, bcp, pt):
        self._addMoveTo()
        bounds = self.bounds
        bounds = self._arrayTools.updateBounds(bounds, pt)
        if not self._arrayTools.pointInRect(bcp, bounds):
            bounds = self._arrayToolsunionRect(bounds, self._bezierTools.calcQuadraticBounds(
                    self._getCurrentPoint(), bcp, pt))
        self.bounds = bounds



def _testFont(font):
    succes = True
    for glyph in font:
        fontToolsBoundsPen = BoundsPen(font, arrayTools, bezierTools)
        glyph.draw(fontToolsBoundsPen)
        noNumpyBoundsPen = BoundsPen(font, noNumpyArrayTools, noNumpyBezierTools)
        glyph.draw(noNumpyBoundsPen)
        if fontToolsBoundsPen.bounds != noNumpyBoundsPen.bounds:
            succes = False
    return succes

    
def testCompareAgainstFontTools():
    """
    >>> font = createRandomFont()
    >>> _testFont(font)
    True
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()