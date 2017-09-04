from fontTools.pens.basePen import BasePen

class QuartzPen(BasePen):

	"""Pen to draw onto a Quartz drawing context (Carbon.CG)."""

	def __init__(self, glyphSet, quartzContext):
		BasePen.__init__(self, glyphSet)
		self._context = quartzContext

	def _moveTo(self, (x, y)):
		self._context.CGContextMoveToPoint(x, y)

	def _lineTo(self, (x, y)):
		self._context.CGContextAddLineToPoint(x, y)

	def _curveToOne(self, (x1, y1), (x2, y2), (x3, y3)):
		self._context.CGContextAddCurveToPoint(x1, y1, x2, y2, x3, y3)

	def _closePath(self):
		self._context.closePath()
