""""
A library for importing .ufo files and their descendants.
Refer to http://unifiedfontobject.com for the UFO specification.

The UFOReader and UFOWriter classes support versions 1 and 2
of the specification. Up and down conversion functions are also
supplied in this library. These conversion functions are only
necessary if conversion without loading the UFO data into
a set of objects is desired. These functions are:
	convertUFOFormatVersion1ToFormatVersion2
	convertUFOFormatVersion2ToFormatVersion1

Two sets that list the font info attribute names for the two
fontinfo.plist formats are available for external use. These are:
	fontInfoAttributesVersion1
	fontInfoAttributesVersion2

A set listing the fontinfo.plist attributes that were deprecated
in version 2 is available for external use:
	deprecatedFontInfoAttributesVersion2

A function, validateFontInfoVersion2ValueForAttribute, that does
some basic validation on values for a fontinfo.plist value is
available for external use.

Two value conversion functions are availble for converting
fontinfo.plist values between the possible format versions.
	convertFontInfoValueForAttributeFromVersion1ToVersion2
	convertFontInfoValueForAttributeFromVersion2ToVersion1
"""


import os
import shutil
from cStringIO import StringIO
import calendar
from robofab.plistlib import readPlist, writePlist
from robofab.glifLib import GlyphSet, READ_MODE, WRITE_MODE

try:
	set
except NameError:
	from sets import Set as set

__all__ = [
	"makeUFOPath"
	"UFOLibError",
	"UFOReader",
	"UFOWriter",
	"convertUFOFormatVersion1ToFormatVersion2",
	"convertUFOFormatVersion2ToFormatVersion1",
	"fontInfoAttributesVersion1",
	"fontInfoAttributesVersion2",
	"deprecatedFontInfoAttributesVersion2",
	"validateFontInfoVersion2ValueForAttribute",
	"convertFontInfoValueForAttributeFromVersion1ToVersion2",
	"convertFontInfoValueForAttributeFromVersion2ToVersion1"
]


class UFOLibError(Exception): pass


# ----------
# File Names
# ----------

GLYPHS_DIRNAME = "glyphs"
METAINFO_FILENAME = "metainfo.plist"
FONTINFO_FILENAME = "fontinfo.plist"
LIB_FILENAME = "lib.plist"	
GROUPS_FILENAME = "groups.plist"
KERNING_FILENAME = "kerning.plist"
FEATURES_FILENAME = "features.fea"

supportedUFOFormatVersions = [1, 2]


# ---------------------------
# Format Conversion Functions
# ---------------------------


def convertUFOFormatVersion1ToFormatVersion2(inPath, outPath=None):
	"""
	Function for converting a version format 1 UFO
	to version format 2. inPath should be a path
	to a UFO. outPath is the path where the new UFO
	should be written. If outPath is not given, the
	inPath will be used and, therefore, the UFO will
	be converted in place. Otherwise, if outPath is
	specified, nothing must exist at that path.
	"""
	if outPath is None:
		outPath = inPath
	if inPath != outPath and os.path.exists(outPath):
		raise UFOLibError("A file already exists at %s." % outPath)
	# use a reader for loading most of the data
	reader = UFOReader(inPath)
	if reader.formatVersion == 2:
		raise UFOLibError("The UFO at %s is already format version 2." % inPath)
	groups = reader.readGroups()
	kerning = reader.readKerning()
	libData = reader.readLib()
	# read the info data manually and convert
	infoPath = os.path.join(inPath, FONTINFO_FILENAME)
	if not os.path.exists(infoPath):
		infoData = {}
	else:
		infoData = readPlist(infoPath)
	infoData = _convertFontInfoDataVersion1ToVersion2(infoData)
	# if the paths are the same, only need to change the
	# fontinfo and meta info files.
	infoPath = os.path.join(outPath, FONTINFO_FILENAME)
	if inPath == outPath:
		metaInfoPath = os.path.join(inPath, METAINFO_FILENAME)
		metaInfo = dict(
			creator="org.robofab.ufoLib",
			formatVersion=2
		)
		writePlistAtomically(metaInfo, metaInfoPath)
		writePlistAtomically(infoData, infoPath)
	# otherwise write everything.
	else:
		writer = UFOWriter(outPath)
		writer.writeGroups(groups)
		writer.writeKerning(kerning)
		writer.writeLib(libData)
		# write the info manually
		writePlistAtomically(infoData, infoPath)
		# copy the glyph tree
		inGlyphs = os.path.join(inPath, GLYPHS_DIRNAME)
		outGlyphs = os.path.join(outPath, GLYPHS_DIRNAME)
		if os.path.exists(inGlyphs):
			shutil.copytree(inGlyphs, outGlyphs)

