"""A couple of point pens which return the glyph as a list of basic values."""


from robofab.pens.pointPen import AbstractPointPen


class DigestPointPen(AbstractPointPen):

	"""Calculate a digest of all points
		AND coordinates
		AND components
	in a glyph.
	"""

	def __init__(self, ignoreSmoothAndName=False):
		self._data = []
		self.ignoreSmoothAndName = ignoreSmoothAndName

	def beginPath(self):
		self._data.append('beginPath')

	def endPath(self):
		self._data.append('endPath')

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		if self.ignoreSmoothAndName:
			self._data.append((pt, segmentType))
		else:
			self._data.append((pt, segmentType, smooth, name))

	def addComponent(self, baseGlyphName, transformation):
		t = []
		for v in transformation:
			if int(v) == v:
				t.append(int(v))
			else:
				t.append(v)
		self._data.append((baseGlyphName, tuple(t)))

	def getDigest(self):
		return tuple(self._data)
	
	def getDigestPointsOnly(self, needSort=True):
		""" Return a tuple with all coordinates of all points, 
			but without smooth info or drawing instructions.
			For instance if you want to compare 2 glyphs in shape,
			but not interpolatability.
			"""
		points = []
		from types import TupleType
		for item in self._data:
			if type(item) == TupleType:
				points.append(item[0])
		if needSort:
			points.sort()
		return tuple(points)


class DigestPointStructurePen(DigestPointPen):

	"""Calculate a digest of the structure of the glyph
		NOT coordinates
		NOT values.
	"""

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		self._data.append(segmentType)

	def addComponent(self, baseGlyphName, transformation):
		self._data.append(baseGlyphName)

if __name__ == "__main__":
	"""
	
	beginPath
	((112, 651), 'line', False, None)
	((112, 55), 'line', False, None)
	((218, 55), 'line', False, None)
	((218, 651), 'line', False, None)
	endPath
	
	"""
	# a test
	
	from robofab.objects.objectsRF import RGlyph
	
	g = RGlyph()
	p = g.getPen()
	p.moveTo((112, 651))
	p.lineTo((112, 55))
	p.lineTo((218, 55))
	p.lineTo((218, 651))
	p.closePath()
	
	print g, len(g)
	
	digestPen = DigestPointPen()
	g.drawPoints(digestPen)

	print
	print "getDigest", digestPen.getDigest()
	
	print
	print "getDigestPointsOnly", digestPen.getDigestPointsOnly()
	
	