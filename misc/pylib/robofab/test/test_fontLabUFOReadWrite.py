import os
import shutil
import unittest
import tempfile
from robofab.plistlib import readPlist
import robofab
from robofab.ufoLib import UFOReader, UFOWriter
from robofab.test.testSupport import fontInfoVersion2, expectedFontInfo1To2Conversion
from robofab.objects.objectsFL import NewFont, OpenFont

vfbPath = os.path.dirname(robofab.__file__)
vfbPath = os.path.dirname(vfbPath)
vfbPath = os.path.dirname(vfbPath)
vfbPath = os.path.join(vfbPath, "TestData", "TestFont1.vfb")

ufoPath1 = os.path.dirname(robofab.__file__)
ufoPath1 = os.path.dirname(ufoPath1)
ufoPath1 = os.path.dirname(ufoPath1)
ufoPath1 = os.path.join(ufoPath1, "TestData", "TestFont1 (UFO1).ufo")
ufoPath2 = ufoPath1.replace("TestFont1 (UFO1).ufo", "TestFont1 (UFO2).ufo")


expectedFormatVersion1Features = """@myClass = [A B];

feature liga {
    sub A A by b;
} liga;
"""

# robofab should remove these from the lib after a load.
removeFromFormatVersion1Lib = [
	"org.robofab.opentype.classes",
	"org.robofab.opentype.features",
	"org.robofab.opentype.featureorder",
	"org.robofab.postScriptHintData"
]