def convertUFOFormatVersion2ToFormatVersion1(inPath, outPath=None):
	"""
	Function for converting a version format 2 UFO
	to version format 1. inPath should be a path
	to a UFO. outPath is the path where the new UFO
	should be written. If outPath is not given, the
	inPath will be used and, therefore, the UFO will
	be converted in place. Otherwise, if outPath is
	specified, nothing must exist at that path.
	"""
	if outPath is None:
		outPath = inPath
	if inPath != outPath and os.path.exists(outPath):
		raise UFOLibError("A file already exists at %s." % outPath)
	# use a reader for loading most of the data
	reader = UFOReader(inPath)
	if reader.formatVersion == 1:
		raise UFOLibError("The UFO at %s is already format version 1." % inPath)
	groups = reader.readGroups()
	kerning = reader.readKerning()
	libData = reader.readLib()
	# read the info data manually and convert
	infoPath = os.path.join(inPath, FONTINFO_FILENAME)
	if not os.path.exists(infoPath):
		infoData = {}
	else:
		infoData = readPlist(infoPath)
	infoData = _convertFontInfoDataVersion2ToVersion1(infoData)
	# if the paths are the same, only need to change the
	# fontinfo, metainfo and feature files.
	infoPath = os.path.join(outPath, FONTINFO_FILENAME)
	if inPath == outPath:
		metaInfoPath = os.path.join(inPath, METAINFO_FILENAME)
		metaInfo = dict(
			creator="org.robofab.ufoLib",
			formatVersion=1
		)
		writePlistAtomically(metaInfo, metaInfoPath)
		writePlistAtomically(infoData, infoPath)
		featuresPath = os.path.join(inPath, FEATURES_FILENAME)
		if os.path.exists(featuresPath):
			os.remove(featuresPath)
	# otherwise write everything.
	else:
		writer = UFOWriter(outPath, formatVersion=1)
		writer.writeGroups(groups)
		writer.writeKerning(kerning)
		writer.writeLib(libData)
		# write the info manually
		writePlistAtomically(infoData, infoPath)
		# copy the glyph tree
		inGlyphs = os.path.join(inPath, GLYPHS_DIRNAME)
		outGlyphs = os.path.join(outPath, GLYPHS_DIRNAME)
		if os.path.exists(inGlyphs):
			shutil.copytree(inGlyphs, outGlyphs)


# ----------
# UFO Reader
# ----------


class UFOReader(object):

	"""Read the various components of the .ufo."""

	def __init__(self, path):
		self._path = path
		self.readMetaInfo()

	def _get_formatVersion(self):
		return self._formatVersion

	formatVersion = property(_get_formatVersion, doc="The format version of the UFO. This is determined by reading metainfo.plist during __init__.")

	def _checkForFile(self, path):
		if not os.path.exists(path):
			return False
		else:
			return True

	def readMetaInfo(self):
		"""
		Read metainfo.plist. Only used for internal operations.
		"""
		path = os.path.join(self._path, METAINFO_FILENAME)
		if not self._checkForFile(path):
			raise UFOLibError("metainfo.plist is missing in %s. This file is required." % self._path)
		# should there be a blind try/except with a UFOLibError
		# raised in except here (and elsewhere)? It would be nice to
		# provide external callers with a single exception to catch.
		data = readPlist(path)
		formatVersion = data["formatVersion"]
		if formatVersion not in supportedUFOFormatVersions:
			raise UFOLibError("Unsupported UFO format (%d) in %s." % (formatVersion, self._path))
		self._formatVersion = formatVersion

	def readGroups(self):
		"""
		Read groups.plist. Returns a dict.
		"""
		path = os.path.join(self._path, GROUPS_FILENAME)
		if not self._checkForFile(path):
			return {}
		return readPlist(path)

	def readInfo(self, info):
		"""
		Read fontinfo.plist. It requires an object that allows
		setting attributes with names that follow the fontinfo.plist
		version 2 specification. This will write the attributes
		defined in the file into the object.
		"""
		# load the file and return if there is no file
		path = os.path.join(self._path, FONTINFO_FILENAME)
		if not self._checkForFile(path):
			return
		infoDict = readPlist(path)
		infoDataToSet = {}
		# version 1
		if self._formatVersion == 1:
			for attr in fontInfoAttributesVersion1:
				value = infoDict.get(attr)
				if value is not None:
					infoDataToSet[attr] = value
			infoDataToSet = _convertFontInfoDataVersion1ToVersion2(infoDataToSet)
		# version 2
		elif self._formatVersion == 2:
			for attr, dataValidationDict in _fontInfoAttributesVersion2ValueData.items():
				value = infoDict.get(attr)
				if value is None:
					continue
				infoDataToSet[attr] = value
		# unsupported version
		else:
			raise NotImplementedError
		# validate data
		infoDataToSet = _validateInfoVersion2Data(infoDataToSet)
		# populate the object
		for attr, value in infoDataToSet.items():
			try:
				setattr(info, attr, value)
			except AttributeError:
				raise UFOLibError("The supplied info object does not support setting a necessary attribute (%s)." % attr)

	def readKerning(self):
		"""
		Read kerning.plist. Returns a dict.
		"""
		path = os.path.join(self._path, KERNING_FILENAME)
		if not self._checkForFile(path):
			return {}
		kerningNested = readPlist(path)
		kerning = {}
		for left in kerningNested:
			for right in kerningNested[left]:
				value = kerningNested[left][right]
				kerning[left, right] = value
		return kerning

	def readLib(self):
		"""
		Read lib.plist. Returns a dict.
		"""
		path = os.path.join(self._path, LIB_FILENAME)
		if not self._checkForFile(path):
			return {}
		return readPlist(path)

	def readFeatures(self):
		"""
		Read features.fea. Returns a string.
		"""
		path = os.path.join(self._path, FEATURES_FILENAME)
		if not self._checkForFile(path):
			return ""
		f = open(path, READ_MODE)
		text = f.read()
		f.close()
		return text

	def getGlyphSet(self):
		"""
		Return the GlyphSet associated with the
		glyphs directory in the .ufo.
		"""
		glyphsPath = os.path.join(self._path, GLYPHS_DIRNAME)
		return GlyphSet(glyphsPath)

	def getCharacterMapping(self):
		"""
		Return a dictionary that maps unicode values (ints) to
		lists of glyph names.
		"""
		glyphsPath = os.path.join(self._path, GLYPHS_DIRNAME)
		glyphSet = GlyphSet(glyphsPath)
		allUnicodes = glyphSet.getUnicodes()
		cmap = {}
		for glyphName, unicodes in allUnicodes.iteritems():
			for code in unicodes:
				if code in cmap:
					cmap[code].append(glyphName)
				else:
					cmap[code] = [glyphName]
		return cmap


