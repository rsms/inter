"""A couple of point pens to filter contours in various ways."""

from fontTools.pens.basePen import AbstractPen, BasePen

from robofab.pens.pointPen import AbstractPointPen
from robofab.objects.objectsRF import RGlyph as _RGlyph
from robofab.objects.objectsBase import _interpolatePt

import math

#
#	 threshold filtering
#

def distance(pt1, pt2):
	return math.hypot(pt1[0]-pt2[0], pt1[1]-pt2[1])

class ThresholdPointPen(AbstractPointPen):
	
	"""
		Rewrite of the ThresholdPen as a PointPen
		so that we can preserve named points and other arguments.
		This pen will add components from the original glyph, but
		but it won't filter those components.
		
		"move", "line", "curve" or "qcurve"
	
	"""
	def __init__(self, otherPointPen, threshold=10):
		self.threshold = threshold
		self._lastPt = None
		self._offCurveBuffer = []
		self.otherPointPen = otherPointPen
		
	def beginPath(self):
		"""Start a new sub path."""
		self.otherPointPen.beginPath()
		self._lastPt = None

	def endPath(self):
		"""End the current sub path."""
		self.otherPointPen.endPath()

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		"""Add a point to the current sub path."""
		if segmentType in ['curve', 'qcurve']:
			# it's an offcurve, let's buffer them until we get another oncurve
			# and we know what to do with them
			self._offCurveBuffer.append((pt, segmentType, smooth, name, kwargs))
			return
		
		elif segmentType == "move":
			# start of an open contour
			self.otherPointPen.addPoint(pt, segmentType, smooth, name)	# how to add kwargs?
			self._lastPt = pt
			self._offCurveBuffer = []

		elif segmentType == "line":
			if self._lastPt is None:
				self.otherPointPen.addPoint(pt, segmentType, smooth, name)	# how to add kwargs?
				self._lastPt = pt
			elif distance(pt, self._lastPt) >= self.threshold:
				# we're oncurve and far enough from the last oncurve
				if self._offCurveBuffer:
					# empty any buffered offcurves
					for buf_pt, buf_segmentType, buf_smooth, buf_name, buf_kwargs in self._offCurveBuffer:
						self.otherPointPen.addPoint(buf_pt, buf_segmentType, buf_smooth, buf_name)	# how to add kwargs?
					self._offCurveBuffer = []
				# finally add the oncurve.
				self.otherPointPen.addPoint(pt, segmentType, smooth, name)	# how to add kwargs?
				self._lastPt = pt
			else:
				# we're too short, so we're not going to make it.
				# we need to clear out the offcurve buffer. 
				self._offCurveBuffer = []

	def addComponent(self, baseGlyphName, transformation):
		"""Add a sub glyph. Note: this way components are not filtered."""
		self.otherPointPen.addComponent(baseGlyphName, transformation)


class ThresholdPen(AbstractPen):

	"""Removes segments shorter in length than the threshold value."""

	def __init__(self, otherPen, threshold=10):
		self.threshold = threshold
		self._lastPt = None
		self.otherPen = otherPen

	def moveTo(self, pt):
		self._lastPt = pt
		self.otherPen.moveTo(pt)
	
	def lineTo(self, pt, smooth=False):
		if self.threshold <= distance(pt, self._lastPt):
			self.otherPen.lineTo(pt)
			self._lastPt = pt
		
	def curveTo(self, pt1, pt2, pt3):
		if self.threshold <= distance(pt3, self._lastPt):
			self.otherPen.curveTo(pt1, pt2, pt3)
			self._lastPt = pt3

	def qCurveTo(self, *points):
		if self.threshold <= distance(points[-1], self._lastPt):
			self.otherPen.qCurveTo(*points)
			self._lastPt = points[-1]
		
	def closePath(self):
		self.otherPen.closePath()
	
	def endPath(self):
		self.otherPen.endPath()
		
	def addComponent(self, glyphName, transformation):
		self.otherPen.addComponent(glyphName, transformation)


def thresholdGlyph(aGlyph, threshold=10):
	""" Convenience function that handles the filtering. """
	from robofab.pens.adapterPens import PointToSegmentPen
	new = _RGlyph()
	filterpen = ThresholdPen(new.getPen(), threshold)
	wrappedPen = PointToSegmentPen(filterpen)
	aGlyph.drawPoints(wrappedPen)
	aGlyph.clear()
	aGlyph.appendGlyph(new)
	aGlyph.update()
	return aGlyph

def thresholdGlyphPointPen(aGlyph, threshold=10):
	""" Same a thresholdGlyph, but using the ThresholdPointPen, which should respect anchors."""
	from robofab.pens.adapterPens import PointToSegmentPen
	new = _RGlyph()
	wrappedPen = new.getPointPen()
	filterpen = ThresholdPointPen(wrappedPen, threshold)
	aGlyph.drawPoints(filterpen)
	aGlyph.clear()
	new.drawPoints(aGlyph.getPointPen())
	aGlyph.update()
	return aGlyph

	
