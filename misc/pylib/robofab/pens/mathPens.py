"""Some pens that are needed during glyph math"""


from robofab.pens.pointPen import BasePointToSegmentPen, AbstractPointPen


class GetMathDataPointPen(AbstractPointPen):
	
	"""
	Point pen that converts all "line" segments into
	curve segments containing two off curve points.
	"""
	
	def __init__(self):
		self.contours = []
		self.components = []
		self.anchors = []
		self._points = []
	
	def _flushContour(self):
		points = self._points
		if len(points) == 1:
			segmentType, pt, smooth, name = points[0]
			self.anchors.append((pt, name))
		else:
			self.contours.append([])
			prevOnCurve = None
			offCurves = []
			# deal with the first point
			segmentType, pt, smooth, name = points[0]
			# if it is an offcurve, add it to the offcurve list
			if segmentType is None:
				offCurves.append((segmentType, pt, smooth, name))
			# if it is a line, change the type to curve and add it to the contour
			# create offcurves corresponding with the last oncurve and
			# this point and add them to the points list
			elif segmentType == "line":
				prevOnCurve = pt
				self.contours[-1].append(("curve", pt, False, name))
				lastPoint = points[-1][1]
				points.append((None, lastPoint, False, None))
				points.append((None, pt, False, None))
			# a move, curve or qcurve. simple append the data.
			else:
				self.contours[-1].append((segmentType, pt, smooth, name))
				prevOnCurve = pt
			# now go through the rest of the points
			for segmentType, pt, smooth, name in points[1:]:
				# store the off curves
				if segmentType is None:
					offCurves.append((segmentType, pt, smooth, name))
					continue
				# make off curve corresponding the the previous
				# on curve an dthis point
				if segmentType == "line":
					segmentType = "curve"
					offCurves.append((None, prevOnCurve, False, None))
					offCurves.append((None, pt, False, None))
				# add the offcurves to the contour
				for offCurve in offCurves:
					self.contours[-1].append(offCurve)
				# add the oncurve to the contour
				self.contours[-1].append((segmentType, pt, smooth, name))
				# reset the stored data
				prevOnCurve = pt
				offCurves = []
			# catch offcurves that belong to the first
			if len(offCurves) != 0:
				self.contours[-1].extend(offCurves)
	
	def beginPath(self):
		self._points = []
	
	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		self._points.append((segmentType, pt, smooth, name))
	
	def endPath(self):
		self._flushContour()
	
	def addComponent(self, baseGlyphName, transformation):
		self.components.append((baseGlyphName, transformation))
	
	def getData(self):
		return {
			'contours':list(self.contours),
			'components':list(self.components),
			'anchors':list(self.anchors)
			}


class CurveSegmentFilterPointPen(AbstractPointPen):
	
	"""
	Point pen that turns curve segments that contain
	unnecessary anchor points into line segments.
	"""
	# XXX it would be great if this also checked to see if the
	# off curves are on the segment and therefre unneeded
	
	def __init__(self, anotherPointPen):
		self._pen = anotherPointPen
		self._points = []
	
	def _flushContour(self):
		points = self._points
		# an anchor
		if len(points) == 1:
			pt, segmentType, smooth, name = points[0]
			self._pen.addPoint(pt, segmentType, smooth, name)
		else:
			prevOnCurve = None
			offCurves = []
			
			pointsToDraw = []
			
			# deal with the first point
			pt, segmentType, smooth, name = points[0]
			# if it is an offcurve, add it to the offcurve list
			if segmentType is None:
				offCurves.append((pt, segmentType, smooth, name))
			else:
				# potential redundancy
				if segmentType == "curve":
					# gather preceding off curves
					testOffCurves = []
					lastPoint = None
					for i in xrange(len(points)):
						i = -i - 1
						testPoint = points[i]
						testSegmentType = testPoint[1]
						if testSegmentType is not None:
							lastPoint = testPoint[0]
							break
						testOffCurves.append(testPoint[0])
					# if two offcurves exist we can test for redundancy
					if len(testOffCurves) == 2:
						if testOffCurves[1] == lastPoint and testOffCurves[0] == pt:
							segmentType = "line"
							# remove the last two points
							points = points[:-2]
				# add the point to the contour
				pointsToDraw.append((pt, segmentType, smooth, name))
				prevOnCurve = pt
			for pt, segmentType, smooth, name in points[1:]:
				# store offcurves
				if segmentType is None:
					offCurves.append((pt, segmentType, smooth, name))
					continue
				# curves are a potential redundancy
				elif segmentType == "curve":
					if len(offCurves) == 2:
						# test for redundancy
						if offCurves[0][0] == prevOnCurve and offCurves[1][0] == pt:
							offCurves = []
							segmentType = "line"
				# add all offcurves
				for offCurve in offCurves:
					pointsToDraw.append(offCurve)
				# add the on curve
				pointsToDraw.append((pt, segmentType, smooth, name))
				# reset the stored data
				prevOnCurve = pt
				offCurves = []
			# catch any remaining offcurves
			if len(offCurves) != 0:
				for offCurve in offCurves:
					pointsToDraw.append(offCurve)
			# draw to the pen
			for pt, segmentType, smooth, name in pointsToDraw:
				self._pen.addPoint(pt, segmentType, smooth, name)
	
	def beginPath(self):
		self._points = []
		self._pen.beginPath()
	
	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		self._points.append((pt, segmentType, smooth, name))
	
	def endPath(self):
		self._flushContour()
		self._pen.endPath()
	
	def addComponent(self, baseGlyphName, transformation):
		self._pen.addComponent(baseGlyphName, transformation)