# ----------
# UFO Writer
# ----------


class UFOWriter(object):

	"""Write the various components of the .ufo."""

	def __init__(self, path, formatVersion=2, fileCreator="org.robofab.ufoLib"):
		if formatVersion not in supportedUFOFormatVersions:
			raise UFOLibError("Unsupported UFO format (%d)." % formatVersion)
		self._path = path
		self._formatVersion = formatVersion
		self._fileCreator = fileCreator
		self._writeMetaInfo()
		# handle down conversion
		if formatVersion == 1:
			## remove existing features.fea
			featuresPath = os.path.join(path, FEATURES_FILENAME)
			if os.path.exists(featuresPath):
				os.remove(featuresPath)

	def _get_formatVersion(self):
		return self._formatVersion

	formatVersion = property(_get_formatVersion, doc="The format version of the UFO. This is set into metainfo.plist during __init__.")

	def _get_fileCreator(self):
		return self._fileCreator

	fileCreator = property(_get_fileCreator, doc="The file creator of the UFO. This is set into metainfo.plist during __init__.")

	def _makeDirectory(self, subDirectory=None):
		path = self._path
		if subDirectory:
			path = os.path.join(self._path, subDirectory)
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def _writeMetaInfo(self):
		self._makeDirectory()
		path = os.path.join(self._path, METAINFO_FILENAME)
		metaInfo = dict(
			creator=self._fileCreator,
			formatVersion=self._formatVersion
		)
		writePlistAtomically(metaInfo, path)

	def writeGroups(self, groups):
		"""
		Write groups.plist. This method requires a
		dict of glyph groups as an argument.
		"""
		self._makeDirectory()
		path = os.path.join(self._path, GROUPS_FILENAME)
		groupsNew = {}
		for key, value in groups.items():
			groupsNew[key] = list(value)
		if groupsNew:
			writePlistAtomically(groupsNew, path)
		elif os.path.exists(path):
			os.remove(path)

	def writeInfo(self, info):
		"""
		Write info.plist. This method requires an object
		that supports getting attributes that follow the
		fontinfo.plist version 2 secification. Attributes
		will be taken from the given object and written
		into the file.
		"""
		self._makeDirectory()
		path = os.path.join(self._path, FONTINFO_FILENAME)
		# gather version 2 data
		infoData = {}
		for attr in _fontInfoAttributesVersion2ValueData.keys():
			try:
				value = getattr(info, attr)
			except AttributeError:
				raise UFOLibError("The supplied info object does not support getting a necessary attribute (%s)." % attr)
			if value is None:
				continue
			infoData[attr] = value
		# validate data
		infoData = _validateInfoVersion2Data(infoData)
		# down convert data to version 1 if necessary
		if self._formatVersion == 1:
			infoData = _convertFontInfoDataVersion2ToVersion1(infoData)
		# write file
		writePlistAtomically(infoData, path)

	def writeKerning(self, kerning):
		"""
		Write kerning.plist. This method requires a
		dict of kerning pairs as an argument.
		"""
		self._makeDirectory()
		path = os.path.join(self._path, KERNING_FILENAME)
		kerningDict = {}
		for left, right in kerning.keys():
			value = kerning[left, right]
			if not left in kerningDict:
				kerningDict[left] = {}
			kerningDict[left][right] = value
		if kerningDict:
			writePlistAtomically(kerningDict, path)
		elif os.path.exists(path):
			os.remove(path)

	def writeLib(self, libDict):
		"""
		Write lib.plist. This method requires a
		lib dict as an argument.
		"""
		self._makeDirectory()
		path = os.path.join(self._path, LIB_FILENAME)
		if libDict:
			writePlistAtomically(libDict, path)
		elif os.path.exists(path):
			os.remove(path)

	def writeFeatures(self, features):
		"""
		Write features.fea. This method requires a
		features string as an argument.
		"""
		if self._formatVersion == 1:
			raise UFOLibError("features.fea is not allowed in UFO Format Version 1.")
		self._makeDirectory()
		path = os.path.join(self._path, FEATURES_FILENAME)
		writeFileAtomically(features, path)

	def makeGlyphPath(self):
		"""
		Make the glyphs directory in the .ufo.
		Returns the path of the directory created.
		"""
		glyphDir = self._makeDirectory(GLYPHS_DIRNAME)
		return glyphDir

	def getGlyphSet(self, glyphNameToFileNameFunc=None):
		"""
		Return the GlyphSet associated with the
		glyphs directory in the .ufo.
		"""
		return GlyphSet(self.makeGlyphPath(), glyphNameToFileNameFunc)

