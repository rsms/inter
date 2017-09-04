import math
from fontTools.pens.basePen import AbstractPen
from robofab.pens.pointPen import AbstractPointPen, BasePointToSegmentPen


class FabToFontToolsPenAdapter:

	"""Class that covers up the subtle differences between RoboFab
	Pens and FontTools Pens. 'Fab should eventually move to FontTools
	Pens, this class may help to make the transition smoother.
	"""

	# XXX The change to FontTools pens has almost been completed. Any
	# usage of this class should be highly suspect.

	def __init__(self, fontToolsPen):
		self.fontToolsPen = fontToolsPen

	def moveTo(self, pt, **kargs):
		self.fontToolsPen.moveTo(pt)

	def lineTo(self, pt, **kargs):
		self.fontToolsPen.lineTo(pt)

	def curveTo(self, *pts, **kargs):
		self.fontToolsPen.curveTo(*pts)

	def qCurveTo(self, *pts, **kargs):
		self.fontToolsPen.qCurveTo(*pts)

	def closePath(self):
		self.fontToolsPen.closePath()

	def endPath(self):
		self.fontToolsPen.endPath()

	def addComponent(self, glyphName, offset=(0, 0), scale=(1, 1)):
		self.fontToolsPen.addComponent(glyphName,
				(scale[0], 0, 0, scale[1], offset[0], offset[1]))

	def setWidth(self, width):
		self.width = width

	def setNote(self, note):
		pass

	def addAnchor(self, name, pt):
		self.fontToolsPen.moveTo(pt)
		self.fontToolsPen.endPath()

	def doneDrawing(self):
		pass


class PointToSegmentPen(BasePointToSegmentPen):

	"""Adapter class that converts the PointPen protocol to the
	(Segment)Pen protocol.
	"""

	def __init__(self, segmentPen, outputImpliedClosingLine=False):
		BasePointToSegmentPen.__init__(self)
		self.pen = segmentPen
		self.outputImpliedClosingLine = outputImpliedClosingLine

	def _flushContour(self, segments):
		assert len(segments) >= 1
		pen = self.pen
		if segments[0][0] == "move":
			# It's an open path.
			closed = False
			points = segments[0][1]
			assert len(points) == 1
			movePt, smooth, name, kwargs = points[0]
			del segments[0]
		else:
			# It's a closed path, do a moveTo to the last
			# point of the last segment.
			closed = True
			segmentType, points = segments[-1]
			movePt, smooth, name, kwargs = points[-1]
		if movePt is None:
			# quad special case: a contour with no on-curve points contains
			# one "qcurve" segment that ends with a point that's None. We
			# must not output a moveTo() in that case.
			pass
		else:
			pen.moveTo(movePt)
		outputImpliedClosingLine = self.outputImpliedClosingLine
		nSegments = len(segments)
		for i in range(nSegments):
			segmentType, points = segments[i]
			points = [pt for pt, smooth, name, kwargs in points]
			if segmentType == "line":
				assert len(points) == 1
				pt = points[0]
				if i + 1 != nSegments or outputImpliedClosingLine or not closed:
					pen.lineTo(pt)
			elif segmentType == "curve":
				pen.curveTo(*points)
			elif segmentType == "qcurve":
				pen.qCurveTo(*points)
			else:
				assert 0, "illegal segmentType: %s" % segmentType
		if closed:
			pen.closePath()
		else:
			pen.endPath()

	def addComponent(self, glyphName, transform):
		self.pen.addComponent(glyphName, transform)


class SegmentToPointPen(AbstractPen):

	"""Adapter class that converts the (Segment)Pen protocol to the
	PointPen protocol.
	"""

	def __init__(self, pointPen, guessSmooth=True):
		if guessSmooth:
			self.pen = GuessSmoothPointPen(pointPen)
		else:
			self.pen = pointPen
		self.contour = None

	def _flushContour(self):
		pen = self.pen
		pen.beginPath()
		for pt, segmentType in self.contour:
			pen.addPoint(pt, segmentType=segmentType)
		pen.endPath()

	def moveTo(self, pt):
		self.contour = []
		self.contour.append((pt, "move"))

	def lineTo(self, pt):
		self.contour.append((pt, "line"))

	def curveTo(self, *pts):
		for pt in pts[:-1]:
			self.contour.append((pt, None))
		self.contour.append((pts[-1], "curve"))

	def qCurveTo(self, *pts):
		if pts[-1] is None:
			self.contour = []
		for pt in pts[:-1]:
			self.contour.append((pt, None))
		if pts[-1] is not None:
			self.contour.append((pts[-1], "qcurve"))

	def closePath(self):
		if len(self.contour) > 1 and self.contour[0][0] == self.contour[-1][0]:
			self.contour[0] = self.contour[-1]
			del self.contour[-1]
		else:
			# There's an implied line at the end, replace "move" with "line"
			# for the first point
			pt, tp = self.contour[0]
			if tp == "move":
				self.contour[0] = pt, "line"
		self._flushContour()
		self.contour = None

	def endPath(self):
		self._flushContour()
		self.contour = None

	def addComponent(self, glyphName, transform):
		assert self.contour is None
		self.pen.addComponent(glyphName, transform)


