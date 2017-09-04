__all__ = ["AbstractPointPen", "BasePointToSegmentPen", "PrintingPointPen",
           "PrintingSegmentPen", "SegmentPrintingPointPen"]


class AbstractPointPen:

	def beginPath(self):
		"""Start a new sub path."""
		raise NotImplementedError

	def endPath(self):
		"""End the current sub path."""
		raise NotImplementedError

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		"""Add a point to the current sub path."""
		raise NotImplementedError

	def addComponent(self, baseGlyphName, transformation):
		"""Add a sub glyph."""
		raise NotImplementedError


class BasePointToSegmentPen(AbstractPointPen):

	"""Base class for retrieving the outline in a segment-oriented
	way. The PointPen protocol is simple yet also a little tricky,
	so when you need an outline presented as segments but you have
	as points, do use this base implementation as it properly takes
	care of all the edge cases.
	"""

	def __init__(self):
		self.currentPath = None

	def beginPath(self):
		assert self.currentPath is None
		self.currentPath = []

	def _flushContour(self, segments):
		"""Override this method.

		It will be called for each non-empty sub path with a list
		of segments: the 'segments' argument.

		The segments list contains tuples of length 2:
			(segmentType, points)

		segmentType is one of "move", "line", "curve" or "qcurve".
		"move" may only occur as the first segment, and it signifies
		an OPEN path. A CLOSED path does NOT start with a "move", in
		fact it will not contain a "move" at ALL.

		The 'points' field in the 2-tuple is a list of point info
		tuples. The list has 1 or more items, a point tuple has
		four items:
			(point, smooth, name, kwargs)
		'point' is an (x, y) coordinate pair.

		For a closed path, the initial moveTo point is defined as
		the last point of the last segment.

		The 'points' list of "move" and "line" segments always contains
		exactly one point tuple.
		"""
		raise NotImplementedError

	def endPath(self):
		assert self.currentPath is not None
		points = self.currentPath
		self.currentPath = None
		if not points:
			return
		if len(points) == 1:
			# Not much more we can do than output a single move segment.
			pt, segmentType, smooth, name, kwargs = points[0]
			segments = [("move", [(pt, smooth, name, kwargs)])]
			self._flushContour(segments)
			return
		segments = []
		if points[0][1] == "move":
			# It's an open contour, insert a "move" segment for the first
			# point and remove that first point from the point list.
			pt, segmentType, smooth, name, kwargs = points[0]
			segments.append(("move", [(pt, smooth, name, kwargs)]))
			points.pop(0)
		else:
			# It's a closed contour. Locate the first on-curve point, and
			# rotate the point list so that it _ends_ with an on-curve
			# point.
			firstOnCurve = None
			for i in range(len(points)):
				segmentType = points[i][1]
				if segmentType is not None:
					firstOnCurve = i
					break
			if firstOnCurve is None:
				# Special case for quadratics: a contour with no on-curve
				# points. Add a "None" point. (See also the Pen protocol's
				# qCurveTo() method and fontTools.pens.basePen.py.)
				points.append((None, "qcurve", None, None, None))
			else:
				points = points[firstOnCurve+1:] + points[:firstOnCurve+1]

		currentSegment = []
		for pt, segmentType, smooth, name, kwargs in points:
			currentSegment.append((pt, smooth, name, kwargs))
			if segmentType is None:
				continue
			segments.append((segmentType, currentSegment))
			currentSegment = []

		self._flushContour(segments)

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		self.currentPath.append((pt, segmentType, smooth, name, kwargs))


class PrintingPointPen(AbstractPointPen):
	def __init__(self):
		self.havePath = False
	def beginPath(self):
		self.havePath = True
		print "pen.beginPath()"
	def endPath(self):
		self.havePath = False
		print "pen.endPath()"
	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		assert self.havePath
		args = ["(%s, %s)" % (pt[0], pt[1])]
		if segmentType is not None:
			args.append("segmentType=%r" % segmentType)
		if smooth:
			args.append("smooth=True")
		if name is not None:
			args.append("name=%r" % name)
		if kwargs:
			args.append("**%s" % kwargs)
		print "pen.addPoint(%s)" % ", ".join(args)
	def addComponent(self, baseGlyphName, transformation):
		assert not self.havePath
		print "pen.addComponent(%r, %s)" % (baseGlyphName, tuple(transformation))


from fontTools.pens.basePen import AbstractPen

class PrintingSegmentPen(AbstractPen):
	def moveTo(self, pt):
		print "pen.moveTo(%s)" % (pt,)
	def lineTo(self, pt):
		print "pen.lineTo(%s)" % (pt,)
	def curveTo(self, *pts):
		print "pen.curveTo%s" % (pts,)
	def qCurveTo(self, *pts):
		print "pen.qCurveTo%s" % (pts,)
	def closePath(self):
		print "pen.closePath()"
	def endPath(self):
		print "pen.endPath()"
	def addComponent(self, baseGlyphName, transformation):
		print "pen.addComponent(%r, %s)" % (baseGlyphName, tuple(transformation))


class SegmentPrintingPointPen(BasePointToSegmentPen):
	def _flushContour(self, segments):
		from pprint import pprint
		pprint(segments)


if __name__ == "__main__":
	p = SegmentPrintingPointPen()
	from robofab.test.test_pens import TestShapes
	TestShapes.onCurveLessQuadShape(p)