# ----------------
# Helper Functions
# ----------------

def makeUFOPath(path):
	"""
	Return a .ufo pathname.

	>>> makeUFOPath("/directory/something.ext")
	'/directory/something.ufo'
	>>> makeUFOPath("/directory/something.another.thing.ext")
	'/directory/something.another.thing.ufo'
	"""
	dir, name = os.path.split(path)
	name = ".".join([".".join(name.split(".")[:-1]), "ufo"])
	return os.path.join(dir, name)

def writePlistAtomically(obj, path):
	"""
	Write a plist for "obj" to "path". Do this sort of atomically,
	making it harder to cause corrupt files, for example when writePlist
	encounters an error halfway during write. This also checks to see
	if text matches the text that is already in the file at path.
	If so, the file is not rewritten so that the modification date
	is preserved.
	"""
	f = StringIO()
	writePlist(obj, f)
	data = f.getvalue()
	writeFileAtomically(data, path)

def writeFileAtomically(text, path):
	"""Write text into a file at path. Do this sort of atomically
	making it harder to cause corrupt files. This also checks to see
	if text matches the text that is already in the file at path.
	If so, the file is not rewritten so that the modification date
	is preserved."""
	if os.path.exists(path):
		f = open(path, READ_MODE)
		oldText = f.read()
		f.close()
		if text == oldText:
			return
		# if the text is empty, remove the existing file
		if not text:
			os.remove(path)
	if text:
		f = open(path, WRITE_MODE)
		f.write(text)
		f.close()

# ----------------------
# fontinfo.plist Support
# ----------------------

# Version 1

fontInfoAttributesVersion1 = set([
	"familyName",
	"styleName",
	"fullName",
	"fontName",
	"menuName",
	"fontStyle",
	"note",
	"versionMajor",
	"versionMinor",
	"year",
	"copyright",
	"notice",
	"trademark",
	"license",
	"licenseURL",
	"createdBy",
	"designer",
	"designerURL",
	"vendorURL",
	"unitsPerEm",
	"ascender",
	"descender",
	"capHeight",
	"xHeight",
	"defaultWidth",
	"slantAngle",
	"italicAngle",
	"widthName",
	"weightName",
	"weightValue",
	"fondName",
	"otFamilyName",
	"otStyleName",
	"otMacName",
	"msCharSet",
	"fondID",
	"uniqueID",
	"ttVendor",
	"ttUniqueID",
	"ttVersion",
])

# Version 2

# Validators

def validateFontInfoVersion2ValueForAttribute(attr, value):
	"""
	This performs very basic validation of the value for attribute
	following the UFO fontinfo.plist specification. The results
	of this should not be interpretted as *correct* for the font
	that they are part of. This merely indicates that the value
	is of the proper type and, where the specification defines
	a set range of possible values for an attribute, that the
	value is in the accepted range.
	"""
	dataValidationDict = _fontInfoAttributesVersion2ValueData[attr]
	valueType = dataValidationDict.get("type")
	validator = dataValidationDict.get("valueValidator")
	valueOptions = dataValidationDict.get("valueOptions")
	# have specific options for the validator
	if valueOptions is not None:
		isValidValue = validator(value, valueOptions)
	# no specific options
	else:
		if validator == _fontInfoTypeValidator:
			isValidValue = validator(value, valueType)
		else:
			isValidValue = validator(value)
	return isValidValue

def _validateInfoVersion2Data(infoData):
	validInfoData = {}
	for attr, value in infoData.items():
		isValidValue = validateFontInfoVersion2ValueForAttribute(attr, value)
		if not isValidValue:
			raise UFOLibError("Invalid value for attribute %s (%s)." % (attr, repr(value)))
		else:
			validInfoData[attr] = value
	return infoData

