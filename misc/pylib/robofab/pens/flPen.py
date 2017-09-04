"""Pens for creating glyphs in FontLab."""


__all__ = ["FLPen", "FLPointPen", "drawFLGlyphOntoPointPen"]


from FL import *

try:
	from fl_cmd import *
except ImportError:
	print "The fl_cmd module is not available here. flPen.py"

from robofab.tools.toolsFL import NewGlyph
from robofab.pens.pointPen import AbstractPointPen
from robofab.pens.adapterPens import SegmentToPointPen


def roundInt(x):
	return int(round(x))


class FLPen(SegmentToPointPen):

	def __init__(self, glyph):
		SegmentToPointPen.__init__(self, FLPointPen(glyph))


class FLPointPen(AbstractPointPen):

	def __init__(self, glyph):
		if hasattr(glyph, "isRobofab"):
			self.glyph = glyph.naked()
		else:
			self.glyph = glyph
		self.currentPath = None

	def beginPath(self):
		self.currentPath = []

	def endPath(self):
		# Love is... abstracting away FL's madness.
		path = self.currentPath
		self.currentPath = None
		glyph = self.glyph
		if len(path) == 1 and path[0][3] is not None:
			# Single point on the contour, it has a name. Make it an anchor.
			x, y = path[0][0]
			name = path[0][3]
			anchor = Anchor(name, roundInt(x), roundInt(y))
			glyph.anchors.append(anchor)
			return
		firstOnCurveIndex = None
		for i in range(len(path)):
			if path[i][1] is not None:
				firstOnCurveIndex = i
				break
		if firstOnCurveIndex is None:
			# TT special case: on-curve-less contour. FL doesn't support that,
			# so we insert an implied point at the end.
			x1, y1 = path[0][0]
			x2, y2 = path[-1][0]
			impliedPoint = 0.5 * (x1 + x2), 0.5 * (y1 + y2)
			path.append((impliedPoint, "qcurve", True, None))
			firstOnCurveIndex = 0
		path = path[firstOnCurveIndex + 1:] + path[:firstOnCurveIndex + 1]
		firstPoint, segmentType, smooth, name = path[-1]
		closed = True
		if segmentType == "move":
			path = path[:-1]
			closed = False
			# XXX The contour is not closed, but I can't figure out how to
			# create an open contour in FL. Creating one by hand shows type"0x8011"
			# for a move node in an open contour, but I'm not able to access
			# that flag.
		elif segmentType == "line":
			# The contour is closed and ends in a lineto, which is redundant
			# as it's implied by closepath.
			path = path[:-1]
		x, y = firstPoint
		node = Node(nMOVE, Point(roundInt(x), roundInt(y)))
		if smooth and closed:
			if segmentType == "line" or path[0][1] == "line":
				node.alignment = nFIXED
			else:
				node.alignment = nSMOOTH
		glyph.Insert(node, len(glyph))
		segment = []
		nPoints = len(path)
		for i in range(nPoints):
			pt, segmentType, smooth, name = path[i]
			segment.append(pt)
			if segmentType is None:
				continue
			if segmentType == "curve":
				if len(segment) < 2:
					segmentType = "line"
				elif len(segment) == 2:
					segmentType = "qcurve"
			if segmentType == "qcurve":
				for x, y in segment[:-1]:
					glyph.Insert(Node(nOFF, Point(roundInt(x), roundInt(y))), len(glyph))
				x, y = segment[-1]
				node = Node(nLINE, Point(roundInt(x), roundInt(y)))
				glyph.Insert(node, len(glyph))
			elif segmentType == "curve":
				if len(segment) == 3:
					cubicSegments = [segment]
				else:
					from fontTools.pens.basePen import decomposeSuperBezierSegment
					cubicSegments = decomposeSuperBezierSegment(segment)
				nSegments = len(cubicSegments)
				for i in range(nSegments):
					pt1, pt2, pt3 = cubicSegments[i]
					x, y = pt3
					node = Node(nCURVE, Point(roundInt(x), roundInt(y)))
					node.points[1].x, node.points[1].y = roundInt(pt1[0]), roundInt(pt1[1])
					node.points[2].x, node.points[2].y = roundInt(pt2[0]), roundInt(pt2[1])
					if i != nSegments - 1:
						node.alignment = nSMOOTH
					glyph.Insert(node, len(self.glyph))
			elif segmentType == "line":
				assert len(segment) == 1, segment
				x, y = segment[0]
				node = Node(nLINE, Point(roundInt(x), roundInt(y)))
				glyph.Insert(node, len(glyph))
			else:
				assert 0, "unsupported curve type (%s)" % segmentType
			if smooth:
				if i + 1 < nPoints or closed:
					# Can't use existing node, as you can't change node attributes
					# AFTER it's been appended to the glyph.
					node = glyph[-1]
					if segmentType == "line" or path[(i+1) % nPoints][1] == "line":
						# tangent
						node.alignment = nFIXED
					else:
						# curve
						node.alignment = nSMOOTH
			segment = []
		if closed:
			# we may have output a node too much
			node = glyph[-1]
			if node.type == nLINE and (node.x, node.y) == (roundInt(firstPoint[0]), roundInt(firstPoint[1])):
				glyph.DeleteNode(len(glyph) - 1)

	def addPoint(self, pt, segmentType=None, smooth=None, name=None, **kwargs):
		self.currentPath.append((pt, segmentType, smooth, name))

	def addComponent(self, baseName, transformation):
		assert self.currentPath is None
		# make base glyph if needed, Component() needs the index
		NewGlyph(self.glyph.parent, baseName, updateFont=False)
		baseIndex = self.glyph.parent.FindGlyph(baseName)
		if baseIndex == -1:
			raise KeyError, "couldn't find or make base glyph"
		xx, xy, yx, yy, dx, dy = transformation
		# XXX warn when xy or yx != 0
		new = Component(baseIndex, Point(dx, dy), Point(xx, yy))
		self.glyph.components.append(new)


