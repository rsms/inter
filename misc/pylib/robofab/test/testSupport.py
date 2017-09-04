"""Miscellaneous helpers for our test suite."""


import sys
import os
import types
import unittest


def getDemoFontPath():
	"""Return the path to Data/DemoFont.ufo/."""
	import robofab
	root = os.path.dirname(os.path.dirname(os.path.dirname(robofab.__file__)))
	return os.path.join(root, "Data", "DemoFont.ufo")


def getDemoFontGlyphSetPath():
	"""Return the path to Data/DemoFont.ufo/glyphs/."""
	return os.path.join(getDemoFontPath(), "glyphs")


def _gatherTestCasesFromCallerByMagic():
	# UGLY magic: fetch TestClass subclasses from the globals of our
	# caller's caller.
	frame = sys._getframe(2)
	return _gatherTestCasesFromDict(frame.f_globals)


def _gatherTestCasesFromDict(d):
	testCases = []
	for ob in d.values():
		if isinstance(ob, type) and issubclass(ob, unittest.TestCase):
			testCases.append(ob)
	return testCases

	
def runTests(testCases=None, verbosity=1):
	"""Run a series of tests."""
	if testCases is None:
		testCases = _gatherTestCasesFromCallerByMagic()
	loader = unittest.TestLoader()
	suites = []
	for testCase in testCases:
		suites.append(loader.loadTestsFromTestCase(testCase))

	testRunner = unittest.TextTestRunner(verbosity=verbosity)
	testSuite = unittest.TestSuite(suites)
	testRunner.run(testSuite)

# font info values used by several tests

fontInfoVersion1 = {
	"familyName"   : "Some Font (Family Name)",
	"styleName"	   : "Regular (Style Name)",
	"fullName"	   : "Some Font-Regular (Postscript Full Name)",
	"fontName"	   : "SomeFont-Regular (Postscript Font Name)",
	"menuName"	   : "Some Font Regular (Style Map Family Name)",
	"fontStyle"	   : 64,
	"note"		   : "A note.",
	"versionMajor" : 1,
	"versionMinor" : 0,
	"year"		   : 2008,
	"copyright"	   : "Copyright Some Foundry.",
	"notice"	   : "Some Font by Some Designer for Some Foundry.",
	"trademark"	   : "Trademark Some Foundry",
	"license"	   : "License info for Some Foundry.",
	"licenseURL"   : "http://somefoundry.com/license",
	"createdBy"	   : "Some Foundry",
	"designer"	   : "Some Designer",
	"designerURL"  : "http://somedesigner.com",
	"vendorURL"	   : "http://somefoundry.com",
	"unitsPerEm"   : 1000,
	"ascender"	   : 750,
	"descender"	   : -250,
	"capHeight"	   : 750,
	"xHeight"	   : 500,
	"defaultWidth" : 400,
	"slantAngle"   : -12.5,
	"italicAngle"  : -12.5,
	"widthName"	   : "Medium (normal)",
	"weightName"   : "Medium",
	"weightValue"  : 500,
	"fondName"	   : "SomeFont Regular (FOND Name)",
	"otFamilyName" : "Some Font (Preferred Family Name)",
	"otStyleName"  : "Regular (Preferred Subfamily Name)",
	"otMacName"	   : "Some Font Regular (Compatible Full Name)",
	"msCharSet"	   : 0,
	"fondID"	   : 15000,
	"uniqueID"	   : 4000000,
	"ttVendor"	   : "SOME",
	"ttUniqueID"   : "OpenType name Table Unique ID",
	"ttVersion"	   : "OpenType name Table Version",
}