def _fontInfoTypeValidator(value, typ):
	return isinstance(value, typ)

def _fontInfoVersion2IntListValidator(values, validValues):
	if not isinstance(values, (list, tuple)):
		return False
	valuesSet = set(values)
	validValuesSet = set(validValues)
	if len(valuesSet - validValuesSet) > 0:
		return False
	for value in values:
		if not isinstance(value, int):
			return False
	return True

def _fontInfoVersion2StyleMapStyleNameValidator(value):
	options = ["regular", "italic", "bold", "bold italic"]
	return value in options

def _fontInfoVersion2OpenTypeHeadCreatedValidator(value):
	# format: 0000/00/00 00:00:00
	if not isinstance(value, (str, unicode)):
		return False
	# basic formatting
	if not len(value) == 19:
		return False
	if value.count(" ") != 1:
		return False
	date, time = value.split(" ")
	if date.count("/") != 2:
		return False
	if time.count(":") != 2:
		return False
	# date
	year, month, day = date.split("/")
	if len(year) != 4:
		return False
	if len(month) != 2:
		return False
	if len(day) != 2:
		return False
	try:
		year = int(year)
		month = int(month)
		day = int(day)
	except ValueError:
		return False
	if month < 1 or month > 12:
		return False
	monthMaxDay = calendar.monthrange(year, month)
	if month > monthMaxDay:
		return False
	# time
	hour, minute, second = time.split(":")
	if len(hour) != 2:
		return False
	if len(minute) != 2:
		return False
	if len(second) != 2:
		return False
	try:
		hour = int(hour)
		minute = int(minute)
		second = int(second)
	except ValueError:
		return False
	if hour < 0 or hour > 23:
		return False
	if minute < 0 or minute > 59:
		return False
	if second < 0 or second > 59:
		return True
	# fallback
	return True

def _fontInfoVersion2OpenTypeOS2WeightClassValidator(value):
	if not isinstance(value, int):
		return False
	if value < 0:
		return False
	return True

def _fontInfoVersion2OpenTypeOS2WidthClassValidator(value):
	if not isinstance(value, int):
		return False
	if value < 1:
		return False
	if value > 9:
		return False
	return True

def _fontInfoVersion2OpenTypeOS2PanoseValidator(values):
	if not isinstance(values, (list, tuple)):
		return False
	if len(values) != 10:
		return False
	for value in values:
		if not isinstance(value, int):
			return False
	# XXX further validation?
	return True

def _fontInfoVersion2OpenTypeOS2FamilyClassValidator(values):
	if not isinstance(values, (list, tuple)):
		return False
	if len(values) != 2:
		return False
	for value in values:
		if not isinstance(value, int):
			return False
	classID, subclassID = values
	if classID < 0 or classID > 14:
		return False
	if subclassID < 0 or subclassID > 15:
		return False
	return True

def _fontInfoVersion2PostscriptBluesValidator(values):
	if not isinstance(values, (list, tuple)):
		return False
	if len(values) > 14:
		return False
	if len(values) % 2:
		return False
	for value in values:
		if not isinstance(value, (int, float)):
			return False
	return True

def _fontInfoVersion2PostscriptOtherBluesValidator(values):
	if not isinstance(values, (list, tuple)):
		return False
	if len(values) > 10:
		return False
	if len(values) % 2:
		return False
	for value in values:
		if not isinstance(value, (int, float)):
			return False
	return True

def _fontInfoVersion2PostscriptStemsValidator(values):
	if not isinstance(values, (list, tuple)):
		return False
	if len(values) > 12:
		return False
	for value in values:
		if not isinstance(value, (int, float)):
			return False
	return True

def _fontInfoVersion2PostscriptWindowsCharacterSetValidator(value):
	validValues = range(1, 21)
	if value not in validValues:
		return False
	return True

# Attribute Definitions
# This defines the attributes, types and, in some
# cases the possible values, that can exist is
# fontinfo.plist.

_fontInfoVersion2OpenTypeHeadFlagsOptions = range(0, 14)
_fontInfoVersion2OpenTypeOS2SelectionOptions = [1, 2, 3, 4, 7, 8, 9]
_fontInfoVersion2OpenTypeOS2UnicodeRangesOptions = range(0, 128)
_fontInfoVersion2OpenTypeOS2CodePageRangesOptions = range(0, 64)
_fontInfoVersion2OpenTypeOS2TypeOptions = [0, 1, 2, 3, 8, 9]

