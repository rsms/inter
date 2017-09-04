import unittest
from cStringIO import StringIO
import sys
from robofab import ufoLib
from robofab.objects.objectsFL import NewFont
from robofab.test.testSupport import fontInfoVersion1, fontInfoVersion2


class RInfoRFTestCase(unittest.TestCase):

	def testRoundTripVersion2(self):
		font = NewFont()
		infoObject = font.info
		for attr, value in fontInfoVersion2.items():
			if attr in infoObject._ufoToFLAttrMapping and infoObject._ufoToFLAttrMapping[attr]["nakedAttribute"] is None:
				continue
			setattr(infoObject, attr, value)
			newValue = getattr(infoObject, attr)
			self.assertEqual((attr, newValue), (attr, value))
		font.close()

	def testVersion2UnsupportedSet(self):
		saveStderr = sys.stderr
		saveStdout = sys.stdout
		tempStderr = StringIO()
		sys.stderr = tempStderr
		sys.stdout = tempStderr
		font = NewFont()
		infoObject = font.info
		requiredWarnings = []
		try:
			for attr, value in fontInfoVersion2.items():
				if attr in infoObject._ufoToFLAttrMapping and infoObject._ufoToFLAttrMapping[attr]["nakedAttribute"] is not None:
					continue
				setattr(infoObject, attr, value)
				s = "The attribute %s is not supported by FontLab." % attr
				requiredWarnings.append((attr, s))
		finally:
			sys.stderr = saveStderr
			sys.stdout = saveStdout
		tempStderr = tempStderr.getvalue()
		for attr, line in requiredWarnings:
			self.assertEquals((attr, line in tempStderr), (attr, True))
		font.close()

	def testVersion2UnsupportedGet(self):
		saveStderr = sys.stderr
		saveStdout = sys.stdout
		tempStderr = StringIO()
		sys.stderr = tempStderr
		sys.stdout = tempStderr
		font = NewFont()
		infoObject = font.info
		requiredWarnings = []
		try:
			for attr, value in fontInfoVersion2.items():
				if attr in infoObject._ufoToFLAttrMapping and infoObject._ufoToFLAttrMapping[attr]["nakedAttribute"] is not None:
					continue
				getattr(infoObject, attr, value)
				s = "The attribute %s is not supported by FontLab." % attr
				requiredWarnings.append((attr, s))
		finally:
			sys.stderr = saveStderr
			sys.stdout = saveStdout
		tempStderr = tempStderr.getvalue()
		for attr, line in requiredWarnings:
			self.assertEquals((attr, line in tempStderr), (attr, True))
		font.close()

	def testRoundTripVersion1(self):
		font = NewFont()
		infoObject = font.info
		for attr, value in fontInfoVersion1.items():
			if attr not in ufoLib.deprecatedFontInfoAttributesVersion2:
				setattr(infoObject, attr, value)
		for attr, expectedValue in fontInfoVersion1.items():
			if attr not in ufoLib.deprecatedFontInfoAttributesVersion2:
				value = getattr(infoObject, attr)
				self.assertEqual((attr, expectedValue), (attr, value))
		font.close()

	def testVersion1DeprecationRoundTrip(self):
		saveStderr = sys.stderr
		saveStdout = sys.stdout
		tempStderr = StringIO()
		sys.stderr = tempStderr
		sys.stdout = tempStderr
		font = NewFont()
		infoObject = font.info
		requiredWarnings = []
		try:
			for attr, value in fontInfoVersion1.items():
				if attr in ufoLib.deprecatedFontInfoAttributesVersion2:
					setattr(infoObject, attr, value)
					v = getattr(infoObject, attr)
					self.assertEquals((attr, value), (attr, v))
					s = "DeprecationWarning: The %s attribute has been deprecated." % attr
					requiredWarnings.append((attr, s))
		finally:
			sys.stderr = saveStderr
			sys.stdout = saveStdout
		tempStderr = tempStderr.getvalue()
		for attr, line in requiredWarnings:
			self.assertEquals((attr, line in tempStderr), (attr, True))
		font.close()


if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	runTests()

