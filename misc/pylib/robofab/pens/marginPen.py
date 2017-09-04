from fontTools.pens.basePen import AbstractPen, BasePen
from robofab.misc.bezierTools import splitLine, splitCubic


from sets import Set

class MarginPen(BasePen):

	"""
		Pen to calculate the margins at a given value.
			When isHorizontal is True, the margins at <value> are horizontal.
			When isHorizontal is False, the margins at <value> are vertical.
		
		When a glyphset or font is given, MarginPen will also calculate for glyphs with components.

		pen.getMargins() returns the minimum and maximum intersections of the glyph.
		pen.getContourMargins() returns the minimum and maximum intersections for each contour.
		
		
		Possible optimisation:
		Initialise the pen object with a list of points we want to measure,
		then draw the glyph once, but do the splitLine() math for all measure points.
		
	"""

	def __init__(self, glyphSet, value, isHorizontal=True):
		BasePen.__init__(self, glyphSet)
		self.value = value
		self.hits = {}
		self.filterDoubles = True
		self.contourIndex = None
		self.startPt = None
		self.isHorizontal = isHorizontal
		
	def _moveTo(self, pt):
		self.currentPt = pt
		self.startPt = pt
		if self.contourIndex is None:
			self.contourIndex = 0
		else:
			self.contourIndex += 1

	def _lineTo(self, pt):
		if self.filterDoubles:
			if pt == self.currentPt:
				return
		hits = splitLine(self.currentPt, pt, self.value, self.isHorizontal)
		if len(hits)>1:
			# result will be 2 tuples of 2 coordinates
			# first two points: start to intersect
			# second two points: intersect to end
			# so, second point in first tuple is the intersect
			# then, the first coordinate of that point is the x.
			if not self.contourIndex in self.hits:
				self.hits[self.contourIndex] = []
			if self.isHorizontal:
				self.hits[self.contourIndex].append(round(hits[0][-1][0], 4))
			else:
				self.hits[self.contourIndex].append(round(hits[0][-1][1], 4))
		if self.isHorizontal and pt[1] == self.value:
			# it could happen
			if not self.contourIndex in self.hits:
				self.hits[self.contourIndex] =	[]
			self.hits[self.contourIndex].append(pt[0])
		elif (not self.isHorizontal) and (pt[0] == self.value):
			# it could happen
			if not self.contourIndex in self.hits:
				self.hits[self.contourIndex] =	[]
			self.hits[self.contourIndex].append(pt[1])
		self.currentPt = pt

	def _curveToOne(self, pt1, pt2, pt3):
		hits = splitCubic(self.currentPt, pt1, pt2, pt3, self.value, self.isHorizontal)
		for i in range(len(hits)-1):
			# a number of intersections is possible. Just take the 
			# last point of each segment.
			if not self.contourIndex in self.hits:
				self.hits[self.contourIndex] = []
			if self.isHorizontal:
				self.hits[self.contourIndex].append(round(hits[i][-1][0], 4))
			else:
				self.hits[self.contourIndex].append(round(hits[i][-1][1], 4))
		if self.isHorizontal and pt3[1] == self.value:
			# it could happen
			if not self.contourIndex in self.hits:
				self.hits[self.contourIndex] = []
			self.hits[self.contourIndex].append(pt3[0])
		if (not self.isHorizontal) and (pt3[0] == self.value):
			# it could happen
			if not self.contourIndex in self.hits:
				self.hits[self.contourIndex] = []
			self.hits[self.contourIndex].append(pt3[1])
		self.currentPt = pt3
		
	def _closePath(self):
		if self.currentPt != self.startPt:
			self._lineTo(self.startPt)
		self.currentPt = self.startPt = None
	
	def _endPath(self):
		self.currentPt = None

	def addComponent(self, baseGlyph, transformation):
		from fontTools.pens.transformPen import TransformPen
		if self.glyphSet is None:
			return
		if baseGlyph in self.glyphSet:
			glyph = self.glyphSet[baseGlyph]
			if glyph is None:
				return
			tPen = TransformPen(self, transformation)
			glyph.draw(tPen)

	def getMargins(self):
		"""Get the horizontal margins for all contours combined, i.e. the whole glyph."""
		allHits = []
		for index, pts in self.hits.items():
			allHits.extend(pts)
		if allHits:
			return min(allHits), max(allHits)
		return None
		
	def getContourMargins(self):
		"""Get the horizontal margins for each contour."""
		allHits = {}
		for index, pts in self.hits.items():
			unique = list(Set(pts))
			unique.sort()
			allHits[index] = unique
		return allHits
		
	def getAll(self):
		"""Get all the slices."""
		allHits = []
		for index, pts in self.hits.items():
			allHits.extend(pts)
		unique = list(Set(allHits))
		unique = list(unique)
		unique.sort()
		return unique
		
		
if __name__ == "__main__":

	from robofab.world import CurrentGlyph, CurrentFont
	f = CurrentFont()
	g = CurrentGlyph()

	pt = (74, 216)

	pen = MarginPen(f, pt[1], isHorizontal=False)
	g.draw(pen) 
	print 'glyph Y margins', pen.getMargins()
	print pen.getContourMargins()