_fontInfoAttributesVersion2ValueData = {
	"familyName"							: dict(type=(str, unicode)),
	"styleName"								: dict(type=(str, unicode)),
	"styleMapFamilyName"					: dict(type=(str, unicode)),
	"styleMapStyleName"						: dict(type=(str, unicode), valueValidator=_fontInfoVersion2StyleMapStyleNameValidator),
	"versionMajor"							: dict(type=int),
	"versionMinor"							: dict(type=int),
	"year"									: dict(type=int),
	"copyright"								: dict(type=(str, unicode)),
	"trademark"								: dict(type=(str, unicode)),
	"unitsPerEm"							: dict(type=(int, float)),
	"descender"								: dict(type=(int, float)),
	"xHeight"								: dict(type=(int, float)),
	"capHeight"								: dict(type=(int, float)),
	"ascender"								: dict(type=(int, float)),
	"italicAngle"							: dict(type=(float, int)),
	"note"									: dict(type=(str, unicode)),
	"openTypeHeadCreated"					: dict(type=(str, unicode), valueValidator=_fontInfoVersion2OpenTypeHeadCreatedValidator),
	"openTypeHeadLowestRecPPEM"				: dict(type=(int, float)),
	"openTypeHeadFlags"						: dict(type="integerList", valueValidator=_fontInfoVersion2IntListValidator, valueOptions=_fontInfoVersion2OpenTypeHeadFlagsOptions),
	"openTypeHheaAscender"					: dict(type=(int, float)),
	"openTypeHheaDescender"					: dict(type=(int, float)),
	"openTypeHheaLineGap"					: dict(type=(int, float)),
	"openTypeHheaCaretSlopeRise"			: dict(type=int),
	"openTypeHheaCaretSlopeRun"				: dict(type=int),
	"openTypeHheaCaretOffset"				: dict(type=(int, float)),
	"openTypeNameDesigner"					: dict(type=(str, unicode)),
	"openTypeNameDesignerURL"				: dict(type=(str, unicode)),
	"openTypeNameManufacturer"				: dict(type=(str, unicode)),
	"openTypeNameManufacturerURL"			: dict(type=(str, unicode)),
	"openTypeNameLicense"					: dict(type=(str, unicode)),
	"openTypeNameLicenseURL"				: dict(type=(str, unicode)),
	"openTypeNameVersion"					: dict(type=(str, unicode)),
	"openTypeNameUniqueID"					: dict(type=(str, unicode)),
	"openTypeNameDescription"				: dict(type=(str, unicode)),
	"openTypeNamePreferredFamilyName"		: dict(type=(str, unicode)),
	"openTypeNamePreferredSubfamilyName"	: dict(type=(str, unicode)),
	"openTypeNameCompatibleFullName"		: dict(type=(str, unicode)),
	"openTypeNameSampleText"				: dict(type=(str, unicode)),
	"openTypeNameWWSFamilyName"				: dict(type=(str, unicode)),
	"openTypeNameWWSSubfamilyName"			: dict(type=(str, unicode)),
	"openTypeOS2WidthClass"					: dict(type=int, valueValidator=_fontInfoVersion2OpenTypeOS2WidthClassValidator),
	"openTypeOS2WeightClass"				: dict(type=int, valueValidator=_fontInfoVersion2OpenTypeOS2WeightClassValidator),
	"openTypeOS2Selection"					: dict(type="integerList", valueValidator=_fontInfoVersion2IntListValidator, valueOptions=_fontInfoVersion2OpenTypeOS2SelectionOptions),
	"openTypeOS2VendorID"					: dict(type=(str, unicode)),
	"openTypeOS2Panose"						: dict(type="integerList", valueValidator=_fontInfoVersion2OpenTypeOS2PanoseValidator),
	"openTypeOS2FamilyClass"				: dict(type="integerList", valueValidator=_fontInfoVersion2OpenTypeOS2FamilyClassValidator),
	"openTypeOS2UnicodeRanges"				: dict(type="integerList", valueValidator=_fontInfoVersion2IntListValidator, valueOptions=_fontInfoVersion2OpenTypeOS2UnicodeRangesOptions),
	"openTypeOS2CodePageRanges"				: dict(type="integerList", valueValidator=_fontInfoVersion2IntListValidator, valueOptions=_fontInfoVersion2OpenTypeOS2CodePageRangesOptions),
	"openTypeOS2TypoAscender"				: dict(type=(int, float)),
	"openTypeOS2TypoDescender"				: dict(type=(int, float)),
	"openTypeOS2TypoLineGap"				: dict(type=(int, float)),
	"openTypeOS2WinAscent"					: dict(type=(int, float)),
	"openTypeOS2WinDescent"					: dict(type=(int, float)),
	"openTypeOS2Type"						: dict(type="integerList", valueValidator=_fontInfoVersion2IntListValidator, valueOptions=_fontInfoVersion2OpenTypeOS2TypeOptions),
	"openTypeOS2SubscriptXSize"				: dict(type=(int, float)),
	"openTypeOS2SubscriptYSize"				: dict(type=(int, float)),
	"openTypeOS2SubscriptXOffset"			: dict(type=(int, float)),
	"openTypeOS2SubscriptYOffset"			: dict(type=(int, float)),
	"openTypeOS2SuperscriptXSize"			: dict(type=(int, float)),
	"openTypeOS2SuperscriptYSize"			: dict(type=(int, float)),
	"openTypeOS2SuperscriptXOffset"			: dict(type=(int, float)),
	"openTypeOS2SuperscriptYOffset"			: dict(type=(int, float)),
	"openTypeOS2StrikeoutSize"				: dict(type=(int, float)),
	"openTypeOS2StrikeoutPosition"			: dict(type=(int, float)),
	"openTypeVheaVertTypoAscender"			: dict(type=(int, float)),
	"openTypeVheaVertTypoDescender"			: dict(type=(int, float)),
	"openTypeVheaVertTypoLineGap"			: dict(type=(int, float)),
	"openTypeVheaCaretSlopeRise"			: dict(type=int),
	"openTypeVheaCaretSlopeRun"				: dict(type=int),
	"openTypeVheaCaretOffset"				: dict(type=(int, float)),
	"postscriptFontName"					: dict(type=(str, unicode)),
	"postscriptFullName"					: dict(type=(str, unicode)),
	"postscriptSlantAngle"					: dict(type=(float, int)),
	"postscriptUniqueID"					: dict(type=int),
	"postscriptUnderlineThickness"			: dict(type=(int, float)),
	"postscriptUnderlinePosition"			: dict(type=(int, float)),
	"postscriptIsFixedPitch"				: dict(type=bool),
	"postscriptBlueValues"					: dict(type="integerList", valueValidator=_fontInfoVersion2PostscriptBluesValidator),
	"postscriptOtherBlues"					: dict(type="integerList", valueValidator=_fontInfoVersion2PostscriptOtherBluesValidator),
	"postscriptFamilyBlues"					: dict(type="integerList", valueValidator=_fontInfoVersion2PostscriptBluesValidator),
	"postscriptFamilyOtherBlues"			: dict(type="integerList", valueValidator=_fontInfoVersion2PostscriptOtherBluesValidator),
	"postscriptStemSnapH"					: dict(type="integerList", valueValidator=_fontInfoVersion2PostscriptStemsValidator),
	"postscriptStemSnapV"					: dict(type="integerList", valueValidator=_fontInfoVersion2PostscriptStemsValidator),
	"postscriptBlueFuzz"					: dict(type=(int, float)),
	"postscriptBlueShift"					: dict(type=(int, float)),
	"postscriptBlueScale"					: dict(type=(float, int)),
	"postscriptForceBold"					: dict(type=bool),
	"postscriptDefaultWidthX"				: dict(type=(int, float)),
	"postscriptNominalWidthX"				: dict(type=(int, float)),
	"postscriptWeightName"					: dict(type=(str, unicode)),
	"postscriptDefaultCharacter"			: dict(type=(str, unicode)),
	"postscriptWindowsCharacterSet"			: dict(type=int, valueValidator=_fontInfoVersion2PostscriptWindowsCharacterSetValidator),
	"macintoshFONDFamilyID"					: dict(type=int),
	"macintoshFONDName"						: dict(type=(str, unicode)),
}
fontInfoAttributesVersion2 = set(_fontInfoAttributesVersion2ValueData.keys())