#
# Curve flattening
#

def _estimateCubicCurveLength(pt0, pt1, pt2, pt3, precision=10):
	"""Estimate the length of this curve by iterating
	through it and averaging the length of the flat bits.
	"""
	points = []
	length = 0
	step = 1.0/precision
	factors = range(0, precision+1)
	for i in factors:
		points.append(_getCubicPoint(i*step, pt0, pt1, pt2, pt3))
	for i in range(len(points)-1):
		pta = points[i]
		ptb = points[i+1]
		length += distance(pta, ptb)
	return length

def _mid((x0, y0), (x1, y1)):
	"""(Point, Point) -> Point\nReturn the point that lies in between the two input points."""
	return 0.5 * (x0 + x1), 0.5 * (y0 + y1)

def _getCubicPoint(t, pt0, pt1, pt2, pt3):
	if t == 0:
		return pt0
	if t == 1:
		return pt3
	if t == 0.5:
		a = _mid(pt0, pt1)
		b = _mid(pt1, pt2)
		c = _mid(pt2, pt3)
		d = _mid(a, b)
		e = _mid(b, c)
		return _mid(d, e)
	else:
		cx = (pt1[0] - pt0[0]) * 3
		cy = (pt1[1] - pt0[1]) * 3
		bx = (pt2[0] - pt1[0]) * 3 - cx
		by = (pt2[1] - pt1[1]) * 3 - cy
		ax = pt3[0] - pt0[0] - cx - bx
		ay = pt3[1] - pt0[1] - cy - by
		t3 = t ** 3
		t2 = t * t
		x = ax * t3 + bx * t2 + cx * t + pt0[0]
		y = ay * t3 + by * t2 + cy * t + pt0[1]
		return x, y


class FlattenPen(BasePen):

	"""Process the contours into a series of straight lines by flattening the curves.
	"""

	def __init__(self, otherPen, approximateSegmentLength=5, segmentLines=False, filterDoubles=True):
		self.approximateSegmentLength = approximateSegmentLength
		BasePen.__init__(self, {})
		self.otherPen = otherPen
		self.currentPt = None
		self.firstPt = None
		self.segmentLines = segmentLines
		self.filterDoubles = filterDoubles

	def _moveTo(self, pt):
		self.otherPen.moveTo(pt)
		self.currentPt = pt
		self.firstPt = pt

	def _lineTo(self, pt):
		if self.filterDoubles:
			if pt == self.currentPt:
				return
		if not self.segmentLines:
			self.otherPen.lineTo(pt)
			self.currentPt = pt
			return
		d = distance(self.currentPt, pt)
		maxSteps = int(round(d / self.approximateSegmentLength))
		if maxSteps < 1:
			self.otherPen.lineTo(pt)
			self.currentPt = pt
			return
		step = 1.0/maxSteps
		factors = range(0, maxSteps+1)
		for i in factors[1:]:
			self.otherPen.lineTo(_interpolatePt(self.currentPt, pt, i*step))
		self.currentPt = pt

	def _curveToOne(self, pt1, pt2, pt3):
		est = _estimateCubicCurveLength(self.currentPt, pt1, pt2, pt3)/self.approximateSegmentLength
		maxSteps = int(round(est))
		falseCurve = (pt1==self.currentPt) and (pt2==pt3)
		if maxSteps < 1 or falseCurve:
			self.otherPen.lineTo(pt3)
			self.currentPt = pt3
			return
		step = 1.0/maxSteps
		factors = range(0, maxSteps+1)
		for i in factors[1:]:
			pt = _getCubicPoint(i*step, self.currentPt, pt1, pt2, pt3)
			self.otherPen.lineTo(pt)
		self.currentPt = pt3
		
	def _closePath(self):
		self.lineTo(self.firstPt)
		self.otherPen.closePath()
		self.currentPt = None
	
	def _endPath(self):
		self.otherPen.endPath()
		self.currentPt = None
		
	def addComponent(self, glyphName, transformation):
		self.otherPen.addComponent(glyphName, transformation)
		

def flattenGlyph(aGlyph, threshold=10, segmentLines=True):

	"""Replace curves with series of straight l ines."""

	from robofab.pens.adapterPens import PointToSegmentPen
	if len(aGlyph.contours) == 0:
		return
	new = _RGlyph()
	writerPen = new.getPen()
	filterpen = FlattenPen(writerPen, threshold, segmentLines)
	wrappedPen = PointToSegmentPen(filterpen)
	aGlyph.drawPoints(wrappedPen)
	aGlyph.clear()
	aGlyph.appendGlyph(new)
	aGlyph.update()
	return aGlyph


