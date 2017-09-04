# -*- coding: utf-8 -*-
"""glifLib.py -- Generic module for reading and writing the .glif format.

More info about the .glif format (GLyphInterchangeFormat) can be found here:

	http://unifiedfontobject.org

The main class in this module is GlyphSet. It manages a set of .glif files
in a folder. It offers two ways to read glyph data, and one way to write
glyph data. See the class doc string for details.
"""

__all__ = ["GlyphSet", "GlifLibError",
		"readGlyphFromString", "writeGlyphToString",
		"glyphNameToFileName"]

import os
from robofab.xmlTreeBuilder import buildTree, stripCharacterData
from robofab.pens.pointPen import AbstractPointPen
from cStringIO import StringIO


class GlifLibError(Exception): pass


if os.name == "mac":
	WRITE_MODE = "wb"  # use unix line endings, even with Classic MacPython
	READ_MODE = "rb"
else:
	WRITE_MODE = "w"
	READ_MODE = "r"


class Glyph:

	"""Minimal glyph object. It has no glyph attributes until either
	the draw() or the drawPoint() method has been called.
	"""

	def __init__(self, glyphName, glyphSet):
		self.glyphName = glyphName
		self.glyphSet = glyphSet

	def draw(self, pen):
		"""Draw this glyph onto a *FontTools* Pen."""
		from robofab.pens.adapterPens import PointToSegmentPen
		pointPen = PointToSegmentPen(pen)
		self.drawPoints(pointPen)

	def drawPoints(self, pointPen):
		"""Draw this glyph onto a PointPen."""
		self.glyphSet.readGlyph(self.glyphName, self, pointPen)


def glyphNameToFileName(glyphName, glyphSet):
	"""Default algorithm for making a file name out of a glyph name.
	This one has limited support for case insensitive file systems:
	it assumes glyph names are not case sensitive apart from the first
	character:
		'a'     -> 'a.glif'
		'A'     -> 'A_.glif'
		'A.alt' -> 'A_.alt.glif'
		'A.Alt' -> 'A_.Alt.glif'
		'T_H'   -> 'T__H_.glif'
		'T_h'   -> 'T__h.glif'
		't_h'   -> 't_h.glif'
		'F_F_I' -> 'F__F__I_.glif'
		'f_f_i' -> 'f_f_i.glif'

	"""
	if glyphName.startswith("."):
		# some OSes consider filenames such as .notdef "hidden"
		glyphName = "_" + glyphName[1:]
	parts = glyphName.split(".")
	if parts[0].find("_")!=-1:
		# it is a compound name, check the separate parts
		bits = []
		for p in parts[0].split("_"):
			if p != p.lower():
				bits.append(p+"_")
				continue
			bits.append(p)
		parts[0] = "_".join(bits)
	else:
		# it is a single name
		if parts[0] != parts[0].lower():
			parts[0] += "_"
	for i in range(1, len(parts)):
		# resolve additional, period separated parts, like alt / Alt
		if parts[i] != parts[i].lower():
			parts[i] += "_"
	return ".".join(parts) + ".glif"