# insert the type validator for all attrs that
# have no defined validator.
for attr, dataDict in _fontInfoAttributesVersion2ValueData.items():
	if "valueValidator" not in dataDict:
		dataDict["valueValidator"] = _fontInfoTypeValidator

# Version Conversion Support
# These are used from converting from version 1
# to version 2 or vice-versa.

def _flipDict(d):
	flipped = {}
	for key, value in d.items():
		flipped[value] = key
	return flipped

_fontInfoAttributesVersion1To2 = {
	"menuName"		: "styleMapFamilyName",
	"designer"		: "openTypeNameDesigner",
	"designerURL"	: "openTypeNameDesignerURL",
	"createdBy"		: "openTypeNameManufacturer",
	"vendorURL"		: "openTypeNameManufacturerURL",
	"license"		: "openTypeNameLicense",
	"licenseURL"	: "openTypeNameLicenseURL",
	"ttVersion"		: "openTypeNameVersion",
	"ttUniqueID"	: "openTypeNameUniqueID",
	"notice"		: "openTypeNameDescription",
	"otFamilyName"	: "openTypeNamePreferredFamilyName",
	"otStyleName"	: "openTypeNamePreferredSubfamilyName",
	"otMacName"		: "openTypeNameCompatibleFullName",
	"weightName"	: "postscriptWeightName",
	"weightValue"	: "openTypeOS2WeightClass",
	"ttVendor"		: "openTypeOS2VendorID",
	"uniqueID"		: "postscriptUniqueID",
	"fontName"		: "postscriptFontName",
	"fondID"		: "macintoshFONDFamilyID",
	"fondName"		: "macintoshFONDName",
	"defaultWidth"	: "postscriptDefaultWidthX",
	"slantAngle"	: "postscriptSlantAngle",
	"fullName"		: "postscriptFullName",
	# require special value conversion
	"fontStyle"		: "styleMapStyleName",
	"widthName"		: "openTypeOS2WidthClass",
	"msCharSet"		: "postscriptWindowsCharacterSet"
}
_fontInfoAttributesVersion2To1 = _flipDict(_fontInfoAttributesVersion1To2)
deprecatedFontInfoAttributesVersion2 = set(_fontInfoAttributesVersion1To2.keys())

