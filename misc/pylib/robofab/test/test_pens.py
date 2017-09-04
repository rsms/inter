"""This test suite test general Pen stuff, it should not contain
FontLab-specific code.
"""

import unittest

from robofab.pens.digestPen import DigestPointPen
from robofab.pens.adapterPens import SegmentToPointPen, PointToSegmentPen
from robofab.pens.adapterPens import GuessSmoothPointPen
from robofab.pens.reverseContourPointPen import ReverseContourPointPen
from robofab.test.testSupport import getDemoFontGlyphSetPath
from robofab.glifLib import GlyphSet


class TestShapes:

	# Collection of test shapes. It's probably better to add these as
	# glyphs to the demo font.

	def square(pen):
		# a simple square as a closed path (100, 100, 600, 600)
		pen.beginPath()
		pen.addPoint((100, 100), "line")
		pen.addPoint((100, 600), "line")
		pen.addPoint((600, 600), "line")
		pen.addPoint((600, 100), "line")
		pen.endPath()
	square = staticmethod(square)

	def onCurveLessQuadShape(pen):
		pen.beginPath()
		pen.addPoint((100, 100))
		pen.addPoint((100, 600))
		pen.addPoint((600, 600))
		pen.addPoint((600, 100))
		pen.endPath()
	onCurveLessQuadShape = staticmethod(onCurveLessQuadShape)

	def openPath(pen):
		# a simple square as a closed path (100, 100, 600, 600)
		pen.beginPath()
		pen.addPoint((100, 100), "move")
		pen.addPoint((100, 600), "line")
		pen.addPoint((600, 600), "line")
		pen.addPoint((600, 100), "line")
		pen.endPath()
	openPath = staticmethod(openPath)

	def circle(pen):
		pen.beginPath()
		pen.addPoint((0, 500), "curve")
		pen.addPoint((0, 800))
		pen.addPoint((200, 1000))
		pen.addPoint((500, 1000), "curve")
		pen.addPoint((800, 1000))
		pen.addPoint((1000, 800))
		pen.addPoint((1000, 500), "curve")
		pen.addPoint((1000, 200))
		pen.addPoint((800, 0))
		pen.addPoint((500, 0), "curve")
		pen.addPoint((200, 0))
		pen.addPoint((0, 200))
		pen.endPath()
	circle = staticmethod(circle)


class RoundTripTestCase(unittest.TestCase):

	def _doTest(self, shapeFunc, shapeName):
		pen = DigestPointPen(ignoreSmoothAndName=True)
		shapeFunc(pen)
		digest1 = pen.getDigest()

		digestPen = DigestPointPen(ignoreSmoothAndName=True)
		pen = PointToSegmentPen(SegmentToPointPen(digestPen))
		shapeFunc(pen)
		digest2 = digestPen.getDigest()
		self.assertEqual(digest1, digest2, "%r failed round tripping" % shapeName)

	def testShapes(self):
		for name in dir(TestShapes):
			if name[0] != "_":
				self._doTest(getattr(TestShapes, name), name)

	def testShapesFromGlyphSet(self):
		glyphSet = GlyphSet(getDemoFontGlyphSetPath())
		for name in glyphSet.keys():
			self._doTest(glyphSet[name].drawPoints, name)

	def testGuessSmoothPen(self):
		glyphSet = GlyphSet(getDemoFontGlyphSetPath())
		for name in glyphSet.keys():
			digestPen = DigestPointPen()
			glyphSet[name].drawPoints(digestPen)
			digest1 = digestPen.getDigest()
			digestPen = DigestPointPen()
			pen = GuessSmoothPointPen(digestPen)
			glyphSet[name].drawPoints(pen)
			digest2 = digestPen.getDigest()
			self.assertEqual(digest1, digest2)


class ReverseContourTestCase(unittest.TestCase):

	def testReverseContourClosedPath(self):
		digestPen = DigestPointPen()
		TestShapes.square(digestPen)
		d1 = digestPen.getDigest()
		digestPen = DigestPointPen()
		pen = ReverseContourPointPen(digestPen)
		pen.beginPath()
		pen.addPoint((100, 100), "line")
		pen.addPoint((600, 100), "line")
		pen.addPoint((600, 600), "line")
		pen.addPoint((100, 600), "line")
		pen.endPath()
		d2 = digestPen.getDigest()
		self.assertEqual(d1, d2)

	def testReverseContourOpenPath(self):
		digestPen = DigestPointPen()
		TestShapes.openPath(digestPen)
		d1 = digestPen.getDigest()
		digestPen = DigestPointPen()
		pen = ReverseContourPointPen(digestPen)
		pen.beginPath()
		pen.addPoint((600, 100), "move")
		pen.addPoint((600, 600), "line")
		pen.addPoint((100, 600), "line")
		pen.addPoint((100, 100), "line")
		pen.endPath()
		d2 = digestPen.getDigest()
		self.assertEqual(d1, d2)

	def testReversContourFromGlyphSet(self):
		glyphSet = GlyphSet(getDemoFontGlyphSetPath())
		digestPen = DigestPointPen()
		glyphSet["testglyph1"].drawPoints(digestPen)
		digest1 = digestPen.getDigest()
		digestPen = DigestPointPen()
		pen = ReverseContourPointPen(digestPen)
		glyphSet["testglyph1.reversed"].drawPoints(pen)
		digest2 = digestPen.getDigest()
		self.assertEqual(digest1, digest2)


if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	runTests()