def spikeGlyph(aGlyph, segmentLength=20, spikeLength=40, patternFunc=None):
	
	"""Add narly spikes or dents to the glyph.
	patternFunc is an optional function which recalculates the offset."""

	from math import atan2, sin, cos, pi
	
	new = _RGlyph()
	new.appendGlyph(aGlyph)
	new.width = aGlyph.width
	
	if len(new.contours) == 0:
		return
	flattenGlyph(new, segmentLength, segmentLines=True)
	for contour in new:
		l = len(contour.points)
		lastAngle = None
		for i in range(0, len(contour.points), 2):
			prev = contour.points[i-1]
			cur = contour.points[i]
			next = contour.points[(i+1)%l]
			angle = atan2(prev.x - next.x, prev.y - next.y)
			lastAngle = angle
			if patternFunc is not None:
				thisSpikeLength = patternFunc(spikeLength)
			else:
				thisSpikeLength = spikeLength
			cur.x -= sin(angle+.5*pi)*thisSpikeLength
			cur.y -= cos(angle+.5*pi)*thisSpikeLength
			new.update()
	aGlyph.clear()
	aGlyph.appendGlyph(new)
	aGlyph.update()
	return aGlyph


def halftoneGlyph(aGlyph, invert=False):
	
	"""Convert the glyph into some sort of halftoning pattern.
	Measure a bunch of inside/outside points to simulate grayscale levels.
	Slow.
	"""
	print 'halftoneGlyph is running...'
	grid = {}
	drawing = {}
	dataDistance = 10
	scan = 2
	preload = 0
	cellDistance = dataDistance * 5
	overshoot = dataDistance * 2
	(xMin, yMin, xMax, yMax) = aGlyph.box
	for x in range(xMin-overshoot, xMax+overshoot, dataDistance):
		print 'scanning..', x
		for y in range(yMin-overshoot, yMax+overshoot, dataDistance):
			if aGlyph.pointInside((x, y)):
				grid[(x, y)] = True
			else:
				grid[(x, y)] = False
			#print 'gathering data', x, y, grid[(x, y)]
	print 'analyzing..'
	for x in range(xMin-overshoot, xMax+overshoot, cellDistance):
		for y in range(yMin-overshoot, yMax+overshoot, cellDistance):
			total = preload
			for scanx in range(-scan, scan):
				for scany in range(-scan, scan):
					if grid.get((x+scanx*dataDistance, y+scany*dataDistance)):
						total += 1
			if invert:
				drawing[(x, y)] = 2*scan**2 - float(total)
			else:
				drawing[(x, y)] = float(total)
	aGlyph.clear()
	print drawing
	for (x,y) in drawing.keys():
		size = drawing[(x,y)] / float(2*scan**2) * 5
		pen = aGlyph.getPen()
		pen.moveTo((x-size, y-size))
		pen.lineTo((x+size, y-size))
		pen.lineTo((x+size, y+size))
		pen.lineTo((x-size, y+size))
		pen.lineTo((x-size, y-size))
		pen.closePath()
		aGlyph.update()


if __name__ == "__main__":
	from robofab.pens.pointPen import PrintingPointPen
	pp = PrintingPointPen()
	#pp.beginPath()
	#pp.addPoint((100, 100))
	#pp.endPath()

	tpp = ThresholdPointPen(pp, threshold=20)
	tpp.beginPath()
	#segmentType=None, smooth=False, name=None
	tpp.addPoint((100, 100), segmentType="line", smooth=True)
	# section that should be too small
	tpp.addPoint((100, 102), segmentType="line", smooth=True)
	tpp.addPoint((200, 200), segmentType="line", smooth=True)
	# curve section with final point that's far enough, but with offcurves that are under the threshold
	tpp.addPoint((200, 205), segmentType="curve", smooth=True)
	tpp.addPoint((300, 295), segmentType="curve", smooth=True)
	tpp.addPoint((300, 300), segmentType="line", smooth=True)
	# curve section with final point that is not far enough
	tpp.addPoint((550, 350), segmentType="curve", smooth=True)
	tpp.addPoint((360, 760), segmentType="curve", smooth=True)
	tpp.addPoint((310, 310), segmentType="line", smooth=True)

	tpp.addPoint((400, 400), segmentType="line", smooth=True)
	tpp.addPoint((100, 100), segmentType="line", smooth=True)
	tpp.endPath()

	# couple of single points with names
	tpp.beginPath()
	tpp.addPoint((500, 500), segmentType="move", smooth=True, name="named point")
	tpp.addPoint((600, 500), segmentType="move", smooth=True, name="named point")
	tpp.addPoint((601, 501), segmentType="move", smooth=True, name="named point")
	tpp.endPath()

	# open path
	tpp.beginPath()
	tpp.addPoint((500, 500), segmentType="move", smooth=True)
	tpp.addPoint((501, 500), segmentType="line", smooth=True)
	tpp.addPoint((101, 500), segmentType="line", smooth=True)
	tpp.addPoint((101, 100), segmentType="line", smooth=True)
	tpp.addPoint((498, 498), segmentType="line", smooth=True)
	tpp.endPath()
	