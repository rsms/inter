"""This test suite for various FontLab-specific tests."""


import FL  # needed to quickly raise ImportError if run outside of FL


import os
import tempfile
import unittest

from robofab.world import NewFont
from robofab.test.testSupport import getDemoFontPath, getDemoFontGlyphSetPath
from robofab.tools.glifImport import importAllGlifFiles
from robofab.pens.digestPen import DigestPointPen
from robofab.pens.adapterPens import SegmentToPointPen


def getDigests(font):
	digests = {}
	for glyphName in font.keys():
		pen = DigestPointPen()
		font[glyphName].drawPoints(pen)
		digests[glyphName] = pen.getDigest()
	return digests


class FLTestCase(unittest.TestCase):

	def testUFOVersusGlifImport(self):
		font = NewFont()
		font.readUFO(getDemoFontPath(), doProgress=False)
		d1 = getDigests(font)
		font.close(False)
		font = NewFont()
		importAllGlifFiles(font.naked(), getDemoFontGlyphSetPath(), doProgress=False)
		d2 = getDigests(font)
		self.assertEqual(d1, d2)
		font.close(False)

	def testTwoUntitledFonts(self):
		font1 = NewFont()
		font2 = NewFont()
		font1.unitsPerEm = 1024
		font2.unitsPerEm = 2048
		self.assertNotEqual(font1.unitsPerEm, font2.unitsPerEm)
		font1.update()
		font2.update()
		font1.close(False)
		font2.close(False)


if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	runTests()