class ReadUFOFormatVersion1TestCase(unittest.TestCase):

	def setUpFont(self, doInfo=False, doKerning=False, doGroups=False, doLib=False, doFeatures=False):
		self.font = NewFont()
		self.ufoPath = ufoPath1
		self.font.readUFO(ufoPath1, doInfo=doInfo, doKerning=doKerning, doGroups=doGroups, doLib=doLib, doFeatures=doFeatures)
		self.font.update()

	def tearDownFont(self):
		self.font.close()
		self.font = None

	def compareToUFO(self, doInfo=True, doKerning=True, doGroups=True, doLib=True, doFeatures=True):
		reader = UFOReader(self.ufoPath)
		results = {}
		if doInfo:
			infoMatches = True
			info = self.font.info
			for attr, expectedValue in expectedFontInfo1To2Conversion.items():
				writtenValue = getattr(info, attr)
				if expectedValue != writtenValue:
					infoMatches = False
					break
			results["info"]= infoMatches
		if doKerning:
			kerning = self.font.kerning.asDict()
			expectedKerning = reader.readKerning()
			results["kerning"] = expectedKerning == kerning
		if doGroups:
			groups = dict(self.font.groups)
			expectedGroups = reader.readGroups()
			results["groups"] = expectedGroups == groups
		if doFeatures:
			features = self.font.features.text
			expectedFeatures = expectedFormatVersion1Features
			# FontLab likes to add lines to the features, so skip blank lines.
			features = [line for line in features.splitlines() if line]
			expectedFeatures = [line for line in expectedFeatures.splitlines() if line]
			results["features"] = expectedFeatures == features
		if doLib:
			lib = dict(self.font.lib)
			expectedLib = reader.readLib()
			for key in removeFromFormatVersion1Lib:
				if key in expectedLib:
					del expectedLib[key]
			results["lib"] = expectedLib == lib
		return results

	def testFull(self):
		self.setUpFont(doInfo=True, doKerning=True, doGroups=True, doFeatures=True, doLib=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], True)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], True)
		self.assertEqual(otherResults["features"], True)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()

	def testInfo(self):
		self.setUpFont(doInfo=True)
		otherResults = self.compareToUFO(doInfo=False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		info = self.font.info
		for attr, expectedValue in expectedFontInfo1To2Conversion.items():
			writtenValue = getattr(info, attr)
			self.assertEqual((attr, expectedValue), (attr, writtenValue))
		self.tearDownFont()

	def testFeatures(self):
		self.setUpFont(doFeatures=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], True)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testKerning(self):
		self.setUpFont(doKerning=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testGroups(self):
		self.setUpFont(doGroups=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], True)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testLib(self):
		self.setUpFont(doLib=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()


class ReadUFOFormatVersion2TestCase(unittest.TestCase):

	def setUpFont(self, doInfo=False, doKerning=False, doGroups=False, doLib=False, doFeatures=False):
		self.font = NewFont()
		self.ufoPath = ufoPath2
		self.font.readUFO(ufoPath2, doInfo=doInfo, doKerning=doKerning, doGroups=doGroups, doLib=doLib, doFeatures=doFeatures)
		self.font.update()

	def tearDownFont(self):
		self.font.close()
		self.font = None

	def compareToUFO(self, doInfo=True, doKerning=True, doGroups=True, doLib=True, doFeatures=True):
		reader = UFOReader(self.ufoPath)
		results = {}
		if doInfo:
			infoMatches = True
			info = self.font.info
			for attr, expectedValue in fontInfoVersion2.items():
				# cheat by skipping attrs that aren't supported
				if info._ufoToFLAttrMapping[attr]["nakedAttribute"] is None:
					continue
				writtenValue = getattr(info, attr)
				if expectedValue != writtenValue:
					infoMatches = False
					break
			results["info"]= infoMatches
		if doKerning:
			kerning = self.font.kerning.asDict()
			expectedKerning = reader.readKerning()
			results["kerning"] = expectedKerning == kerning
		if doGroups:
			groups = dict(self.font.groups)
			expectedGroups = reader.readGroups()
			results["groups"] = expectedGroups == groups
		if doFeatures:
			features = self.font.features.text
			expectedFeatures = reader.readFeatures()
			results["features"] = expectedFeatures == features
		if doLib:
			lib = dict(self.font.lib)
			expectedLib = reader.readLib()
			results["lib"] = expectedLib == lib
		return results

	def testFull(self):
		self.setUpFont(doInfo=True, doKerning=True, doGroups=True, doFeatures=True, doLib=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], True)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], True)
		self.assertEqual(otherResults["features"], True)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()

	def testInfo(self):
		self.setUpFont(doInfo=True)
		otherResults = self.compareToUFO(doInfo=False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		info = self.font.info
		for attr, expectedValue in fontInfoVersion2.items():
			# cheat by skipping attrs that aren't supported
			if info._ufoToFLAttrMapping[attr]["nakedAttribute"] is None:
				continue
			writtenValue = getattr(info, attr)
			self.assertEqual((attr, expectedValue), (attr, writtenValue))
		self.tearDownFont()

	def testFeatures(self):
		self.setUpFont(doFeatures=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], True)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testKerning(self):
		self.setUpFont(doKerning=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testGroups(self):
		self.setUpFont(doGroups=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], True)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testLib(self):
		self.setUpFont(doLib=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()


class WriteUFOFormatVersion1TestCase(unittest.TestCase):

	def setUpFont(self, doInfo=False, doKerning=False, doGroups=False):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)
		self.font = OpenFont(vfbPath)
		self.font.writeUFO(self.dstDir, doInfo=doInfo, doKerning=doKerning, doGroups=doGroups, formatVersion=1)
		self.font.close()

	def tearDownFont(self):
		shutil.rmtree(self.dstDir)

	def compareToUFO(self, doInfo=True, doKerning=True, doGroups=True, doLib=True, doFeatures=True):
		readerExpected = UFOReader(ufoPath1)
		readerWritten = UFOReader(self.dstDir)
		results = {}
		if doInfo:
			matches = True
			expectedPath = os.path.join(ufoPath1, "fontinfo.plist")
			writtenPath = os.path.join(self.dstDir, "fontinfo.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				expected = readPlist(expectedPath)
				written = readPlist(writtenPath)
				for attr, expectedValue in expected.items():
					if expectedValue != written[attr]:
						matches = False
						break
			results["info"] = matches
		if doKerning:
			matches = True
			expectedPath = os.path.join(ufoPath1, "kerning.plist")
			writtenPath = os.path.join(self.dstDir, "kerning.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				matches = readPlist(expectedPath) == readPlist(writtenPath)
			results["kerning"] = matches
		if doGroups:
			matches = True
			expectedPath = os.path.join(ufoPath1, "groups.plist")
			writtenPath = os.path.join(self.dstDir, "groups.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				matches = readPlist(expectedPath) == readPlist(writtenPath)
			results["groups"] = matches
		if doFeatures:
			matches = True
			featuresPath = os.path.join(self.dstDir, "features.fea")
			libPath = os.path.join(self.dstDir, "lib.plist")
			if os.path.exists(featuresPath):
				matches = False
			else:
				fontLib = readPlist(libPath)
				writtenText = [fontLib.get("org.robofab.opentype.classes", "")]
				features = fontLib.get("org.robofab.opentype.features", {})
				featureOrder= fontLib.get("org.robofab.opentype.featureorder", [])
				for featureName in featureOrder:
					writtenText.append(features.get(featureName, ""))
				writtenText = "\n".join(writtenText)
				# FontLab likes to add lines to the features, so skip blank lines.
				expectedText = [line for line in expectedFormatVersion1Features.splitlines() if line]
				writtenText = [line for line in writtenText.splitlines() if line]
				matches = "\n".join(expectedText) == "\n".join(writtenText)
			results["features"] = matches
		if doLib:
			matches = True
			expectedPath = os.path.join(ufoPath1, "lib.plist")
			writtenPath = os.path.join(self.dstDir, "lib.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				# the test file doesn't have the glyph order
				# so purge it from the written
				writtenLib = readPlist(writtenPath)
				del writtenLib["org.robofab.glyphOrder"]
				matches = readPlist(expectedPath) == writtenLib
			results["lib"] = matches
		return results

	def testFull(self):
		self.setUpFont(doInfo=True, doKerning=True, doGroups=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], True)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], True)
		self.assertEqual(otherResults["features"], True)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()

	def testInfo(self):
		self.setUpFont(doInfo=True)
		otherResults = self.compareToUFO(doInfo=False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		expectedPath = os.path.join(ufoPath1, "fontinfo.plist")
		writtenPath = os.path.join(self.dstDir, "fontinfo.plist")
		expected = readPlist(expectedPath)
		written = readPlist(writtenPath)
		for attr, expectedValue in expected.items():
			self.assertEqual((attr, expectedValue), (attr, written[attr]))
		self.tearDownFont()

	def testFeatures(self):
		self.setUpFont()
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], True)
		self.tearDownFont()

	def testKerning(self):
		self.setUpFont(doKerning=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], False)
		self.tearDownFont()

	def testGroups(self):
		self.setUpFont(doGroups=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], True)
		self.tearDownFont()

	def testLib(self):
		self.setUpFont()
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()



