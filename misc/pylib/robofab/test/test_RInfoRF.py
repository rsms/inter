import unittest
from cStringIO import StringIO
import sys
from robofab import ufoLib
from robofab.objects.objectsRF import RInfo
from robofab.test.testSupport import fontInfoVersion1, fontInfoVersion2


class RInfoRFTestCase(unittest.TestCase):

	def testRoundTripVersion2(self):
		infoObject = RInfo()
		for attr, value in fontInfoVersion2.items():
			setattr(infoObject, attr, value)
			newValue = getattr(infoObject, attr)
			self.assertEqual((attr, newValue), (attr, value))

	def testRoundTripVersion1(self):
		infoObject = RInfo()
		for attr, value in fontInfoVersion1.items():
			if attr not in ufoLib.deprecatedFontInfoAttributesVersion2:
				setattr(infoObject, attr, value)
		for attr, expectedValue in fontInfoVersion1.items():
			if attr not in ufoLib.deprecatedFontInfoAttributesVersion2:
				value = getattr(infoObject, attr)
				self.assertEqual((attr, expectedValue), (attr, value))

	def testVersion1DeprecationRoundTrip(self):
		"""
		unittest doesn't catch warnings in self.assertRaises,
		so some hackery is required to catch the warnings
		that are raised when setting deprecated attributes.
		"""
		saveStderr = sys.stderr
		tempStderr = StringIO()
		sys.stderr = tempStderr
		infoObject = RInfo()
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
		tempStderr = tempStderr.getvalue()
		for attr, line in requiredWarnings:
			self.assertEquals((attr, line in tempStderr), (attr, True))


if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	runTests()
