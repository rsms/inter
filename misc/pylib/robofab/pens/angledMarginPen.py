from robofab.world import RFont
from fontTools.pens.basePen import BasePen
from robofab.misc.arrayTools import updateBounds, pointInRect, unionRect
from robofab.misc.bezierTools import calcCubicBounds, calcQuadraticBounds
from robofab.pens.filterPen import _estimateCubicCurveLength, _getCubicPoint
import math



__all__ = ["AngledMarginPen", "getAngledMargins", 
	"setAngledLeftMargin", "setAngledRightMargin",
	"centerAngledMargins"]



class AngledMarginPen(BasePen):
	"""
		Angled Margin Pen

		Pen to calculate the margins as if the margin lines were slanted
		according to the font.info.italicAngle.

		Notes:
		- this pen works on the on-curve points, and approximates the distance to curves.
		- results will be float.
		- when used in FontLab, the resulting margins may be slightly
			different from the values originally set, due to rounding errors.
		- similar to what RoboFog used to do.
		- RoboFog had a special attribute for "italicoffset", horizontal
		shift of all glyphs. This is missing in Robofab.
	"""
	def __init__(self, glyphSet, width, italicAngle):
		BasePen.__init__(self, glyphSet)
		self.width = width
		self._angle = math.radians(90+italicAngle)
		self.maxSteps = 100
		self.margin = None
		self._left = None
		self._right = None
		self._start = None
		self.currentPt = None
	
	def _getAngled(self, pt):
		r = (g.width + (pt[1] / math.tan(self._angle)))-pt[0]
		l = pt[0]-((pt[1] / math.tan(self._angle)))
		if self._right is None:
			self._right = r
		else:
			self._right = min(self._right, r)
		if self._left is None:
			self._left = l
		else:
			self._left = min(self._left, l)
		#print pt, l, r
		self.margin = self._left, self._right
		
	def _moveTo(self, pt):
		self._start = self.currentPt = pt

	def _addMoveTo(self):
		if self._start is None:
			return
		self._start = self.currentPt = None

	def _lineTo(self, pt):
		self._addMoveTo()
		self._getAngled(pt)

	def _curveToOne(self, pt1, pt2, pt3):
		step = 1.0/self.maxSteps
		factors = range(0, self.maxSteps+1)
		for i in factors:
			pt = _getCubicPoint(i*step, self.currentPt, pt1, pt2, pt3)
			self._getAngled(pt)
		self.currentPt = pt3
					
	def _qCurveToOne(self, bcp, pt):
		self._addMoveTo()
		# add curve tracing magic here.
		self._getAngled(pt)
		self.currentPt = pt3

def getAngledMargins(glyph, font):
	"""Get the angled margins for this glyph."""
	pen = AngledMarginPen(font, glyph.width, font.info.italicAngle)
	glyph.draw(pen)
	return pen.margin
	
def setAngledLeftMargin(glyph, font, value):
	"""Set the left angled margin to value, adjusted for font.info.italicAngle."""
	pen = AngledMarginPen(font, glyph.width, font.info.italicAngle)
	g.draw(pen)
	isLeft, isRight = pen.margin
	glyph.leftMargin += value-isLeft
	
def setAngledRightMargin(glyph, font, value):
	"""Set the right angled margin to value, adjusted for font.info.italicAngle."""
	pen = AngledMarginPen(font, glyph.width, font.info.italicAngle)
	g.draw(pen)
	isLeft, isRight = pen.margin
	glyph.rightMargin += value-isRight

def centerAngledMargins(glyph, font):
	"""Center the glyph on angled margins."""
	pen = AngledMarginPen(font, glyph.width, font.info.italicAngle)
	g.draw(pen)
	isLeft, isRight = pen.margin
	setAngledLeftMargin(glyph, font, (isLeft+isRight)*.5)
	setAngledRightMargin(glyph, font, (isLeft+isRight)*.5)
	
def guessItalicOffset(glyph, font):
	"""Guess the italic offset based on the margins of a symetric glyph.
		For instance H or I.
	"""
	l, r = getAngledMargins(glyph, font)
	return l - (l+r)*.5


if __name__ == "__main__":
	
	# example for FontLab, with a glyph open.
	from robofab.world import CurrentFont, CurrentGlyph
	g = CurrentGlyph()
	f = CurrentFont()

	print "margins!", getAngledMargins(g, f)
	# set the angled margin to a value
	m = 50
	setAngledLeftMargin(g, f, m)
	setAngledRightMargin(g, f, m)
	g.update()