def drawFLGlyphOntoPointPen(flGlyph, pen):
	"""Draw a FontLab glyph onto a PointPen."""
	for anchor in flGlyph.anchors:
		pen.beginPath()
		pen.addPoint((anchor.x, anchor.y), name=anchor.name)
		pen.endPath()
	for contour in _getContours(flGlyph):
		pen.beginPath()
		for pt, segmentType, smooth in contour:
			pen.addPoint(pt, segmentType=segmentType, smooth=smooth)
		pen.endPath()
	for baseGlyph, tranform in _getComponents(flGlyph):
		pen.addComponent(baseGlyph, tranform)
		


class FLPointContourPen(FLPointPen):
	"""Same as FLPointPen, except that it ignores components."""
	def addComponent(self, baseName, transformation):
		pass


NODE_TYPES = {nMOVE: "move", nLINE: "line", nCURVE: "curve",
             nOFF: None}

def _getContours(glyph):
	contours = []
	for i in range(len(glyph)):
		node = glyph[i]
		segmentType = NODE_TYPES[node.type]
		if segmentType == "move":
			contours.append([])
		for pt in node.points[1:]:
			contours[-1].append(((pt.x, pt.y), None, False))
		smooth = node.alignment != nSHARP
		contours[-1].append(((node.x, node.y), segmentType, smooth))

	for contour in contours:
		# filter out or change the move
		movePt, segmentType, smooth = contour[0]
		assert segmentType == "move"
		lastSegmentType = contour[-1][1]
		if movePt == contour[-1][0] and lastSegmentType == "curve":
			contour[0] = contour[-1]
			contour.pop()
		elif lastSegmentType is None:
			contour[0] = movePt, "qcurve", smooth
		else:
			assert lastSegmentType in ("line", "curve")
			contour[0] = movePt, "line", smooth

		# change "line" to "qcurve" if appropriate
		previousSegmentType = "ArbitraryValueOtherThanNone"
		for i in range(len(contour)):
			pt, segmentType, smooth = contour[i]
			if segmentType == "line" and previousSegmentType is None:
				contour[i] = pt, "qcurve", smooth
			previousSegmentType = segmentType

	return contours


def _simplifyValues(*values):
	"""Given a set of numbers, convert items to ints if they are
	integer float values, eg. 0.0, 1.0."""
	newValues = []
	for v in values:
		i = int(v)
		if v == i:
			v = i
		newValues.append(v)
	return newValues


def _getComponents(glyph):
	components = []
	for comp in glyph.components:
		baseName = glyph.parent[comp.index].name
		dx, dy = comp.delta.x, comp.delta.y
		sx, sy = comp.scale.x, comp.scale.y
		dx, dy, sx, sy = _simplifyValues(dx, dy, sx, sy)
		components.append((baseName, (sx, 0, 0, sy, dx, dy)))
	return components


def test():
	g = fl.glyph
	g.Clear()
	
	p = PLPen(g)
	p.moveTo((50, 50))
	p.lineTo((150,50))
	p.lineTo((170, 200), smooth=2)
	p.curveTo((173, 225), (150, 250), (120, 250), smooth=1)
	p.curveTo((85, 250), (50, 200), (50, 200))
	p.closePath()
	
	p.moveTo((300, 300))
	p.lineTo((400, 300))
	p.curveTo((450, 325), (450, 375), (400, 400))
	p.qCurveTo((400, 500), (350, 550), (300, 500), (300, 400))
	p.closePath()
	p.setWidth(600)
	p.setNote("Hello, this is a note")
	p.addAnchor("top", (250, 600))
	
	fl.UpdateGlyph(-1)
	fl.UpdateFont(-1)


if __name__ == "__main__":
	test()
