from fontTools.pens.basePen import BasePen
from robofab.misc.arrayTools import updateBounds, pointInRect, unionRect
from robofab.misc.bezierTools import calcCubicBounds, calcQuadraticBounds


__all__ = ["BoundsPen", "ControlBoundsPen"]


class ControlBoundsPen(BasePen):

	"""Pen to calculate the "control bounds" of a shape. This is the
	bounding box of all control points __on closed paths__, so may be larger than the
	actual bounding box if there are curves that don't have points
	on their extremes.
	
	Single points, or anchors, are ignored.

	When the shape has been drawn, the bounds are available as the
	'bounds' attribute of the pen object. It's a 4-tuple:
		(xMin, yMin, xMax, yMax)
		
	This replaces fontTools/pens/boundsPen (temporarily?)
	The fontTools bounds pen takes lose anchor points into account, 
	this one doesn't.
	"""

	def __init__(self, glyphSet):
		BasePen.__init__(self, glyphSet)
		self.bounds = None
		self._start = None

	def _moveTo(self, pt):
		self._start = pt
	
	def _addMoveTo(self):
		if self._start is None:
			return
		bounds = self.bounds
		if bounds:
			self.bounds = updateBounds(bounds, self._start)
		else:
			x, y = self._start
			self.bounds = (x, y, x, y)
		self._start = None

	def _lineTo(self, pt):
		self._addMoveTo()
		self.bounds = updateBounds(self.bounds, pt)

	def _curveToOne(self, bcp1, bcp2, pt):
		self._addMoveTo()
		bounds = self.bounds
		bounds = updateBounds(bounds, bcp1)
		bounds = updateBounds(bounds, bcp2)
		bounds = updateBounds(bounds, pt)
		self.bounds = bounds

	def _qCurveToOne(self, bcp, pt):
		self._addMoveTo()
		bounds = self.bounds
		bounds = updateBounds(bounds, bcp)
		bounds = updateBounds(bounds, pt)
		self.bounds = bounds


class BoundsPen(ControlBoundsPen):

	"""Pen to calculate the bounds of a shape. It calculates the
	correct bounds even when the shape contains curves that don't
	have points on their extremes. This is somewhat slower to compute
	than the "control bounds".

	When the shape has been drawn, the bounds are available as the
	'bounds' attribute of the pen object. It's a 4-tuple:
		(xMin, yMin, xMax, yMax)
	"""

	def _curveToOne(self, bcp1, bcp2, pt):
		self._addMoveTo()
		bounds = self.bounds
		bounds = updateBounds(bounds, pt)
		if not pointInRect(bcp1, bounds) or not pointInRect(bcp2, bounds):
			bounds = unionRect(bounds, calcCubicBounds(
					self._getCurrentPoint(), bcp1, bcp2, pt))
		self.bounds = bounds

	def _qCurveToOne(self, bcp, pt):
		self._addMoveTo()
		bounds = self.bounds
		bounds = updateBounds(bounds, pt)
		if not pointInRect(bcp, bounds):
			bounds = unionRect(bounds, calcQuadraticBounds(
					self._getCurrentPoint(), bcp, pt))
		self.bounds = bounds