class GlyphSet:

	"""GlyphSet manages a set of .glif files inside one directory.

	GlyphSet's constructor takes a path to an existing directory as it's
	first argument. Reading glyph data can either be done through the
	readGlyph() method, or by using GlyphSet's dictionary interface, where
	the keys are glyph names and the values are (very) simple glyph objects.

	To write a glyph to the glyph set, you use the writeGlyph() method.
	The simple glyph objects returned through the dict interface do not
	support writing, they are just a convenient way to get at the glyph data.
	"""

	glyphClass = Glyph

	def __init__(self, dirName, glyphNameToFileNameFunc=None):
		"""'dirName' should be a path to an existing directory.

		The optional 'glyphNameToFileNameFunc' argument must be a callback
		function that takes two arguments: a glyph name and the GlyphSet
		instance. It should return a file name (including the .glif
		extension). The glyphNameToFileName function is called whenever
		a file name is created for a given glyph name.
		"""
		self.dirName = dirName
		if glyphNameToFileNameFunc is None:
			glyphNameToFileNameFunc = glyphNameToFileName
		self.glyphNameToFileName = glyphNameToFileNameFunc
		self.contents = self._findContents()
		self._reverseContents = None
		self._glifCache = {}

	def rebuildContents(self):
		"""Rebuild the contents dict by checking what glyphs are available
		on disk.
		"""
		self.contents = self._findContents(forceRebuild=True)
		self._reverseContents = None

	def getReverseContents(self):
		"""Return a reversed dict of self.contents, mapping file names to
		glyph names. This is primarily an aid for custom glyph name to file
		name schemes that want to make sure they don't generate duplicate
		file names. The file names are converted to lowercase so we can
		reliably check for duplicates that only differ in case, which is
		important for case-insensitive file systems.
		"""
		if self._reverseContents is None:
			d = {}
			for k, v in self.contents.iteritems():
				d[v.lower()] = k
			self._reverseContents = d
		return self._reverseContents

	def writeContents(self):
		"""Write the contents.plist file out to disk. Call this method when
		you're done writing glyphs.
		"""
		from plistlib import writePlistToString
		contentsPath = os.path.join(self.dirName, "contents.plist")
		# We need to force Unix line endings, even in OS9 MacPython in FL,
		# so we do the writing to file ourselves.
		plist = writePlistToString(self.contents)
		f = open(contentsPath, WRITE_MODE)
		f.write(plist)
		f.close()

	# read caching

	def getGLIF(self, glyphName):
		"""Get the raw GLIF text for a given glyph name. This only works
		for GLIF files that are already on disk.

		This method is useful in situations when the raw XML needs to be
		read from a glyph set for a particular glyph before fully parsing
		it into an object structure via the readGlyph method.

		Internally, this method will load a GLIF the first time it is
		called and then cache it. The next time this method is called
		the GLIF will be pulled from the cache if the file's modification
		time has not changed since the GLIF was cached. For memory
		efficiency, the cached GLIF will be purged by various other methods
		such as readGlyph.
		"""
		needRead = False
		fileName = self.contents.get(glyphName)
		path = None
		if fileName is not None:
			path = os.path.join(self.dirName, fileName)
		if glyphName not in self._glifCache:
			needRead = True
		elif fileName is not None and os.path.getmtime(path) != self._glifCache[glyphName][1]:
			needRead = True
		if needRead:
			fileName = self.contents[glyphName]
			if not os.path.exists(path):
				raise KeyError, glyphName
			f = open(path, "rb")
			text = f.read()
			f.close()
			self._glifCache[glyphName] = (text, os.path.getmtime(path))
		return self._glifCache[glyphName][0]

	def _purgeCachedGLIF(self, glyphName):
		if glyphName in self._glifCache:
			del self._glifCache[glyphName]

	# reading/writing API

	def readGlyph(self, glyphName, glyphObject=None, pointPen=None):
		"""Read a .glif file for 'glyphName' from the glyph set. The
		'glyphObject' argument can be any kind of object (even None);
		the readGlyph() method will attempt to set the following
		attributes on it:
			"width"     the advance with of the glyph
			"unicodes"  a list of unicode values for this glyph
			"note"      a string
			"lib"       a dictionary containing custom data

		All attributes are optional, in two ways:
			1) An attribute *won't* be set if the .glif file doesn't
			   contain data for it. 'glyphObject' will have to deal
			   with default values itself.
			2) If setting the attribute fails with an AttributeError
			   (for example if the 'glyphObject' attribute is read-
			   only), readGlyph() will not propagate that exception,
			   but ignore that attribute.

		To retrieve outline information, you need to pass an object
		conforming to the PointPen protocol as the 'pointPen' argument.
		This argument may be None if you don't need the outline data.

		readGlyph() will raise KeyError if the glyph is not present in
		the glyph set.
		"""
		text = self.getGLIF(glyphName)
		self._purgeCachedGLIF(glyphName)
		tree = _glifTreeFromFile(StringIO(text))
		_readGlyphFromTree(tree, glyphObject, pointPen)

	def writeGlyph(self, glyphName, glyphObject=None, drawPointsFunc=None):
		"""Write a .glif file for 'glyphName' to the glyph set. The
		'glyphObject' argument can be any kind of object (even None);
		the writeGlyph() method will attempt to get the following
		attributes from it:
			"width"     the advance with of the glyph
			"unicodes"  a list of unicode values for this glyph
			"note"      a string
			"lib"       a dictionary containing custom data

		All attributes are optional: if 'glyphObject' doesn't
		have the attribute, it will simply be skipped.

		To write outline data to the .glif file, writeGlyph() needs
		a function (any callable object actually) that will take one
		argument: an object that conforms to the PointPen protocol.
		The function will be called by writeGlyph(); it has to call the
		proper PointPen methods to transfer the outline to the .glif file.
		"""
		self._purgeCachedGLIF(glyphName)
		data = writeGlyphToString(glyphName, glyphObject, drawPointsFunc)
		fileName = self.contents.get(glyphName)
		if fileName is None:
			fileName = self.glyphNameToFileName(glyphName, self)
			self.contents[glyphName] = fileName
			if self._reverseContents is not None:
				self._reverseContents[fileName.lower()] = glyphName
		path = os.path.join(self.dirName, fileName)
		if os.path.exists(path):
			f = open(path, READ_MODE)
			oldData = f.read()
			f.close()
			if data == oldData:
				return
		f = open(path, WRITE_MODE)
		f.write(data)
		f.close()

	def deleteGlyph(self, glyphName):
		"""Permanently delete the glyph from the glyph set on disk. Will
		raise KeyError if the glyph is not present in the glyph set.
		"""
		self._purgeCachedGLIF(glyphName)
		fileName = self.contents[glyphName]
		os.remove(os.path.join(self.dirName, fileName))
		if self._reverseContents is not None:
			del self._reverseContents[self.contents[glyphName].lower()]
		del self.contents[glyphName]

	# dict-like support

	def keys(self):
		return self.contents.keys()

	def has_key(self, glyphName):
		return glyphName in self.contents

	__contains__ = has_key

	def __len__(self):
		return len(self.contents)

	def __getitem__(self, glyphName):
		if glyphName not in self.contents:
			raise KeyError, glyphName
		return self.glyphClass(glyphName, self)

	# quickly fetching unicode values

	def getUnicodes(self):
		"""Return a dictionary that maps all glyph names to lists containing
		the unicode value[s] for that glyph, if any. This parses the .glif
		files partially, so is a lot faster than parsing all files completely.
		"""
		unicodes = {}
		for glyphName in self.contents.keys():
			text = self.getGLIF(glyphName)
			unicodes[glyphName] = _fetchUnicodes(text)
		return unicodes

	# internal methods

	def _findContents(self, forceRebuild=False):
		contentsPath = os.path.join(self.dirName, "contents.plist")
		if forceRebuild or not os.path.exists(contentsPath):
			fileNames = os.listdir(self.dirName)
			fileNames = [n for n in fileNames if n.endswith(".glif")]
			contents = {}
			for n in fileNames:
				glyphPath = os.path.join(self.dirName, n)
				contents[_fetchGlyphName(glyphPath)] = n
		else:
			from plistlib import readPlist
			contents = readPlist(contentsPath)
		return contents