class TransformPointPen(AbstractPointPen):

	"""PointPen that transforms all coordinates, and passes them to another
	PointPen. It also transforms the transformation given to addComponent().
	"""

	def __init__(self, outPen, transformation):
		if not hasattr(transformation, "transformPoint"):
			from fontTools.misc.transform import Transform
			transformation = Transform(*transformation)
		self._transformation = transformation
		self._transformPoint = transformation.transformPoint
		self._outPen = outPen
		self._stack = []

	def beginPath(self):
		self._outPen.beginPath()

	def endPath(self):
		self._outPen.endPath()

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		pt = self._transformPoint(pt)
		self._outPen.addPoint(pt, segmentType, smooth, name, **kwargs)

	def addComponent(self, glyphName, transformation):
		transformation = self._transformation.transform(transformation)
		self._outPen.addComponent(glyphName, transformation)


class GuessSmoothPointPen(AbstractPointPen):

	"""Filtering PointPen that tries to determine whether an on-curve point
	should be "smooth", ie. that it's a "tangent" point or a "curve" point.
	"""

	def __init__(self, outPen):
		self._outPen = outPen
		self._points = None

	def _flushContour(self):
		points = self._points
		nPoints = len(points)
		if not nPoints:
			return
		if points[0][1] == "move":
			# Open path.
			indices = range(1, nPoints - 1)
		elif nPoints > 1:
			# Closed path. To avoid having to mod the contour index, we
			# simply abuse Python's negative index feature, and start at -1
			indices = range(-1, nPoints - 1)
		else:
			# closed path containing 1 point (!), ignore.
			indices = []
		for i in indices:
			pt, segmentType, dummy, name, kwargs = points[i]
			if segmentType is None:
				continue
			prev = i - 1
			next = i + 1
			if points[prev][1] is not None and points[next][1] is not None:
				continue
			# At least one of our neighbors is an off-curve point
			pt = points[i][0]
			prevPt = points[prev][0]
			nextPt = points[next][0]
			if pt != prevPt and pt != nextPt:
				dx1, dy1 = pt[0] - prevPt[0], pt[1] - prevPt[1]
				dx2, dy2 = nextPt[0] - pt[0], nextPt[1] - pt[1]
				a1 = math.atan2(dx1, dy1)
				a2 = math.atan2(dx2, dy2)
				if abs(a1 - a2) < 0.05:
					points[i] = pt, segmentType, True, name, kwargs

		for pt, segmentType, smooth, name, kwargs in points:
			self._outPen.addPoint(pt, segmentType, smooth, name, **kwargs)

	def beginPath(self):
		assert self._points is None
		self._points = []
		self._outPen.beginPath()

	def endPath(self):
		self._flushContour()
		self._outPen.endPath()
		self._points = None

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		self._points.append((pt, segmentType, False, name, kwargs))

	def addComponent(self, glyphName, transformation):
		assert self._points is None
		self._outPen.addComponent(glyphName, transformation)


if __name__ == "__main__":
	from fontTools.pens.basePen import _TestPen as PSPen
	from robofab.pens.pointPen import PrintingPointPen
	segmentPen = PSPen(None)
#	pen = PointToSegmentPen(SegmentToPointPen(PointToSegmentPen(PSPen(None))))
	pen = PointToSegmentPen(SegmentToPointPen(PrintingPointPen()))
#	pen = PrintingPointPen()
	pen = PointToSegmentPen(PSPen(None), outputImpliedClosingLine=False)
#	pen.beginPath()
#	pen.addPoint((50, 50), name="an anchor")
#	pen.endPath()
	pen.beginPath()
	pen.addPoint((-100, 0), segmentType="line")
	pen.addPoint((0, 0), segmentType="line")
	pen.addPoint((0, 100), segmentType="line")
	pen.addPoint((30, 200))
	pen.addPoint((50, 100), name="superbezcontrolpoint!")
	pen.addPoint((70, 200))
	pen.addPoint((100, 100), segmentType="curve")
	pen.addPoint((100, 0), segmentType="line")
	pen.endPath()
#	pen.addComponent("a", (1, 0, 0, 1, 100, 200))