class WriteUFOFormatVersion2TestCase(unittest.TestCase):

	def setUpFont(self, doInfo=False, doKerning=False, doGroups=False, doLib=False, doFeatures=False):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)
		self.font = OpenFont(vfbPath)
		self.font.writeUFO(self.dstDir, doInfo=doInfo, doKerning=doKerning, doGroups=doGroups, doLib=doLib, doFeatures=doFeatures)
		self.font.close()

	def tearDownFont(self):
		shutil.rmtree(self.dstDir)

	def compareToUFO(self, doInfo=True, doKerning=True, doGroups=True, doLib=True, doFeatures=True):
		readerExpected = UFOReader(ufoPath2)
		readerWritten = UFOReader(self.dstDir)
		results = {}
		if doInfo:
			matches = True
			expectedPath = os.path.join(ufoPath2, "fontinfo.plist")
			writtenPath = os.path.join(self.dstDir, "fontinfo.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				dummyFont = NewFont()
				_ufoToFLAttrMapping = dict(dummyFont.info._ufoToFLAttrMapping)
				dummyFont.close()
				expected = readPlist(expectedPath)
				written = readPlist(writtenPath)
				for attr, expectedValue in expected.items():
					# cheat by skipping attrs that aren't supported
					if _ufoToFLAttrMapping[attr]["nakedAttribute"] is None:
						continue
					if expectedValue != written[attr]:
						matches = False
						break
			results["info"] = matches
		if doKerning:
			matches = True
			expectedPath = os.path.join(ufoPath2, "kerning.plist")
			writtenPath = os.path.join(self.dstDir, "kerning.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				matches = readPlist(expectedPath) == readPlist(writtenPath)
			results["kerning"] = matches
		if doGroups:
			matches = True
			expectedPath = os.path.join(ufoPath2, "groups.plist")
			writtenPath = os.path.join(self.dstDir, "groups.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				matches = readPlist(expectedPath) == readPlist(writtenPath)
			results["groups"] = matches
		if doFeatures:
			matches = True
			expectedPath = os.path.join(ufoPath2, "features.fea")
			writtenPath = os.path.join(self.dstDir, "features.fea")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				f = open(expectedPath, "r")
				expectedText = f.read()
				f.close()
				f = open(writtenPath, "r")
				writtenText = f.read()
				f.close()
				# FontLab likes to add lines to the features, so skip blank lines.
				expectedText = [line for line in expectedText.splitlines() if line]
				writtenText = [line for line in writtenText.splitlines() if line]
				matches = "\n".join(expectedText) == "\n".join(writtenText)
			results["features"] = matches
		if doLib:
			matches = True
			expectedPath = os.path.join(ufoPath2, "lib.plist")
			writtenPath = os.path.join(self.dstDir, "lib.plist")
			if not os.path.exists(writtenPath):
				matches = False
			else:
				# the test file doesn't have the glyph order
				# so purge it from the written
				writtenLib = readPlist(writtenPath)
				del writtenLib["org.robofab.glyphOrder"]
				matches = readPlist(expectedPath) == writtenLib
			results["lib"] = matches
		return results

	def testFull(self):
		self.setUpFont(doInfo=True, doKerning=True, doGroups=True, doFeatures=True, doLib=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], True)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], True)
		self.assertEqual(otherResults["features"], True)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()

	def testInfo(self):
		self.setUpFont(doInfo=True)
		otherResults = self.compareToUFO(doInfo=False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		expectedPath = os.path.join(ufoPath2, "fontinfo.plist")
		writtenPath = os.path.join(self.dstDir, "fontinfo.plist")
		expected = readPlist(expectedPath)
		written = readPlist(writtenPath)
		dummyFont = NewFont()
		_ufoToFLAttrMapping = dict(dummyFont.info._ufoToFLAttrMapping)
		dummyFont.close()
		for attr, expectedValue in expected.items():
			# cheat by skipping attrs that aren't supported
			if _ufoToFLAttrMapping[attr]["nakedAttribute"] is None:
				continue
			self.assertEqual((attr, expectedValue), (attr, written[attr]))
		self.tearDownFont()

	def testFeatures(self):
		self.setUpFont(doFeatures=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], True)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testKerning(self):
		self.setUpFont(doKerning=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], True)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testGroups(self):
		self.setUpFont(doGroups=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], True)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], False)
		self.tearDownFont()

	def testLib(self):
		self.setUpFont(doLib=True)
		otherResults = self.compareToUFO()
		self.assertEqual(otherResults["info"], False)
		self.assertEqual(otherResults["kerning"], False)
		self.assertEqual(otherResults["groups"], False)
		self.assertEqual(otherResults["features"], False)
		self.assertEqual(otherResults["lib"], True)
		self.tearDownFont()


if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	runTests()
