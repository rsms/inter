import os
import tempfile
import shutil
import unittest

from robofab.test.testSupport import getDemoFontGlyphSetPath
from robofab.glifLib import GlyphSet, glyphNameToFileName, READ_MODE
from robofab.tools.glyphNameSchemes import glyphNameToShortFileName


GLYPHSETDIR = getDemoFontGlyphSetPath()


class GlyphSetTests(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)

	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def testRoundTrip(self):
		srcDir = GLYPHSETDIR
		dstDir = self.dstDir
		src = GlyphSet(srcDir)
		dst = GlyphSet(dstDir)
		for glyphName in src.keys():
			g = src[glyphName]
			g.drawPoints(None)  # load attrs
			dst.writeGlyph(glyphName, g, g.drawPoints)
		# compare raw file data:
		for glyphName in src.keys():
			fileName = src.contents[glyphName]
			org = file(os.path.join(srcDir, fileName), READ_MODE).read()
			new = file(os.path.join(dstDir, fileName), READ_MODE).read()
			self.assertEqual(org, new, "%r .glif file differs after round tripping" % glyphName)

	def testRebuildContents(self):
		gset = GlyphSet(GLYPHSETDIR)
		contents = gset.contents
		gset.rebuildContents()
		self.assertEqual(contents, gset.contents)

	def testReverseContents(self):
		gset = GlyphSet(GLYPHSETDIR)
		d = {}
		for k, v in gset.getReverseContents().items():
			d[v] = k
		org = {}
		for k, v in gset.contents.items():
			org[k] = v.lower()
		self.assertEqual(d, org)

	def testReverseContents2(self):
		src = GlyphSet(GLYPHSETDIR)
		dst = GlyphSet(self.dstDir)
		dstMap = dst.getReverseContents()
		self.assertEqual(dstMap, {})
		for glyphName in src.keys():
			g = src[glyphName]
			g.drawPoints(None)  # load attrs
			dst.writeGlyph(glyphName, g, g.drawPoints)
		self.assertNotEqual(dstMap, {})
		srcMap = dict(src.getReverseContents())  # copy
		self.assertEqual(dstMap, srcMap)
		del srcMap["a.glif"]
		dst.deleteGlyph("a")
		self.assertEqual(dstMap, srcMap)

	def testCustomFileNamingScheme(self):
		def myGlyphNameToFileName(glyphName, glyphSet):
			return "prefix" + glyphNameToFileName(glyphName, glyphSet)
		src = GlyphSet(GLYPHSETDIR)
		dst = GlyphSet(self.dstDir, myGlyphNameToFileName)
		for glyphName in src.keys():
			g = src[glyphName]
			g.drawPoints(None)  # load attrs
			dst.writeGlyph(glyphName, g, g.drawPoints)
		d = {}
		for k, v in src.contents.items():
			print k, v
			d[k] = "prefix" + v
		self.assertEqual(d, dst.contents)

	def testGetUnicodes(self):
		src = GlyphSet(GLYPHSETDIR)
		unicodes = src.getUnicodes()
		for glyphName in src.keys():
			g = src[glyphName]
			g.drawPoints(None)  # load attrs
			if not hasattr(g, "unicodes"):
				self.assertEqual(unicodes[glyphName], [])
			else:
				self.assertEqual(g.unicodes, unicodes[glyphName])


class FileNameTests(unittest.TestCase):

	def testDefaultFileNameScheme(self):
		self.assertEqual(glyphNameToFileName("a", None), "a.glif")
		self.assertEqual(glyphNameToFileName("A", None), "A_.glif")
		self.assertEqual(glyphNameToFileName("Aring", None), "Aring_.glif")
		self.assertEqual(glyphNameToFileName("F_A_B", None), "F__A__B_.glif")
		self.assertEqual(glyphNameToFileName("A.alt", None), "A_.alt.glif")
		self.assertEqual(glyphNameToFileName("A.Alt", None), "A_.Alt_.glif")
		self.assertEqual(glyphNameToFileName(".notdef", None), "_notdef.glif")
		self.assertEqual(glyphNameToFileName("T_H", None), "T__H_.glif")
		self.assertEqual(glyphNameToFileName("T_h", None), "T__h.glif")
		self.assertEqual(glyphNameToFileName("t_h", None), "t_h.glif")
		self.assertEqual(glyphNameToFileName('F_F_I', None), "F__F__I_.glif")
		self.assertEqual(glyphNameToFileName('f_f_i', None), "f_f_i.glif")
		

	def testShortFileNameScheme(self):
		print "testShortFileNameScheme"
		self.assertEqual(glyphNameToShortFileName("a", None), "a.glif")
		self.assertEqual(glyphNameToShortFileName("A", None), "A_.glif")
		self.assertEqual(glyphNameToShortFileName("aE", None), "aE_.glif")
		self.assertEqual(glyphNameToShortFileName("AE", None), "A_E_.glif")
		self.assertEqual(glyphNameToShortFileName("a.alt", None), "a_alt.glif")
		self.assertEqual(glyphNameToShortFileName("A.alt", None), "A__alt.glif")
		self.assertEqual(glyphNameToShortFileName("a.alt#swash", None), "a_alt_swash.glif")
		self.assertEqual(glyphNameToShortFileName("A.alt", None), "A__alt.glif")
		self.assertEqual(glyphNameToShortFileName(".notdef", None), "_notdef.glif")
		self.assertEqual(glyphNameToShortFileName("f_f_i", None), "f_f_i.glif")
		self.assertEqual(glyphNameToShortFileName("F_F_I", None), "F__F__I_.glif")
		self.assertEqual(glyphNameToShortFileName("acircumflexdieresis.swash.alt1", None), "acircumflexdieresi0cfc8352.glif")
		self.assertEqual(glyphNameToShortFileName("acircumflexdieresis.swash.alt2", None), "acircumflexdieresi95f5d2e8.glif")
		self.assertEqual(glyphNameToShortFileName("Acircumflexdieresis.swash.alt1", None), "A_circumflexdieresed24fb56.glif")
		self.assertEqual(glyphNameToShortFileName("F#weight0.800_width0.425", None), "F__weight0_800_width0_425.glif")
		self.assertEqual(glyphNameToShortFileName("F#weight0.83245511_width0.425693567", None), "F__weight0_8324551c9a4143c.glif")
		self.assertEqual(len(glyphNameToShortFileName("F#weight0.83245511_width0.425693567", None)), 31)
		
	def testShortFileNameScheme_clashes(self):
		# test for the condition in code.robofab.com ticket #5
		name1 = glyphNameToShortFileName('Adieresis', None)
		name2 = glyphNameToShortFileName('a_dieresis', None)
		self.assertNotEqual(name1, name2)
		name1 = glyphNameToShortFileName('AE', None)
		name2 = glyphNameToShortFileName('aE', None)
		self.assertNotEqual(name1, name2)
		

if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	import sys
	if len(sys.argv) > 1 and os.path.isdir(sys.argv[-1]):
		GLYPHSETDIR = sys.argv.pop()
	runTests()
