"""Pens for creating UFO glyphs."""

from robofab.objects.objectsBase import MOVE, LINE, CORNER, CURVE, QCURVE, OFFCURVE
from robofab.objects.objectsRF import RContour, RSegment, RPoint
from robofab.pens.pointPen import BasePointToSegmentPen
from robofab.pens.adapterPens import SegmentToPointPen


class RFUFOPen(SegmentToPointPen):

	def __init__(self, glyph):
		SegmentToPointPen.__init__(self, RFUFOPointPen(glyph))


class RFUFOPointPen(BasePointToSegmentPen):
	
	"""Point pen for building objectsRF glyphs"""
	
	def __init__(self, glyph):
		BasePointToSegmentPen.__init__(self)
		self.glyph = glyph
	
	def _flushContour(self, segments):
		#
		# adapted from robofab.pens.adapterPens.PointToSegmentPen
		#
		assert len(segments) >= 1
		# if we only have one point and it has a name, we must have an anchor
		first = segments[0]
		segmentType, points = first
		pt, smooth, name, kwargs = points[0]
		if len(segments) == 1 and name != None:
			self.glyph.appendAnchor(name, pt)
			return
		# we must have a contour
		contour = RContour()
		contour.setParent(self.glyph)
		if segments[0][0] == "move":
			# It's an open path.
			closed = False
			points = segments[0][1]
			assert len(points) == 1
			movePt, smooth, name, kwargs = points[0]
			del segments[0]
		else:
			# It's a closed path, do a moveTo to the last
			# point of the last segment. only if it isn't a qcurve
			closed = True
			segmentType, points = segments[-1]
			movePt, smooth, name, kwargs = points[-1]
			## THIS IS STILL UNDECIDED!!!
			# since objectsRF currently follows the FL model of not
			# allowing open contours, remove the last segment
			# since it is being replaced by a move
			if segmentType == 'line':
				del segments[-1]
		# construct a move segment and apply it to the contour if we aren't dealing with a qcurve
		segment = RSegment()
		segment.setParent(contour)
		segment.smooth = smooth
		rPoint = RPoint(x=movePt[0], y=movePt[1], pointType=MOVE, name=name)
		rPoint.setParent(segment)
		segment.points = [rPoint]
		contour.segments.append(segment)
		# do the rest of the segments
		for segmentType, points in segments:
			points = [(pt, name) for pt, smooth, name, kwargs in points]
			if segmentType == "line":
				assert len(points) == 1
				sType = LINE
			elif segmentType == "curve":
				sType = CURVE
			elif segmentType == "qcurve":
				sType = QCURVE
			else:
				assert 0, "illegal segmentType: %s" % segmentType
			segment = RSegment()
			segment.setParent(contour)
			segment.smooth = smooth
			rPoints = []
			# handle the offCurves
			for point in points[:-1]:
				point, name = point
				rPoint = RPoint(x=point[0], y=point[1], pointType=OFFCURVE, name=name)
				rPoint.setParent(segment)
				rPoints.append(rPoint)
			# now the onCurve
			point, name = points[-1]
			rPoint = RPoint(x=point[0], y=point[1], pointType=sType, name=name)
			rPoint.setParent(segment)
			rPoints.append(rPoint)
			# apply them to the segment
			segment.points = rPoints
			contour.segments.append(segment)
		if contour.segments[-1].type == "curve":
			contour.segments[-1].points[-1].name = None
		self.glyph.contours.append(contour)
		
	def addComponent(self, glyphName, transform):
		xx, xy, yx, yy, dx, dy = transform
		self.glyph.appendComponent(baseGlyph=glyphName, offset=(dx, dy), scale=(xx, yy))