fontInfoVersion2 = {
	"familyName"						 : "Some Font (Family Name)",
	"styleName"							 : "Regular (Style Name)",
	"styleMapFamilyName"				 : "Some Font Regular (Style Map Family Name)",
	"styleMapStyleName"					 : "regular",
	"versionMajor"						 : 1,
	"versionMinor"						 : 0,
	"year"								 : 2008,
	"copyright"							 : "Copyright Some Foundry.",
	"trademark"							 : "Trademark Some Foundry",
	"unitsPerEm"						 : 1000,
	"descender"							 : -250,
	"xHeight"							 : 500,
	"capHeight"							 : 750,
	"ascender"							 : 750,
	"italicAngle"						 : -12.5,
	"note"								 : "A note.",
	"openTypeHeadCreated"				 : "2000/01/01 00:00:00",
	"openTypeHeadLowestRecPPEM"			 : 10,
	"openTypeHeadFlags"					 : [0, 1],
	"openTypeHheaAscender"				 : 750,
	"openTypeHheaDescender"				 : -250,
	"openTypeHheaLineGap"				 : 200,
	"openTypeHheaCaretSlopeRise"		 : 1,
	"openTypeHheaCaretSlopeRun"			 : 0,
	"openTypeHheaCaretOffset"			 : 0,
	"openTypeNameDesigner"				 : "Some Designer",
	"openTypeNameDesignerURL"			 : "http://somedesigner.com",
	"openTypeNameManufacturer"			 : "Some Foundry",
	"openTypeNameManufacturerURL"		 : "http://somefoundry.com",
	"openTypeNameLicense"				 : "License info for Some Foundry.",
	"openTypeNameLicenseURL"			 : "http://somefoundry.com/license",
	"openTypeNameVersion"				 : "OpenType name Table Version",
	"openTypeNameUniqueID"				 : "OpenType name Table Unique ID",
	"openTypeNameDescription"			 : "Some Font by Some Designer for Some Foundry.",
	"openTypeNamePreferredFamilyName"	 : "Some Font (Preferred Family Name)",
	"openTypeNamePreferredSubfamilyName" : "Regular (Preferred Subfamily Name)",
	"openTypeNameCompatibleFullName"	 : "Some Font Regular (Compatible Full Name)",
	"openTypeNameSampleText"			 : "Sample Text for Some Font.",
	"openTypeNameWWSFamilyName"			 : "Some Font (WWS Family Name)",
	"openTypeNameWWSSubfamilyName"		 : "Regular (WWS Subfamily Name)",
	"openTypeOS2WidthClass"				 : 5,
	"openTypeOS2WeightClass"			 : 500,
	"openTypeOS2Selection"				 : [3],
	"openTypeOS2VendorID"				 : "SOME",
	"openTypeOS2Panose"					 : [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
	"openTypeOS2FamilyClass"			 : [1, 1],
	"openTypeOS2UnicodeRanges"			 : [0, 1],
	"openTypeOS2CodePageRanges"			 : [0, 1],
	"openTypeOS2TypoAscender"			 : 750,
	"openTypeOS2TypoDescender"			 : -250,
	"openTypeOS2TypoLineGap"			 : 200,
	"openTypeOS2WinAscent"				 : 750,
	"openTypeOS2WinDescent"				 : -250,
	"openTypeOS2Type"					 : [],
	"openTypeOS2SubscriptXSize"			 : 200,
	"openTypeOS2SubscriptYSize"			 : 400,
	"openTypeOS2SubscriptXOffset"		 : 0,
	"openTypeOS2SubscriptYOffset"		 : -100,
	"openTypeOS2SuperscriptXSize"		 : 200,
	"openTypeOS2SuperscriptYSize"		 : 400,
	"openTypeOS2SuperscriptXOffset"		 : 0,
	"openTypeOS2SuperscriptYOffset"		 : 200,
	"openTypeOS2StrikeoutSize"			 : 20,
	"openTypeOS2StrikeoutPosition"		 : 300,
	"openTypeVheaVertTypoAscender"		 : 750,
	"openTypeVheaVertTypoDescender"		 : -250,
	"openTypeVheaVertTypoLineGap"		 : 200,
	"openTypeVheaCaretSlopeRise"		 : 0,
	"openTypeVheaCaretSlopeRun"			 : 1,
	"openTypeVheaCaretOffset"			 : 0,
	"postscriptFontName"				 : "SomeFont-Regular (Postscript Font Name)",
	"postscriptFullName"				 : "Some Font-Regular (Postscript Full Name)",
	"postscriptSlantAngle"				 : -12.5,
	"postscriptUniqueID"				 : 4000000,
	"postscriptUnderlineThickness"		 : 20,
	"postscriptUnderlinePosition"		 : -200,
	"postscriptIsFixedPitch"			 : False,
	"postscriptBlueValues"				 : [500, 510],
	"postscriptOtherBlues"				 : [-250, -260],
	"postscriptFamilyBlues"				 : [500, 510],
	"postscriptFamilyOtherBlues"		 : [-250, -260],
	"postscriptStemSnapH"				 : [100, 120],
	"postscriptStemSnapV"				 : [80, 90],
	"postscriptBlueFuzz"				 : 1,
	"postscriptBlueShift"				 : 7,
	"postscriptBlueScale"				 : 0.039625,
	"postscriptForceBold"				 : True,
	"postscriptDefaultWidthX"			 : 400,
	"postscriptNominalWidthX"			 : 400,
	"postscriptWeightName"				 : "Medium",
	"postscriptDefaultCharacter"		 : ".notdef",
	"postscriptWindowsCharacterSet"		 : 1,
	"macintoshFONDFamilyID"				 : 15000,
	"macintoshFONDName"					 : "SomeFont Regular (FOND Name)",
}

expectedFontInfo1To2Conversion = {
	"familyName"						: "Some Font (Family Name)",
	"styleMapFamilyName"				: "Some Font Regular (Style Map Family Name)",
	"styleMapStyleName"					: "regular",
	"styleName"							: "Regular (Style Name)",
	"unitsPerEm"						: 1000,
	"ascender"							: 750,
	"capHeight"							: 750,
	"xHeight"							: 500,
	"descender"							: -250,
	"italicAngle"						: -12.5,
	"versionMajor"						: 1,
	"versionMinor"						: 0,
	"year"								: 2008,
	"copyright"							: "Copyright Some Foundry.",
	"trademark"							: "Trademark Some Foundry",
	"note"								: "A note.",
	"macintoshFONDFamilyID"				: 15000,
	"macintoshFONDName"					: "SomeFont Regular (FOND Name)",
	"openTypeNameCompatibleFullName"	: "Some Font Regular (Compatible Full Name)",
	"openTypeNameDescription"			: "Some Font by Some Designer for Some Foundry.",
	"openTypeNameDesigner"				: "Some Designer",
	"openTypeNameDesignerURL"			: "http://somedesigner.com",
	"openTypeNameLicense"				: "License info for Some Foundry.",
	"openTypeNameLicenseURL"			: "http://somefoundry.com/license",
	"openTypeNameManufacturer"			: "Some Foundry",
	"openTypeNameManufacturerURL"		: "http://somefoundry.com",
	"openTypeNamePreferredFamilyName"	: "Some Font (Preferred Family Name)",
	"openTypeNamePreferredSubfamilyName": "Regular (Preferred Subfamily Name)",
	"openTypeNameCompatibleFullName"	: "Some Font Regular (Compatible Full Name)",
	"openTypeNameUniqueID"				: "OpenType name Table Unique ID",
	"openTypeNameVersion"				: "OpenType name Table Version",
	"openTypeOS2VendorID"				: "SOME",
	"openTypeOS2WeightClass"			: 500,
	"openTypeOS2WidthClass"				: 5,
	"postscriptDefaultWidthX"			: 400,
	"postscriptFontName"				: "SomeFont-Regular (Postscript Font Name)",
	"postscriptFullName"				: "Some Font-Regular (Postscript Full Name)",
	"postscriptSlantAngle"				: -12.5,
	"postscriptUniqueID"				: 4000000,
	"postscriptWeightName"				: "Medium",
	"postscriptWindowsCharacterSet"		: 1
}

expectedFontInfo2To1Conversion = {
	"familyName"  	: "Some Font (Family Name)",
	"menuName"	  	: "Some Font Regular (Style Map Family Name)",
	"fontStyle"	  	: 64,
	"styleName"	  	: "Regular (Style Name)",
	"unitsPerEm"  	: 1000,
	"ascender"	  	: 750,
	"capHeight"	  	: 750,
	"xHeight"	  	: 500,
	"descender"	  	: -250,
	"italicAngle" 	: -12.5,
	"versionMajor"	: 1,
	"versionMinor"	: 0,
	"copyright"	  	: "Copyright Some Foundry.",
	"trademark"	  	: "Trademark Some Foundry",
	"note"		  	: "A note.",
	"fondID"	  	: 15000,
	"fondName"	  	: "SomeFont Regular (FOND Name)",
	"fullName"	  	: "Some Font Regular (Compatible Full Name)",
	"notice"	  	: "Some Font by Some Designer for Some Foundry.",
	"designer"	  	: "Some Designer",
	"designerURL" 	: "http://somedesigner.com",
	"license"	  	: "License info for Some Foundry.",
	"licenseURL"  	: "http://somefoundry.com/license",
	"createdBy"	  	: "Some Foundry",
	"vendorURL"	  	: "http://somefoundry.com",
	"otFamilyName"	: "Some Font (Preferred Family Name)",
	"otStyleName" 	: "Regular (Preferred Subfamily Name)",
	"otMacName"	  	: "Some Font Regular (Compatible Full Name)",
	"ttUniqueID"  	: "OpenType name Table Unique ID",
	"ttVersion"	  	: "OpenType name Table Version",
	"ttVendor"	  	: "SOME",
	"weightValue" 	: 500,
	"widthName"	  	: "Medium (normal)",
	"defaultWidth"	: 400,
	"fontName"	  	: "SomeFont-Regular (Postscript Font Name)",
	"fullName"	  	: "Some Font-Regular (Postscript Full Name)",
	"slantAngle"  	: -12.5,
	"uniqueID"	  	: 4000000,
	"weightName"  	: "Medium",
	"msCharSet"	  	: 0,
	"year"			: 2008
}