def readGlyphFromString(aString, glyphObject=None, pointPen=None):
	"""Read .glif data from a string into a glyph object.

	The 'glyphObject' argument can be any kind of object (even None);
	the readGlyphFromString() method will attempt to set the following
	attributes on it:
		"width"     the advance with of the glyph
		"unicodes"  a list of unicode values for this glyph
		"note"      a string
		"lib"       a dictionary containing custom data

	All attributes are optional, in two ways:
		1) An attribute *won't* be set if the .glif file doesn't
		   contain data for it. 'glyphObject' will have to deal
		   with default values itself.
		2) If setting the attribute fails with an AttributeError
		   (for example if the 'glyphObject' attribute is read-
		   only), readGlyphFromString() will not propagate that
		   exception, but ignore that attribute.

	To retrieve outline information, you need to pass an object
	conforming to the PointPen protocol as the 'pointPen' argument.
	This argument may be None if you don't need the outline data.
	"""
	tree = _glifTreeFromFile(StringIO(aString))
	_readGlyphFromTree(tree, glyphObject, pointPen)


def writeGlyphToString(glyphName, glyphObject=None, drawPointsFunc=None, writer=None):
	"""Return .glif data for a glyph as a UTF-8 encoded string.
	The 'glyphObject' argument can be any kind of object (even None);
	the writeGlyphToString() method will attempt to get the following
	attributes from it:
		"width"     the advance with of the glyph
		"unicodes"  a list of unicode values for this glyph
		"note"      a string
		"lib"       a dictionary containing custom data

	All attributes are optional: if 'glyphObject' doesn't
	have the attribute, it will simply be skipped.

	To write outline data to the .glif file, writeGlyphToString() needs
	a function (any callable object actually) that will take one
	argument: an object that conforms to the PointPen protocol.
	The function will be called by writeGlyphToString(); it has to call the
	proper PointPen methods to transfer the outline to the .glif file.
	"""
	if writer is None:
		try:
			from xmlWriter import XMLWriter
		except ImportError:
			# try the other location
			from fontTools.misc.xmlWriter import XMLWriter
		aFile = StringIO()
		writer = XMLWriter(aFile, encoding="UTF-8")
	else:
		aFile = None
	writer.begintag("glyph", [("name", glyphName), ("format", "1")])
	writer.newline()

	width = getattr(glyphObject, "width", None)
	if width is not None:
		if not isinstance(width, (int, float)):
			raise GlifLibError, "width attribute must be int or float"
		writer.simpletag("advance", width=repr(width))
		writer.newline()

	unicodes = getattr(glyphObject, "unicodes", None)
	if unicodes:
		if isinstance(unicodes, int):
			unicodes = [unicodes]
		for code in unicodes:
			if not isinstance(code, int):
				raise GlifLibError, "unicode values must be int"
			hexCode = hex(code)[2:].upper()
			if len(hexCode) < 4:
				hexCode = "0" * (4 - len(hexCode)) + hexCode
			writer.simpletag("unicode", hex=hexCode)
			writer.newline()

	note = getattr(glyphObject, "note", None)
	if note is not None:
		if not isinstance(note, (str, unicode)):
			raise GlifLibError, "note attribute must be str or unicode"
		note = note.encode('utf-8')
		writer.begintag("note")
		writer.newline()
		for line in note.splitlines():
			writer.write(line.strip())
			writer.newline()
		writer.endtag("note")
		writer.newline()

	if drawPointsFunc is not None:
		writer.begintag("outline")
		writer.newline()
		pen = GLIFPointPen(writer)
		drawPointsFunc(pen)
		writer.endtag("outline")
		writer.newline()

	lib = getattr(glyphObject, "lib", None)
	if lib:
		from robofab.plistlib import PlistWriter
		if not isinstance(lib, dict):
			lib = dict(lib)
		writer.begintag("lib")
		writer.newline()
		plistWriter = PlistWriter(writer.file, indentLevel=writer.indentlevel,
				indent=writer.indentwhite, writeHeader=False)
		plistWriter.writeValue(lib)
		writer.endtag("lib")
		writer.newline()

	writer.endtag("glyph")
	writer.newline()
	if aFile is not None:
		return aFile.getvalue()
	else:
		return None


