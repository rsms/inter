"""PointPen for reversing the winding direction of contours."""


__all__ = ["ReverseContourPointPen"]


from robofab.pens.pointPen import AbstractPointPen


class ReverseContourPointPen(AbstractPointPen):

	"""This is a PointPen that passes outline data to another PointPen, but
	reversing the winding direction of all contours. Components are simply
	passed through unchanged.

	Closed contours are reversed in such a way that the first point remains
	the first point.
	"""

	def __init__(self, outputPointPen):
		self.pen = outputPointPen
		self.currentContour = None  # a place to store the points for the current sub path

	def _flushContour(self):
		pen = self.pen
		contour = self.currentContour
		if not contour:
			pen.beginPath()
			pen.endPath()
			return

		closed = contour[0][1] != "move"
		if not closed:
			lastSegmentType = "move"
		else:
			# Remove the first point and insert it at the end. When
			# the list of points gets reversed, this point will then
			# again be at the start. In other words, the following
			# will hold:
			#   for N in range(len(originalContour)):
			#       originalContour[N] == reversedContour[-N]
			contour.append(contour.pop(0))
			# Find the first on-curve point.
			firstOnCurve = None
			for i in range(len(contour)):
				if contour[i][1] is not None:
					firstOnCurve = i
					break
			if firstOnCurve is None:
				# There are no on-curve points, be basically have to
				# do nothing but contour.reverse().
				lastSegmentType = None
			else:
				lastSegmentType = contour[firstOnCurve][1]

		contour.reverse()
		if not closed:
			# Open paths must start with a move, so we simply dump
			# all off-curve points leading up to the first on-curve.
			while contour[0][1] is None:
				contour.pop(0)
		pen.beginPath()
		for pt, nextSegmentType, smooth, name in contour:
			if nextSegmentType is not None:
				segmentType = lastSegmentType
				lastSegmentType = nextSegmentType
			else:
				segmentType = None
			pen.addPoint(pt, segmentType=segmentType, smooth=smooth, name=name)
		pen.endPath()

	def beginPath(self):
		assert self.currentContour is None
		self.currentContour = []
		self.onCurve = []

	def endPath(self):
		assert self.currentContour is not None
		self._flushContour()
		self.currentContour = None

	def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
		self.currentContour.append((pt, segmentType, smooth, name))

	def addComponent(self, glyphName, transform):
		assert self.currentContour is None
		self.pen.addComponent(glyphName, transform)


if __name__ == "__main__":
	from robofab.pens.pointPen import PrintingPointPen
	pP = PrintingPointPen()
	rP = ReverseContourPointPen(pP)

	rP.beginPath()
	rP.addPoint((339, -8), "curve")
	rP.addPoint((502, -8))
	rP.addPoint((635, 65))
	rP.addPoint((635, 305), "curve")
	rP.addPoint((635, 545))
	rP.addPoint((504, 623))
	rP.addPoint((340, 623), "curve")
	rP.addPoint((177, 623))
	rP.addPoint((43, 545))
	rP.addPoint((43, 305), "curve")
	rP.addPoint((43, 65))
	rP.addPoint((176, -8))
	rP.endPath()

	rP.beginPath()
	rP.addPoint((100, 100), "move", smooth=False, name='a')
	rP.addPoint((150, 150))
	rP.addPoint((200, 200))
	rP.addPoint((250, 250), "curve", smooth=True, name='b')
	rP.addPoint((300, 300), "line", smooth=False, name='c')
	rP.addPoint((350, 350))
	rP.addPoint((400, 400))
	rP.addPoint((450, 450))
	rP.addPoint((500, 500), "curve", smooth=True, name='d')
	rP.addPoint((550, 550))
	rP.addPoint((600, 600))
	rP.addPoint((650, 650))
	rP.addPoint((700, 700))
	rP.addPoint((750, 750), "qcurve", smooth=False, name='e')
	rP.endPath()