_fontStyle1To2 = {
	64 : "regular",
	1  : "italic",
	32 : "bold",
	33 : "bold italic"
}
_fontStyle2To1 = _flipDict(_fontStyle1To2)
# Some UFO 1 files have 0
_fontStyle1To2[0] = "regular"

_widthName1To2 = {
	"Ultra-condensed" : 1,
	"Extra-condensed" : 2,
	"Condensed"		  : 3,
	"Semi-condensed"  : 4,
	"Medium (normal)" : 5,
	"Semi-expanded"	  : 6,
	"Expanded"		  : 7,
	"Extra-expanded"  : 8,
	"Ultra-expanded"  : 9
}
_widthName2To1 = _flipDict(_widthName1To2)
# FontLab's default width value is "Normal".
# Many format version 1 UFOs will have this.
_widthName1To2["Normal"] = 5
# FontLab has an "All" width value. In UFO 1
# move this up to "Normal".
_widthName1To2["All"] = 5
# "medium" appears in a lot of UFO 1 files.
_widthName1To2["medium"] = 5
# "Medium" appears in a lot of UFO 1 files.
_widthName1To2["Medium"] = 5

_msCharSet1To2 = {
	0	: 1,
	1	: 2,
	2	: 3,
	77	: 4,
	128 : 5,
	129 : 6,
	130 : 7,
	134 : 8,
	136 : 9,
	161 : 10,
	162 : 11,
	163 : 12,
	177 : 13,
	178 : 14,
	186 : 15,
	200 : 16,
	204 : 17,
	222 : 18,
	238 : 19,
	255 : 20
}
_msCharSet2To1 = _flipDict(_msCharSet1To2)

def convertFontInfoValueForAttributeFromVersion1ToVersion2(attr, value):
	"""
	Convert value from version 1 to version 2 format.
	Returns the new attribute name and the converted value.
	If the value is None, None will be returned for the new value.
	"""
	# convert floats to ints if possible
	if isinstance(value, float):
		if int(value) == value:
			value = int(value)
	if value is not None:
		if attr == "fontStyle":
			v = _fontStyle1To2.get(value)
			if v is None:
				raise UFOLibError("Cannot convert value (%s) for attribute %s." % (repr(value), attr))
			value = v
		elif attr == "widthName":
			v = _widthName1To2.get(value)
			if v is None:
				raise UFOLibError("Cannot convert value (%s) for attribute %s." % (repr(value), attr))
			value = v
		elif attr == "msCharSet":
			v = _msCharSet1To2.get(value)
			if v is None:
				raise UFOLibError("Cannot convert value (%s) for attribute %s." % (repr(value), attr))
			value = v
	attr = _fontInfoAttributesVersion1To2.get(attr, attr)
	return attr, value

def convertFontInfoValueForAttributeFromVersion2ToVersion1(attr, value):
	"""
	Convert value from version 2 to version 1 format.
	Returns the new attribute name and the converted value.
	If the value is None, None will be returned for the new value.
	"""
	if value is not None:
		if attr == "styleMapStyleName":
			value = _fontStyle2To1.get(value)
		elif attr == "openTypeOS2WidthClass":
			value = _widthName2To1.get(value)
		elif attr == "postscriptWindowsCharacterSet":
			value = _msCharSet2To1.get(value)
	attr = _fontInfoAttributesVersion2To1.get(attr, attr)
	return attr, value

def _convertFontInfoDataVersion1ToVersion2(data):
	converted = {}
	for attr, value in data.items():
		# FontLab gives -1 for the weightValue
		# for fonts wil no defined value. Many
		# format version 1 UFOs will have this.
		if attr == "weightValue" and value == -1:
			continue
		newAttr, newValue = convertFontInfoValueForAttributeFromVersion1ToVersion2(attr, value)
		# skip if the attribute is not part of version 2
		if newAttr not in fontInfoAttributesVersion2:
			continue
		# catch values that can't be converted
		if value is None:
			raise UFOLibError("Cannot convert value (%s) for attribute %s." % (repr(value), newAttr))
		# store
		converted[newAttr] = newValue
	return converted

def _convertFontInfoDataVersion2ToVersion1(data):
	converted = {}
	for attr, value in data.items():
		newAttr, newValue = convertFontInfoValueForAttributeFromVersion2ToVersion1(attr, value)
		# only take attributes that are registered for version 1
		if newAttr not in fontInfoAttributesVersion1:
			continue
		# catch values that can't be converted
		if value is None:
			raise UFOLibError("Cannot convert value (%s) for attribute %s." % (repr(value), newAttr))
		# store
		converted[newAttr] = newValue
	return converted


if __name__ == "__main__":
	import doctest
	doctest.testmod()