# misc helper functions

def _stripGlyphXMLTree(nodes):
	for element, attrs, children in nodes:
		# "lib" is formatted as a plist, so we need unstripped
		# character data so we can support strings with leading or
		# trailing whitespace. Do strip everything else.
		recursive = (element != "lib")
		stripCharacterData(children, recursive=recursive)


def _glifTreeFromFile(aFile):
	tree = buildTree(aFile, stripData=False)
	stripCharacterData(tree[2], recursive=False)
	assert tree[0] == "glyph"
	_stripGlyphXMLTree(tree[2])
	return tree


def _relaxedSetattr(object, attr, value):
	try:
		setattr(object, attr, value)
	except AttributeError:
		pass


def _number(s):
	"""Given a numeric string, return an integer or a float, whichever
	the string indicates. _number("1") will return the integer 1,
	_number("1.0") will return the float 1.0.
	"""
	try:
		n = int(s)
	except ValueError:
		n = float(s)
	return n



def _readGlyphFromTree(tree, glyphObject=None, pointPen=None):
	unicodes = []
	assert tree[0] == "glyph"
	formatVersion = int(tree[1].get("format", "0"))
	if formatVersion not in (0, 1):
		raise GlifLibError, "unsupported glif format version: %s" % formatVersion
	glyphName = tree[1].get("name")
	if glyphName and glyphObject is not None:
		_relaxedSetattr(glyphObject, "name", glyphName)
	for element, attrs, children in tree[2]:
		if element == "outline":
			if pointPen is not None:
				if formatVersion == 0:
					buildOutline_Format0(pointPen, children)
				else:
					buildOutline_Format1(pointPen, children)
		elif glyphObject is None:
			continue
		elif element == "advance":
			width = _number(attrs["width"])
			_relaxedSetattr(glyphObject, "width", width)
		elif element == "unicode":
			unicodes.append(int(attrs["hex"], 16))
		elif element == "note":
			rawNote = "\n".join(children)
			lines = rawNote.split("\n")
			lines = [line.strip() for line in lines]
			note = "\n".join(lines)
			_relaxedSetattr(glyphObject, "note", note)
		elif element == "lib":
			from plistFromTree import readPlistFromTree
			assert len(children) == 1
			lib = readPlistFromTree(children[0])
			_relaxedSetattr(glyphObject, "lib", lib)
	if unicodes:
		_relaxedSetattr(glyphObject, "unicodes", unicodes)


