"""This test suite for ufo glyph methods"""


import unittest
import os
import tempfile
import shutil

from robofab.objects.objectsRF import RFont
from robofab.test.testSupport import getDemoFontPath
from robofab.pens.digestPen import DigestPointPen
from robofab.pens.adapterPens import SegmentToPointPen, FabToFontToolsPenAdapter


class ContourMethodsTestCase(unittest.TestCase):
	
	def setUp(self):
		self.font = RFont(getDemoFontPath())
	
	def testReverseContour(self):
		for glyph in self.font:
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest1 = pen.getDigest()
			for contour in glyph:
				contour.reverseContour()
				contour.reverseContour()
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest2 = pen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same after reversing twice" % glyph.name)
	
	def testStartSegment(self):
		for glyph in self.font:
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest1 = pen.getDigest()
			for contour in glyph:
				contour.setStartSegment(2)
				contour.setStartSegment(-2)
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest2 = pen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same after seting start segment twice" % glyph.name)
	
	def testAppendSegment(self):
		for glyph in self.font:
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest1 = pen.getDigest()
			for contour in glyph:
				contour.insertSegment(2, "curve", [(100, 100), (200, 200), (300, 300)])
				contour.removeSegment(2)
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest2 = pen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same after inserting and removing segment" % glyph.name)
	

class GlyphsMethodsTestCase(ContourMethodsTestCase):

	def testCopyGlyph(self):
		for glyph in self.font:
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest1 = pen.getDigest()
			copy = glyph.copy()
			pen = DigestPointPen()
			copy.drawPoints(pen)
			digest2 = pen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same after copying" % glyph.name)
			self.assertEqual(glyph.lib, copy.lib, "%r's lib not the same after copying" % glyph.name)
			self.assertEqual(glyph.width, copy.width, "%r's width not the same after copying" % glyph.name)
			self.assertEqual(glyph.unicodes, copy.unicodes, "%r's unicodes not the same after copying" % glyph.name)

	def testMoveGlyph(self):
		for glyph in self.font:
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest1 = pen.getDigest()
			glyph.move((100, 200))
			glyph.move((-100, -200))
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest2 = pen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same after moving twice" % glyph.name)
	
	def testScaleGlyph(self):
		for glyph in self.font:
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest1 = pen.getDigest()
			glyph.scale((2, 2))
			glyph.scale((.5, .5))
			pen = DigestPointPen()
			glyph.drawPoints(pen)
			digest2 = pen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same after scaling twice" % glyph.name)

	def testSegmentPenInterface(self):
		for glyph in self.font:
			digestPen = DigestPointPen(ignoreSmoothAndName=True)
			pen = SegmentToPointPen(digestPen)
			glyph.draw(pen)
			digest1 = digestPen.getDigest()
			digestPen = DigestPointPen(ignoreSmoothAndName=True)
			glyph.drawPoints(digestPen)
			digest2 = digestPen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same for gl.draw() and gl.drawPoints()" % glyph.name)

	def testFabPenCompatibility(self):
		for glyph in self.font:
			digestPen = DigestPointPen(ignoreSmoothAndName=True)
			pen = FabToFontToolsPenAdapter(SegmentToPointPen(digestPen))
			glyph.draw(pen)
			digest1 = digestPen.getDigest()
			digestPen = DigestPointPen(ignoreSmoothAndName=True)
			glyph.drawPoints(digestPen)
			digest2 = digestPen.getDigest()
			self.assertEqual(digest1, digest2, "%r not the same for gl.draw() and gl.drawPoints()" % glyph.name)
	
	def testComponentTransformations(self):
		from robofab.objects.objectsRF import RComponent
		name = "baseGlyphName"
		c = RComponent(name, transform=(1,0,0,1,0,0))
		# get values
		assert c.baseGlyph == "baseGlyphName"
		assert c.transformation == c.transformation
		assert c.scale == (1,1)
		assert c.offset == (0,0)
		# set values
		c.offset = (12,34)
		assert c.transformation == (1, 0, 0, 1, 12, 34)
		c.offset = (0,0)
		assert c.transformation == (1,0,0,1,0,0)
		c.scale = (12,34)
		assert c.transformation == (12, 0, 0, 34, 0, 0)


class SaveTestCase(ContourMethodsTestCase):

	def testSaveAs(self):
		path = tempfile.mktemp(".ufo")
		try:
			keys1 = self.font.keys()
			self.font.save(path)
			keys2 = self.font.keys()
			keys1.sort()
			keys2.sort()
			self.assertEqual(keys1, keys2)
			self.assertEqual(self.font.path, path)
			font2 = RFont(path)
			keys3 = font2.keys()
			keys3.sort()
			self.assertEqual(keys1, keys3)
		finally:
			if os.path.exists(path):
				shutil.rmtree(path)

	def testSaveAs2(self):
		path = tempfile.mktemp(".ufo")
		# copy a glyph
		self.font["X"] = self.font["a"].copy()
#		self.assertEqual(self.font["X"].name, "X")
		# remove a glyph
		self.font.removeGlyph("a")
		keys1 = self.font.keys()
		try:
			self.font.save(path)
			self.assertEqual(self.font.path, path)
			keys2 = self.font.keys()
			keys1.sort()
			keys2.sort()
			self.assertEqual(keys1, keys2)
			font2 = RFont(path)
			keys3 = font2.keys()
			keys3.sort()
			self.assertEqual(keys1, keys3)
		finally:
			if os.path.exists(path):
				shutil.rmtree(path)

	def testCustomFileNameScheme(self):
		path = tempfile.mktemp(".ufo")
		libKey = "org.robofab.glyphNameToFileNameFuncName"
		self.font.lib[libKey] = "robofab.test.test_objectsUFO.testGlyphNameToFileName"
		try:
			self.font.save(path)
			self.assertEqual(os.path.exists(os.path.join(path,
					"glyphs", "test_a.glif")), True)
		finally:
			if os.path.exists(path):
				shutil.rmtree(path)


def testGlyphNameToFileName(glyphName, glyphSet):
	from robofab.glifLib import glyphNameToFileName
	return "test_" + glyphNameToFileName(glyphName, glyphSet)


if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	runTests()