class _DoneParsing(Exception): pass

def _startElementHandler(tagName, attrs):
	if tagName != "glyph":
		# the top level element of any .glif file must be <glyph>
		raise _DoneParsing(None)
	glyphName = attrs["name"]
	raise _DoneParsing(glyphName)

def _fetchGlyphName(glyphPath):
	# Given a path to an existing .glif file, get the glyph name
	# from the XML data.
	from xml.parsers.expat import ParserCreate

	p = ParserCreate()
	p.StartElementHandler = _startElementHandler
	p.returns_unicode = True
	f = open(glyphPath)
	try:
		p.ParseFile(f)
	except _DoneParsing, why:
		glyphName = why.args[0]
		if glyphName is None:
			raise ValueError, (".glif file doen't have a <glyph> top-level "
					"element: %r" % glyphPath)
	else:
		assert 0, "it's not expected that parsing the file ends normally"
	return glyphName


def _fetchUnicodes(text):
	# Given GLIF text, get a list of all unicode values from the XML data.
	parser = _FetchUnicodesParser(text)
	return parser.unicodes

class _FetchUnicodesParser(object):

	def __init__(self, text):
		from xml.parsers.expat import ParserCreate
		self.unicodes = []
		self._elementStack = []
		parser = ParserCreate()
		parser.returns_unicode = 0  # XXX, Don't remember why. It sucks, though.
		parser.StartElementHandler = self.startElementHandler
		parser.EndElementHandler = self.endElementHandler
		parser.Parse(text)

	def startElementHandler(self, name, attrs):
		if name == "unicode" and len(self._elementStack) == 1 and self._elementStack[0] == "glyph":
			value = attrs.get("hex")
			value = int(value, 16)
			self.unicodes.append(value)
		self._elementStack.append(name)

	def endElementHandler(self, name):
		other = self._elementStack.pop(-1)
		assert other == name


def buildOutline_Format0(pen, xmlNodes):
	# This reads the "old" .glif format, retroactively named "format 0",
	# later formats have a "format" attribute in the <glyph> element.
	for element, attrs, children in xmlNodes:
		if element == "contour":
			pen.beginPath()
			currentSegmentType = None
			for subElement, attrs, dummy in children:
				if subElement != "point":
					continue
				x = _number(attrs["x"])
				y = _number(attrs["y"])
				pointType = attrs.get("type", "onCurve")
				if pointType == "bcp":
					currentSegmentType = "curve"
				elif pointType == "offCurve":
					currentSegmentType = "qcurve"
				elif currentSegmentType is None and pointType == "onCurve":
					currentSegmentType = "line"
				if pointType == "onCurve":
					segmentType = currentSegmentType
					currentSegmentType = None
				else:
					segmentType = None
				smooth = attrs.get("smooth") == "yes"
				pen.addPoint((x, y), segmentType=segmentType, smooth=smooth)
			pen.endPath()
		elif element == "component":
			baseGlyphName = attrs["base"]
			transformation = []
			for attr, default in _transformationInfo:
				value = attrs.get(attr)
				if value is None:
					value = default
				else:
					value = _number(value)
				transformation.append(value)
			pen.addComponent(baseGlyphName, tuple(transformation))
		elif element == "anchor":
			name, x, y = attrs["name"], _number(attrs["x"]), _number(attrs["y"])
			pen.beginPath()
			pen.addPoint((x, y), segmentType="move", name=name)
			pen.endPath()


def buildOutline_Format1(pen, xmlNodes):
	for element, attrs, children in xmlNodes:
		if element == "contour":
			pen.beginPath()
			for subElement, attrs, dummy in children:
				if subElement != "point":
					continue
				x = _number(attrs["x"])
				y = _number(attrs["y"])
				segmentType = attrs.get("type", "offcurve")
				if segmentType == "offcurve":
					segmentType = None
				smooth = attrs.get("smooth") == "yes"
				name = attrs.get("name")
				pen.addPoint((x, y), segmentType=segmentType, smooth=smooth, name=name)
			pen.endPath()
		elif element == "component":
			baseGlyphName = attrs["base"]
			transformation = []
			for attr, default in _transformationInfo:
				value = attrs.get(attr)
				if value is None:
					value = default
				else:
					value = _number(value)
				transformation.append(value)
			pen.addComponent(baseGlyphName, tuple(transformation))


_transformationInfo = [
	# field name, default value
	("xScale",    1),
	("xyScale",   0),
	("yxScale",   0),
	("yScale",    1),
	("xOffset",   0),
	("yOffset",   0),
]

class GLIFPointPen(AbstractPointPen):

	"""Helper class using the PointPen protocol to write the <outline>
	part of .glif files.
	"""

	def __init__(self, xmlWriter):
		self.writer = xmlWriter

	def beginPath(self):
		self.writer.begintag("contour")
		self.writer.newline()

	def endPath(self):
		self.writer.endtag("contour")
		self.writer.newline()

	def addPoint(self, pt, segmentType=None, smooth=None, name=None, **kwargs):
		attrs = []
		if pt is not None:
			for coord in pt:
				if not isinstance(coord, (int, float)):
					raise GlifLibError, "coordinates must be int or float"
			attrs.append(("x", repr(pt[0])))
			attrs.append(("y", repr(pt[1])))
		if segmentType is not None:
			attrs.append(("type", segmentType))
		if smooth:
			attrs.append(("smooth", "yes"))
		if name is not None:
			attrs.append(("name", name))
		self.writer.simpletag("point", attrs)
		self.writer.newline()

	def addComponent(self, glyphName, transformation):
		attrs = [("base", glyphName)]
		for (attr, default), value in zip(_transformationInfo, transformation):
			if not isinstance(value, (int, float)):
				raise GlifLibError, "transformation values must be int or float"
			if value != default:
				attrs.append((attr, repr(value)))
		self.writer.simpletag("component", attrs)
		self.writer.newline()


if __name__ == "__main__":
	from pprint import pprint
	from robofab.pens.pointPen import PrintingPointPen
	class TestGlyph: pass
	gs = GlyphSet(".")
	def drawPoints(pen):
		pen.beginPath()
		pen.addPoint((100, 200), name="foo")
		pen.addPoint((200, 250), segmentType="curve", smooth=True)
		pen.endPath()
		pen.addComponent("a", (1, 0, 0, 1, 20, 30))
	glyph = TestGlyph()
	glyph.width = 120
	glyph.unicodes = [1, 2, 3, 43215, 66666]
	glyph.lib = {"a": "b", "c": [1, 2, 3, True]}
	glyph.note = "  hallo!   "
	if 0:
		gs.writeGlyph("a", glyph, drawPoints)
		g2 = TestGlyph()
		gs.readGlyph("a", g2, PrintingPointPen())
		pprint(g2.__dict__)
	else:
		s = writeGlyphToString("a", glyph, drawPoints)
		print s
		g2 = TestGlyph()
		readGlyphFromString(s, g2, PrintingPointPen())
		pprint(g2.__dict__)

