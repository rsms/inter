""" 
Base classes for the Unified Font Objects (UFO),
a series of classes that deal with fonts, glyphs,
contours and related things.

Unified Font Objects are:
- platform independent
- application independent

About Object Inheritance:
objectsFL and objectsRF objects inherit
methods and attributes from these objects.
In other words, if it is in here, you can
do it with the objectsFL and objectsRF.
"""


from __future__ import generators
from __future__ import division

from warnings import warn
import math
import copy

from robofab import ufoLib
from robofab import RoboFabError
from robofab.misc.arrayTools import updateBounds, pointInRect, unionRect, sectRect
from fontTools.pens.basePen import AbstractPen
from fontTools.pens.areaPen import AreaPen
from ..exceptions import RoboFabError, RoboFabWarning

try:
	set
except NameError:
	from sets import Set as set

#constants for dealing with segments, points and bPoints
MOVE = 'move'
LINE = 'line'
CORNER = 'corner'
CURVE = 'curve'
QCURVE = 'qcurve'
OFFCURVE = 'offcurve'

DEGREE = 180 / math.pi



# the key for the postscript hint data stored in the UFO
postScriptHintDataLibKey = "org.robofab.postScriptHintData"

# from http://svn.typesupply.com/packages/fontMath/mathFunctions.py

def add(v1, v2):
	return v1 + v2

def sub(v1, v2):
	return v1 - v2

def mul(v, f):
	return v * f

def div(v, f):
	return v / f
	
def issequence(x):
	"Is x a sequence? We say it is if it has a __getitem__ method."
	return hasattr(x, '__getitem__')



class BasePostScriptHintValues(object):
	""" Base class for postscript hinting information.
	"""
		
	def __init__(self, data=None):
		if data is not None:
			self.fromDict(data)
		else:
			for name in self._attributeNames.keys():
				setattr(self, name, self._attributeNames[name]['default'])
		
	def getParent(self):
		"""this method will be overwritten with a weakref if there is a parent."""
		return None

	def setParent(self, parent):
		import weakref
		self.getParent = weakref.ref(parent)
		
	def isEmpty(self):
		"""Check all attrs and decide if they're all empty."""
		empty = True
		for name in self._attributeNames:
			if getattr(self, name):
				empty = False
				break
		return empty

	def clear(self):
		"""Set all attributes to default / empty"""
		for name in self._attributeNames:
			setattr(self, name, self._attributeNames[name]['default'])
		
	def _loadFromLib(self, lib):
		data = lib.get(postScriptHintDataLibKey)
		if data is not None:
			self.fromDict(data)

	def _saveToLib(self, lib):
		parent = self.getParent()
		if parent is not None:
			parent.setChanged(True)
		hintsDict = self.asDict()
		if hintsDict:
				lib[postScriptHintDataLibKey] = hintsDict

	def fromDict(self, data):
		for name in self._attributeNames:
			if name in data:
				setattr(self, name, data[name])
	
	def asDict(self):
		d = {}
		for name in self._attributeNames:
			try:
				value = getattr(self, name)
			except AttributeError:
				print "%s attribute not supported"%name
				continue
			if value:
				d[name] = getattr(self, name)
		return d
	
	def update(self, other):
		assert isinstance(other, BasePostScriptHintValues)
		for name in self._attributeNames.keys():
			v = getattr(other, name)
			if v is not None:
				setattr(self, name, v)
	
	def __repr__(self):
		return "<Base PS Hint Data>"

	def copy(self, aParent=None):
		"""Duplicate this object. Pass an object for parenting if you want."""
		n = self.__class__(data=self.asDict())
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		dont = ['getParent']
		for k in self.__dict__.keys():
			if k in dont:
				continue
			dup = copy.deepcopy(self.__dict__[k])
			setattr(n, k, dup)
		return n

class BasePostScriptGlyphHintValues(BasePostScriptHintValues):
	""" Base class for glyph-level postscript hinting information.
		vStems, hStems
	"""
	_attributeNames = {
		# some of these values can have only a certain number of elements
		'vHints':		{'default': None, 'max':100, 'isVertical':True},
		'hHints':		{'default': None, 'max':100, 'isVertical':False},
		}
		
	def __init__(self, data=None):
		if data is not None:
			self.fromDict(data)
		else:
			for name in self._attributeNames.keys():
				setattr(self, name, self._attributeNames[name]['default'])

	def __repr__(self):
		return "<PostScript Glyph Hints Values>"

	def round(self):
		"""Round the values to reasonable values.
			- stems are rounded to int
		"""
		for name, values in self._attributeNames.items():
			v = getattr(self, name)
			if v is None:
				continue
			new = []
			for n in v:
				new.append((int(round(n[0])), int(round(n[1]))))
			setattr(self, name, new)

	# math operations for psHint object
	# Note: math operations can change integers to floats.
	def __add__(self, other):
		assert isinstance(other, BasePostScriptHintValues)
		copied = self.copy()
		self._processMathOne(copied, other, add)
		return copied

	def __sub__(self, other):
		assert isinstance(other, BasePostScriptHintValues)
		copied = self.copy()
		self._processMathOne(copied, other, sub)
		return copied

	def __mul__(self, factor):
		#if isinstance(factor, tuple):
		#	factor = factor[0]
		copiedInfo = self.copy()
		self._processMathTwo(copiedInfo, factor, mul)
		return copiedInfo

	__rmul__ = __mul__

	def __div__(self, factor):
		#if isinstance(factor, tuple):
		#	factor = factor[0]
		copiedInfo = self.copy()
		self._processMathTwo(copiedInfo, factor, div)
		return copiedInfo

	__rdiv__ = __div__

	def _processMathOne(self, copied, other, funct):
		for name, values in self._attributeNames.items():
			a = None
			b = None
			v = None
			if hasattr(copied, name):
				a = getattr(copied, name)
			if hasattr(other, name):
				b = getattr(other, name)
			if a is not None and b is not None:
				if len(a) != len(b):
					# can't do math with non matching zones
					continue
				l = len(a)
				for i in range(l):
					if v is None:
						v = []
					ai = a[i]
					bi = b[i]
					l2 = min(len(ai), len(bi))
					v2 = [funct(ai[j], bi[j]) for j in range(l2)]
					v.append(v2)
			if v is not None:
				setattr(copied, name, v)

	def _processMathTwo(self, copied, factor, funct):
		for name, values in self._attributeNames.items():
			a = None
			b = None
			v = None
			isVertical = self._attributeNames[name]['isVertical']
			splitFactor = factor
			if isinstance(factor, tuple):
				#print "mathtwo", name, funct, factor, isVertical
				if isVertical:
					splitFactor = factor[1]
				else:
					splitFactor = factor[0]
			if hasattr(copied, name):
				a = getattr(copied, name)
			if a is not None:
				for i in range(len(a)):
					if v is None:
						v = []
					v2 = [funct(a[i][j], splitFactor) for j in range(len(a[i]))]
					v.append(v2)
			if v is not None:
				setattr(copied, name, v)
	

class BasePostScriptFontHintValues(BasePostScriptHintValues):
	""" Base class for font-level postscript hinting information.
		Blues values, stem values.
	"""
	
	_attributeNames = {
		# some of these values can have only a certain number of elements
		# 	default: what the value should be when initialised
		#	max:	the maximum number of items this attribute is allowed to have
		#	isVertical:		the vertical relevance
		'blueFuzz':		{'default': None, 'max':1, 'isVertical':True},
		'blueScale':	{'default': None, 'max':1, 'isVertical':True},
		'blueShift':	{'default': None, 'max':1, 'isVertical':True},
		'forceBold':	{'default': None, 'max':1, 'isVertical':False},
		'blueValues':	{'default': None, 'max':7, 'isVertical':True},
		'otherBlues':	{'default': None, 'max':5, 'isVertical':True},
		'familyBlues':	{'default': None, 'max':7, 'isVertical':True},
		'familyOtherBlues': {'default': None, 'max':5, 'isVertical':True},
		'vStems':		{'default': None, 'max':6, 'isVertical':True},
		'hStems':		{'default': None, 'max':11, 'isVertical':False},
		}
		
	def __init__(self, data=None):
		if data is not None:
			self.fromDict(data)

	def __repr__(self):
		return "<PostScript Font Hints Values>"

	# route attribute calls to info object

	def _bluesToPairs(self, values):
		values.sort()
		finalValues = []
		for value in values:
			if not finalValues or len(finalValues[-1]) == 2:
				finalValues.append([])
			finalValues[-1].append(value)
		return finalValues

	def _bluesFromPairs(self, values):
		finalValues = []
		for value1, value2 in values:
			finalValues.append(value1)
			finalValues.append(value2)
		finalValues.sort()
		return finalValues

	def _get_blueValues(self):
		values = self.getParent().info.postscriptBlueValues
		if values is None:
			values = []
		values = self._bluesToPairs(values)
		return values

	def _set_blueValues(self, values):
		if values is None:
			values = []
		values = self._bluesFromPairs(values)
		self.getParent().info.postscriptBlueValues = values

	blueValues = property(_get_blueValues, _set_blueValues)

	def _get_otherBlues(self):
		values = self.getParent().info.postscriptOtherBlues
		if values is None:
			values = []
		values = self._bluesToPairs(values)
		return values

	def _set_otherBlues(self, values):
		if values is None:
			values = []
		values = self._bluesFromPairs(values)
		self.getParent().info.postscriptOtherBlues = values

	otherBlues = property(_get_otherBlues, _set_otherBlues)

	def _get_familyBlues(self):
		values = self.getParent().info.postscriptFamilyBlues
		if values is None:
			values = []
		values = self._bluesToPairs(values)
		return values

	def _set_familyBlues(self, values):
		if values is None:
			values = []
		values = self._bluesFromPairs(values)
		self.getParent().info.postscriptFamilyBlues = values

	familyBlues = property(_get_familyBlues, _set_familyBlues)

	def _get_familyOtherBlues(self):
		values = self.getParent().info.postscriptFamilyOtherBlues
		if values is None:
			values = []
		values = self._bluesToPairs(values)
		return values

	def _set_familyOtherBlues(self, values):
		if values is None:
			values = []
		values = self._bluesFromPairs(values)
		self.getParent().info.postscriptFamilyOtherBlues = values

	familyOtherBlues = property(_get_familyOtherBlues, _set_familyOtherBlues)

	def _get_vStems(self):
		return self.getParent().info.postscriptStemSnapV

	def _set_vStems(self, value):
		if value is None:
			value = []
		self.getParent().info.postscriptStemSnapV = list(value)

	vStems = property(_get_vStems, _set_vStems)

	def _get_hStems(self):
		return self.getParent().info.postscriptStemSnapH

	def _set_hStems(self, value):
		if value is None:
			value = []
		self.getParent().info.postscriptStemSnapH = list(value)

	hStems = property(_get_hStems, _set_hStems)

	def _get_blueScale(self):
		return self.getParent().info.postscriptBlueScale

	def _set_blueScale(self, value):
		self.getParent().info.postscriptBlueScale = value

	blueScale = property(_get_blueScale, _set_blueScale)

	def _get_blueShift(self):
		return self.getParent().info.postscriptBlueShift

	def _set_blueShift(self, value):
		self.getParent().info.postscriptBlueShift = value

	blueShift = property(_get_blueShift, _set_blueShift)

	def _get_blueFuzz(self):
		return self.getParent().info.postscriptBlueFuzz

	def _set_blueFuzz(self, value):
		self.getParent().info.postscriptBlueFuzz = value

	blueFuzz = property(_get_blueFuzz, _set_blueFuzz)

	def _get_forceBold(self):
		return self.getParent().info.postscriptForceBold

	def _set_forceBold(self, value):
		self.getParent().info.postscriptForceBold = value

	forceBold = property(_get_forceBold, _set_forceBold)

	def round(self):
		"""Round the values to reasonable values.
			- blueScale is not rounded, it is a float
			- forceBold is set to False if -0.5 < value < 0.5. Otherwise it will be True.
			- blueShift, blueFuzz are rounded to int
			- stems are rounded to int
			- blues are rounded to int
		"""
		for name, values in self._attributeNames.items():
			if name == "blueScale":
				continue
			elif name == "forceBold":
				v = getattr(self, name)
				if v is None:
					continue
				if -0.5 <= v <= 0.5:
					setattr(self, name, False)
				else:
					setattr(self, name, True)
			elif name in ['blueFuzz', 'blueShift']:
				v = getattr(self, name)
				if v is None:
					continue
				setattr(self, name, int(round(v)))
			elif name in ['hStems', 'vStems']:
				v = getattr(self, name)
				if v is None:
					continue
				new = []
				for n in v:
					new.append(int(round(n)))
				setattr(self, name, new)
			else:
				v = getattr(self, name)
				if v is None:
					continue
				new = []
				for n in v:
					new.append([int(round(m)) for m in n])
				setattr(self, name, new)



class RoboFabInterpolationError(Exception): pass


def _interpolate(a,b,v):
	"""interpolate values by factor v"""
	return a + (b-a) * v

def _interpolatePt(a, b, v):
	"""interpolate point by factor v"""
	xa, ya = a
	xb, yb = b
	if not isinstance(v, tuple):
		xv = v
		yv = v
	else:
		xv, yv = v
	return xa + (xb-xa) * xv, ya + (yb-ya) * yv

def _scalePointFromCenter(pt, scale, center):
	"""scale a point from a center point"""
	pointX, pointY = pt
	scaleX, scaleY = scale
	centerX, centerY = center
	ogCenter = center
	scaledCenter = (centerX * scaleX, centerY * scaleY)
	shiftVal = (scaledCenter[0] - ogCenter[0], scaledCenter[1] - ogCenter[1])
	scaledPointX = (pointX * scaleX) - shiftVal[0]
	scaledPointY = (pointY * scaleY) - shiftVal[1]
	return (scaledPointX, scaledPointY)

def _box(objectToMeasure, fontObject=None):
	"""calculate the bounds of the object and return it as a (xMin, yMin, xMax, yMax)"""
	#from fontTools.pens.boundsPen import BoundsPen
	from robofab.pens.boundsPen import BoundsPen
	boundsPen = BoundsPen(glyphSet=fontObject)
	objectToMeasure.draw(boundsPen)
	bounds = boundsPen.bounds
	if bounds is None:
		bounds = (0, 0, 0, 0)
	return bounds

def roundPt(pt):
	"""Round a vector"""
	return int(round(pt[0])), int(round(pt[1]))

def addPt(ptA, ptB):
	"""Add two vectors"""
	return ptA[0] + ptB[0], ptA[1] + ptB[1]

def subPt(ptA, ptB):
	"""Substract two vectors"""
	return ptA[0] - ptB[0], ptA[1] - ptB[1]

def mulPt(ptA, scalar):
	"""Multiply a vector with scalar"""
	if not isinstance(scalar, tuple):
		f1 = scalar
		f2 = scalar
	else:
		f1, f2 = scalar
	return ptA[0]*f1, ptA[1]*f2
	
def relativeBCPIn(anchor, BCPIn):
	"""convert absolute incoming bcp value to a relative value"""
	return (BCPIn[0] - anchor[0], BCPIn[1] - anchor[1])

def absoluteBCPIn(anchor, BCPIn):
	"""convert relative incoming bcp value to an absolute value"""
	return (BCPIn[0] + anchor[0], BCPIn[1] + anchor[1])

def relativeBCPOut(anchor, BCPOut):
	"""convert absolute outgoing bcp value to a relative value"""
	return (BCPOut[0] - anchor[0], BCPOut[1] - anchor[1])

def absoluteBCPOut(anchor, BCPOut):
	"""convert relative outgoing bcp value to an absolute value"""
	return (BCPOut[0] + anchor[0], BCPOut[1] + anchor[1])

class FuzzyNumber(object):

	def __init__(self, value, threshold):
		self.value = value
		self.threshold = threshold
	
	def __cmp__(self, other):
		if abs(self.value - other.value) < self.threshold:
			return 0
		else:
			return cmp(self.value, other.value)


class RBaseObject(object):
	
	"""Base class for wrapper objects"""
	
	attrMap= {}
	_title = "RoboFab Wrapper"
	
	def __init__(self):
		self._object = {}
		self.changed = False		# if the object needs to be saved
		self.selected = False
		
	def __len__(self):
		return len(self._object)
	
	def __repr__(self):
		try:
			name = `self._object`
		except:
			name = "None"
		return "<%s for %s>" %(self._title, name)
	
	def copy(self, aParent=None):
		"""Duplicate this object. Pass an object for parenting if you want."""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		dont = ['getParent']
		for k in self.__dict__.keys():
			if k in dont:
				continue
			elif isinstance(self.__dict__[k], (RBaseObject, BaseLib)):
				dup = self.__dict__[k].copy(n)
			else:
				dup = copy.deepcopy(self.__dict__[k])
			setattr(n, k, dup)
		return n
			
	def round(self):
		pass
	
	def isRobofab(self):
		"""Presence of this method indicates a Robofab object"""
		return 1
		
	def naked(self):
		"""Return the wrapped object itself, in case it is needed for direct access."""
		return self._object
	
	def setChanged(self, state=True):
		self.changed = state
	
	def getParent(self):
		"""this method will be overwritten with a weakref if there is a parent."""
		return None
	
	def setParent(self, parent):
		import weakref
		self.getParent = weakref.ref(parent)
		
	def _writeXML(self, writer):
		pass

	def dump(self, private=False):
		"""Print a dump of this object to the std out."""
		from robofab.tools.objectDumper import dumpObject
		dumpObject(self, private)
	


class BaseFont(RBaseObject):
	
	"""Base class for all font objects."""
	
	_allFonts = []
	
	def __init__(self):
		import weakref
		RBaseObject.__init__(self)
		self.changed = False		# if the object needs to be saved
		self._allFonts.append(weakref.ref(self))
		self._supportHints = False
		
	def __repr__(self):
		try:
			name = self.info.postscriptFullName
		except AttributeError:
			name = "unnamed_font"
		return "<RFont font for %s>" %(name)
	
	def __eq__(self, other):
		#Compare this font with another, compare if they refer to the same file.
		return self._compare(other)
		
	def _compare(self, other):
		"""Compare this font to other. RF and FL UFO implementations need
		slightly different ways of comparing fonts. This method does the
		basic stuff. Start with simple and quick comparisons, then move into
		detailed comparisons of glyphs."""
		if not hasattr(other, "fileName"):
			return False
		if self.fileName is not None and self.fileName == other.fileName:
			return True
		if self.fileName <> other.fileName:
			return False
		# this will falsely identify two distinct "Untitled" as equal
		# so test some more. A lot of work to please some dolt who
		# does not save his fonts while running scripts.
		try:
			if len(self) <> len(other):
				return False
		except TypeError:
			return False
		# same name and length. start comparing glyphs
		namesSelf = self.keys()
		namesOther = other.keys()
		namesSelf.sort()
		namesOther.sort()
		for i in range(len(namesSelf)):
			if namesSelf[i] <> namesOther[i]:
				return False
		for c in self:
			if not c == other[c.name]:
				return False
		return True
		
	def keys(self):
		# must be implemented by subclass
		raise NotImplementedError

	def __iter__(self):
		for glyphName in self.keys():
			yield self.getGlyph(glyphName)

	def __getitem__(self, glyphName):
		return self.getGlyph(glyphName)

	def __contains__(self, glyphName):
		return self.has_key(glyphName)

	def _hasChanged(self):
		#mark the object as changed
		self.setChanged(True)
	
	def update(self):
		"""update the font"""
		pass
	
	def close(self, save=1):
		"""Close the font, saving is optional."""
		pass

	def round(self):
		"""round all of the points in all of the glyphs"""
		for glyph in self:
			glyph.round()
	
	def autoUnicodes(self):
		"""Using fontTools.agl, assign Unicode lists to all glyphs in the font"""
		for glyph in self:
			glyph.autoUnicodes()
			
	def getCharacterMapping(self):
		"""Create a dictionary of unicode -> [glyphname, ...] mappings.
		Note that this dict is created each time this method is called, 
		which can make it expensive for larger fonts. All glyphs are loaded.
		Note that one glyph can have multiple unicode values,
		and a unicode value can have multiple glyphs pointing to it."""
		map = {}
		for glyph in self:
			for u in glyph.unicodes:
				if not map.has_key(u):
					map[u] = []
				map[u].append(glyph.name)
		return map
	
	def getReverseComponentMapping(self):
		"""
		Get a reversed map of component references in the font.
		{
		'A' : ['Aacute', 'Aring']
		'acute' : ['Aacute']
		'ring' : ['Aring']
		etc.
		}
		"""
		map = {}
		for glyph in self:
			glyphName = glyph.name
			for component in glyph.components:
				baseGlyphName = component.baseGlyph
				if not map.has_key(baseGlyphName):
					map[baseGlyphName] = []
				map[baseGlyphName].append(glyphName)
		return map

	def compileGlyph(self, glyphName, baseName, accentNames, \
		adjustWidth=False, preflight=False, printErrors=True):
		"""Compile components into a new glyph using components and anchorpoints.
		glyphName: the name of the glyph where it all needs to go
		baseName: the name of the base glyph
		accentNames: a list of accentName, anchorName tuples, [('acute', 'top'), etc]
		"""
		anchors = {}
		errors = {}
		baseGlyph = self[baseName]
		for anchor in baseGlyph.getAnchors():
			anchors[anchor.name] = anchor.position
		destGlyph = self.newGlyph(glyphName, clear=True)
		destGlyph.appendComponent(baseName)
		destGlyph.width = baseGlyph.width
		for accentName, anchorName in accentNames:
			try:
				accent = self[accentName]
			except IndexError:
				errors["glyph '%s' is missing in font %s"%(accentName, self.info.fullName)] =  1
				continue
			shift = None
			for accentAnchor in accent.getAnchors():
				if '_'+anchorName == accentAnchor.name:
					shift = anchors[anchorName][0] - accentAnchor.position[0], anchors[anchorName][1] - accentAnchor.position[1]
					destGlyph.appendComponent(accentName, offset=shift)
					break
			if shift is not None:
				for accentAnchor in accent.getAnchors():
					if accentAnchor.name in anchors:
						anchors[accentAnchor.name] = shift[0]+accentAnchor.position[0], shift[1]+accentAnchor.position[1]
		if printErrors:
			for px in errors.keys():
				print px
		return destGlyph
	
	def generateGlyph(self, glyphName, replace=1, preflight=False, printErrors=True):
		"""Generate a glyph and return it. Assembled from GlyphConstruction.txt"""
		from robofab.tools.toolsAll import readGlyphConstructions
		con = readGlyphConstructions()
		entry = con.get(glyphName, None)
		if not entry:
			print "glyph '%s' is not listed in the robofab/Data/GlyphConstruction.txt"%(glyphName)
			return
		baseName = con[glyphName][0]
		parts = con[glyphName][1:]
		return self.compileGlyph(glyphName, baseName, parts, adjustWidth=1, preflight=preflight, printErrors=printErrors)
	
	def interpolate(self, factor, minFont, maxFont, suppressError=True, analyzeOnly=False, doProgress=False):
		"""Traditional interpolation method. Interpolates by factor between minFont and maxFont.
		suppressError will supress all tracebacks and analyze only will not perform the interpolation
		but it will analyze all glyphs and return a dict of problems."""
		errors = {}
		if not isinstance(factor, tuple):
			factor = factor, factor
		minGlyphNames = minFont.keys()
		maxGlyphNames = maxFont.keys()
		allGlyphNames = list(set(minGlyphNames) | set(maxGlyphNames))
		if doProgress:
			from robofab.interface.all.dialogs import ProgressBar
			progress = ProgressBar('Interpolating...', len(allGlyphNames))
			tickCount = 0
		# some dimensions and values
		self.info.ascender = _interpolate(minFont.info.ascender, maxFont.info.ascender, factor[1])
		self.info.descender = _interpolate(minFont.info.descender, maxFont.info.descender, factor[1])
		# check for the presence of the glyph in each of the fonts
		for glyphName in allGlyphNames:
			if doProgress:
				progress.label(glyphName)
			fatalError = False
			if glyphName not in minGlyphNames:
				fatalError = True
				if not errors.has_key('Missing Glyphs'):
					errors['Missing Glyphs'] = []
				errors['Missing Glyphs'].append('Interpolation Error: %s not in %s'%(glyphName, minFont.info.postscriptFullName))
			if glyphName not in maxGlyphNames:
				fatalError = True
				if not errors.has_key('Missing Glyphs'):
					errors['Missing Glyphs'] = []
				errors['Missing Glyphs'].append('Interpolation Error: %s not in %s'%(glyphName, maxFont.info.postscriptFullName))
			# if no major problems, proceed.
			if not fatalError:
				# remove the glyph since FontLab has a problem with
				# interpolating an existing glyph that contains
				# some contour data.
				oldLib = {}
				oldMark = None
				oldNote = None
				if self.has_key(glyphName):
					glyph = self[glyphName]
					oldLib = dict(glyph.lib)
					oldMark = glyph.mark
					oldNote = glyph.note
					self.removeGlyph(glyphName)
				selfGlyph = self.newGlyph(glyphName)
				selfGlyph.lib.update(oldLib)
				if oldMark != None:
					selfGlyph.mark = oldMark
				selfGlyph.note = oldNote
				min = minFont[glyphName]
				max = maxFont[glyphName]
				ok, glyphErrors = selfGlyph.interpolate(factor, min, max, suppressError=suppressError, analyzeOnly=analyzeOnly)
				if not errors.has_key('Glyph Errors'):
					errors['Glyph Errors'] = {}
				errors['Glyph Errors'][glyphName] = glyphErrors
			if doProgress:
				progress.tick(tickCount)
				tickCount = tickCount + 1
		if doProgress:
			progress.close()
		return errors

	def getGlyphNameToFileNameFunc(self):
		funcName = self.lib.get("org.robofab.glyphNameToFileNameFuncName")
		if funcName is None:
			return None
		parts = funcName.split(".")
		module = ".".join(parts[:-1])
		try:
			item = __import__(module)
			for sub in parts[1:]:
				item = getattr(item, sub)
		except (ImportError, AttributeError):
			warn("Can't find glyph name to file name converter function, "
				"falling back to default scheme (%s)" % funcName, RoboFabWarning)
			return None
		else:
			return item


class BaseGlyph(RBaseObject):
	
	"""Base class for all glyph objects."""
	
	def __init__(self):
		RBaseObject.__init__(self)
		#self.contours = []
		#self.components = []
		#self.anchors = []
		#self.width = 0
		#self.note = None
		##self.unicodes = []
		#self.selected = None
		self.changed = False		# if the object needs to be saved
	
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		fontParent = self.getParent()
		if fontParent is not None:
			try:
				font = fontParent.info.postscriptFullName
			except AttributeError:
				pass
		try:
			glyph = self.name
		except AttributeError:
			pass
		return "<RGlyph for %s.%s>" %(font, glyph)
		
	#
	# Glyph Math
	#
	
	def _getMathData(self):
		from robofab.pens.mathPens import GetMathDataPointPen
		pen = GetMathDataPointPen()
		self.drawPoints(pen)
		data = pen.getData()
		return data
	
	def _setMathData(self, data, destination=None):
		from robofab.pens.mathPens import CurveSegmentFilterPointPen
		if destination is None:
			newGlyph = self._mathCopy()
		else:
			newGlyph = destination
		newGlyph.clear()
		#
		# draw the data onto the glyph
		pointPen = newGlyph.getPointPen()
		filterPen = CurveSegmentFilterPointPen(pointPen)
		for contour in data['contours']:
			filterPen.beginPath()
			for segmentType, pt, smooth, name in contour:
				filterPen.addPoint(pt=pt, segmentType=segmentType, smooth=smooth, name=name)
			filterPen.endPath()
		for baseName, transformation in data['components']:
			filterPen.addComponent(baseName, transformation)
		for pt, name in data['anchors']:
			filterPen.beginPath()
			filterPen.addPoint(pt=pt, segmentType="move", smooth=False, name=name)
			filterPen.endPath()
		newGlyph.width = data['width']
		psHints = data.get('psHints')
		if psHints is not None:
			newGlyph.psHints.update(psHints)
		#
		return newGlyph
	
	def _getMathDestination(self):
		# make a new, empty glyph
		return self.__class__()
	
	def _mathCopy(self):
		# copy self without contour, component and anchor data
		glyph = self._getMathDestination()
		glyph.name = self.name
		glyph.unicodes = list(self.unicodes)
		glyph.width = self.width
		glyph.note = self.note
		glyph.lib = dict(self.lib)
		return glyph
	
	def _processMathOne(self, otherGlyph, funct):
		# used by: __add__, __sub__
		#
		newData =	{
				'contours':[],
				'components':[],
				'anchors':[],
				'width':None
				}
		selfData = self._getMathData()
		otherData = otherGlyph._getMathData()
		#
		# contours
		selfContours = selfData['contours']
		otherContours = otherData['contours']
		newContours = newData['contours']
		if len(selfContours) > 0:
			for contourIndex in xrange(len(selfContours)):
				newContours.append([])
				selfContour = selfContours[contourIndex]
				otherContour = otherContours[contourIndex]
				for pointIndex in xrange(len(selfContour)):
					segType, pt, smooth, name = selfContour[pointIndex]
					newX, newY = funct(selfContour[pointIndex][1], otherContour[pointIndex][1])
					newContours[-1].append((segType, (newX, newY), smooth, name))
		# anchors
		selfAnchors = selfData['anchors']
		otherAnchors = otherData['anchors']
		newAnchors = newData['anchors']
		if len(selfAnchors) > 0:
			selfAnchors, otherAnchors = self._mathAnchorCompare(selfAnchors, otherAnchors)
			anchorNames = selfAnchors.keys()
			for anchorName in anchorNames:
				selfAnchorList = selfAnchors[anchorName]
				otherAnchorList = otherAnchors[anchorName]
				for i in range(len(selfAnchorList)):
					selfAnchor = selfAnchorList[i]
					otherAnchor = otherAnchorList[i]
					newAnchor = funct(selfAnchor, otherAnchor)
					newAnchors.append((newAnchor, anchorName))
		# components
		selfComponents = selfData['components']
		otherComponents = otherData['components']
		newComponents = newData['components']
		if len(selfComponents) > 0:
			selfComponents, otherComponents = self._mathComponentCompare(selfComponents, otherComponents)
			componentNames = selfComponents.keys()
			for componentName in componentNames:
				selfComponentList = selfComponents[componentName]
				otherComponentList = otherComponents[componentName]
				for i in range(len(selfComponentList)):
					# transformation breakdown: xScale, xyScale, yxScale, yScale, xOffset, yOffset
					selfXScale, selfXYScale, selfYXScale, selfYScale, selfXOffset, selfYOffset = selfComponentList[i]
					otherXScale, otherXYScale, otherYXScale, otherYScale, otherXOffset, otherYOffset = otherComponentList[i]
					newXScale, newXYScale = funct((selfXScale, selfXYScale), (otherXScale, otherXYScale))
					newYXScale, newYScale = funct((selfYXScale, selfYScale), (otherYXScale, otherYScale))
					newXOffset, newYOffset = funct((selfXOffset, selfYOffset), (otherXOffset, otherYOffset))
					newComponents.append((componentName, (newXScale, newXYScale, newYXScale, newYScale, newXOffset, newYOffset)))
		return newData
	
	def _processMathTwo(self, factor, funct):
		# used by: __mul__, __div__
		#
		newData =	{
				'contours':[],
				'components':[],
				'anchors':[],
				'width':None
				}
		selfData = self._getMathData()
		# contours
		selfContours = selfData['contours']
		newContours = newData['contours']
		for selfContour in selfContours:
			newContours.append([])
			for segType, pt, smooth, name in selfContour:
				newX, newY = funct(pt, factor)
				newContours[-1].append((segType, (newX, newY), smooth, name))
		# anchors
		selfAnchors = selfData['anchors']
		newAnchors = newData['anchors']
		for pt, anchorName in selfAnchors:
			newPt = funct(pt, factor)
			newAnchors.append((newPt, anchorName))
		# components
		selfComponents = selfData['components']
		newComponents = newData['components']
		for baseName, transformation in selfComponents:
			xScale, xyScale, yxScale, yScale, xOffset, yOffset = transformation
			newXOffset, newYOffset = funct((xOffset, yOffset), factor)
			newXScale, newYScale = funct((xScale, yScale), factor)
			newXYScale, newYXScale = funct((xyScale, yxScale), factor)
			newComponents.append((baseName, (newXScale, newXYScale, newYXScale, newYScale, newXOffset, newYOffset)))
		# return the data
		return newData
	
	def _mathAnchorCompare(self, selfMathAnchors, otherMathAnchors):
		# collect compatible anchors
		selfAnchors = {}
		for pt, name in selfMathAnchors:
			if not selfAnchors.has_key(name):
				selfAnchors[name] = []
			selfAnchors[name].append(pt)
		otherAnchors = {}
		for pt, name in otherMathAnchors:
			if not otherAnchors.has_key(name):
				otherAnchors[name] = []
			otherAnchors[name].append(pt)
		compatAnchors = set(selfAnchors.keys()) & set(otherAnchors.keys())
		finalSelfAnchors = {}
		finalOtherAnchors = {}
		for name in compatAnchors:
			if not finalSelfAnchors.has_key(name):
				finalSelfAnchors[name] = []
			if not finalOtherAnchors.has_key(name):
				finalOtherAnchors[name] = []
			selfList = selfAnchors[name]
			otherList = otherAnchors[name]
			selfCount = len(selfList)
			otherCount = len(otherList)
			if selfCount != otherCount:
				r = range(min(selfCount, otherCount))
			else:
				r = range(selfCount)
			for i in r:
				finalSelfAnchors[name].append(selfList[i])
				finalOtherAnchors[name].append(otherList[i])
		return finalSelfAnchors, finalOtherAnchors
	
	def _mathComponentCompare(self, selfMathComponents, otherMathComponents):
		# collect compatible components
		selfComponents = {}
		for baseName, transformation in selfMathComponents:
			if not selfComponents.has_key(baseName):
				selfComponents[baseName] = []
			selfComponents[baseName].append(transformation)
		otherComponents = {}
		for baseName, transformation in otherMathComponents:
			if not otherComponents.has_key(baseName):
				otherComponents[baseName] = []
			otherComponents[baseName].append(transformation)
		compatComponents = set(selfComponents.keys()) & set(otherComponents.keys())
		finalSelfComponents = {}
		finalOtherComponents = {}
		for baseName in compatComponents:
			if not finalSelfComponents.has_key(baseName):
				finalSelfComponents[baseName] = []
			if not finalOtherComponents.has_key(baseName):
				finalOtherComponents[baseName] = []
			selfList = selfComponents[baseName]
			otherList = otherComponents[baseName]
			selfCount = len(selfList)
			otherCount = len(otherList)
			if selfCount != otherCount:
				r = range(min(selfCount, otherCount))
			else:
				r = range(selfCount)
			for i in r:
				finalSelfComponents[baseName].append(selfList[i])
				finalOtherComponents[baseName].append(otherList[i])
		return finalSelfComponents, finalOtherComponents
		
	def __mul__(self, factor):
		assert isinstance(factor, (int, float, tuple)), "Glyphs can only be multiplied by int, float or a 2-tuple."
		if not isinstance(factor, tuple):
			factor = (factor, factor)
		data = self._processMathTwo(factor, mulPt)
		data['width'] = self.width * factor[0]
		# psHints
		if not self.psHints.isEmpty():
			newPsHints = self.psHints * factor
			data['psHints'] = newPsHints
		return self._setMathData(data)

	__rmul__ = __mul__

	def __div__(self, factor):
		assert isinstance(factor, (int, float, tuple)), "Glyphs can only be divided by int, float or a 2-tuple."
		# calculate reverse factor, and cause nice ZeroDivisionError if it can't
		if isinstance(factor, tuple):
			reverse = 1.0/factor[0], 1.0/factor[1]
		else:
			reverse = 1.0/factor
		return self.__mul__(reverse)

	def __add__(self, other):
		assert isinstance(other, BaseGlyph), "Glyphs can only be added to other glyphs."
		data = self._processMathOne(other, addPt)
		data['width'] = self.width + other.width
		return self._setMathData(data)

	def __sub__(self, other):
		assert isinstance(other, BaseGlyph), "Glyphs can only be substracted from other glyphs."
		data = self._processMathOne(other, subPt)
		data['width'] = self.width + other.width
		return self._setMathData(data)
	
	#
	# Interpolation
	#
	
	def interpolate(self, factor, minGlyph, maxGlyph, suppressError=True, analyzeOnly=False):
		"""Traditional interpolation method. Interpolates by factor between minGlyph and maxGlyph.
		suppressError will supress all tracebacks and analyze only will not perform the interpolation
		but it will analyze all glyphs and return a dict of problems."""
		if not isinstance(factor, tuple):
			factor = factor, factor
		fatalError = False
		if analyzeOnly:
			ok, errors = minGlyph.isCompatible(maxGlyph)
			return ok, errors
		minData = None
		maxData = None
		minName = minGlyph.name
		maxName = maxGlyph.name
		try:
			minData = minGlyph._getMathData()
			maxData = maxGlyph._getMathData()
			newContours = self._interpolateContours(factor, minData['contours'], maxData['contours'])
			newComponents = self._interpolateComponents(factor, minData['components'], maxData['components'])
			newAnchors = self._interpolateAnchors(factor, minData['anchors'], maxData['anchors'])
			newWidth = _interpolate(minGlyph.width, maxGlyph.width, factor[0])
			newData = {
					'contours':newContours,
					'components':newComponents,
					'anchors':newAnchors,
					'width':newWidth
					}
			self._setMathData(newData, self)
		except IndexError:
			if not suppressError:
				ok, errors = minGlyph.isCompatible(maxGlyph)
				ok = not ok
				return ok, errors
		self.update()
		return False, []
	
	def isCompatible(self, otherGlyph, report=True):
		"""Return a bool value if the glyph is compatible with otherGlyph.
		With report = True, isCompatible will return a report of what's wrong.
		The interpolate method requires absolute equality between contour data.
		Absolute equality is preferred among component and anchor data, but
		it is NOT required. Interpolation between components and anchors
		will only deal with compatible data and incompatible data will be
		ignored. This method reflects this system."""
		selfName = self.name
		selfData = self._getMathData()
		otherName = otherGlyph.name
		otherData = otherGlyph._getMathData()
		compatible, errors = self._isCompatibleInternal(selfName, otherName, selfData, otherData)
		if report:
			return compatible, errors
		return compatible
				
	def _isCompatibleInternal(self, selfName, otherName, selfData, otherData):
		fatalError = False
		errors = []
		## contours
		# any contour incompatibilities
		# result in fatal errors
		selfContours = selfData['contours']
		otherContours = otherData['contours']
		if len(selfContours) != len(otherContours):
			fatalError = True
			errors.append("Fatal error: glyph %s and glyph %s don't have the same number of contours." %(selfName, otherName))
		else:
			for contourIndex in xrange(len(selfContours)):
				selfContour = selfContours[contourIndex]
				otherContour = otherContours[contourIndex]
				if len(selfContour) != len(otherContour):
					fatalError = True
					errors.append("Fatal error: contour %d in glyph %s and glyph %s don't have the same number of segments." %(contourIndex, selfName, otherName))
		## components
		# component incompatibilities
		# do not result in fatal errors
		selfComponents = selfData['components']
		otherComponents = otherData['components']
		if len(selfComponents) != len(otherComponents):
			errors.append("Error: glyph %s and glyph %s don't have the same number of components." %(selfName, otherName))
		for componentIndex in xrange(min(len(selfComponents), len(otherComponents))):
			selfBaseName, selfTransformation = selfComponents[componentIndex]
			otherBaseName, otherTransformation = otherComponents[componentIndex]
			if selfBaseName != otherBaseName:
				errors.append("Error: component %d in glyph %s and glyph %s don't have the same base glyph." %(componentIndex, selfName, otherName))
		## anchors
		# anchor incompatibilities
		# do not result in fatal errors
		selfAnchors = selfData['anchors']
		otherAnchors = otherData['anchors']
		if len(selfAnchors) != len(otherAnchors):
			errors.append("Error: glyph %s and glyph %s don't have the same number of anchors." %(selfName, otherName))
		for anchorIndex in xrange(min(len(selfAnchors), len(otherAnchors))):
			selfPt, selfAnchorName = selfAnchors[anchorIndex]
			otherPt, otherAnchorName = otherAnchors[anchorIndex]
			if selfAnchorName != otherAnchorName:
				errors.append("Error: anchor %d in glyph %s and glyph %s don't have the same name." %(anchorIndex, selfName, otherName))
		return not fatalError, errors
	
	def _interpolateContours(self, factor, minContours, maxContours):
		newContours = []
		for contourIndex in xrange(len(minContours)):
			minContour = minContours[contourIndex]
			maxContour = maxContours[contourIndex]
			newContours.append([])
			for pointIndex in xrange(len(minContour)):
				segType, pt, smooth, name = minContour[pointIndex]
				minPoint = minContour[pointIndex][1]
				maxPoint = maxContour[pointIndex][1]
				newX, newY = _interpolatePt(minPoint, maxPoint, factor)
				newContours[-1].append((segType, (newX, newY), smooth, name))
		return newContours

	def _interpolateComponents(self, factor, minComponents, maxComponents):
		newComponents = []
		minComponents, maxComponents = self._mathComponentCompare(minComponents, maxComponents)
		componentNames = minComponents.keys()
		for componentName in componentNames:
			minComponentList = minComponents[componentName]
			maxComponentList = maxComponents[componentName]
			for i in xrange(len(minComponentList)):
				# transformation breakdown: xScale, xyScale, yxScale, yScale, xOffset, yOffset
				minXScale, minXYScale, minYXScale, minYScale, minXOffset, minYOffset = minComponentList[i]
				maxXScale, maxXYScale, maxYXScale, maxYScale, maxXOffset, maxYOffset = maxComponentList[i]
				newXScale, newXYScale = _interpolatePt((minXScale, minXYScale), (maxXScale, maxXYScale), factor)
				newYXScale, newYScale = _interpolatePt((minYXScale, minYScale), (maxYXScale, maxYScale), factor)
				newXOffset, newYOffset = _interpolatePt((minXOffset, minYOffset), (maxXOffset, maxYOffset), factor)
				newComponents.append((componentName, (newXScale, newXYScale, newYXScale, newYScale, newXOffset, newYOffset)))
		return newComponents

	def _interpolateAnchors(self, factor, minAnchors, maxAnchors):
		newAnchors = []
		minAnchors, maxAnchors = self._mathAnchorCompare(minAnchors, maxAnchors)
		anchorNames = minAnchors.keys()
		for anchorName in anchorNames:
			minAnchorList = minAnchors[anchorName]
			maxAnchorList = maxAnchors[anchorName]
			for i in range(len(minAnchorList)):
				minAnchor = minAnchorList[i]
				maxAnchor = maxAnchorList[i]
				newAnchor = _interpolatePt(minAnchor, maxAnchor, factor)
				newAnchors.append((newAnchor, anchorName))
		return newAnchors
	
	#
	# comparisons
	#

	def __eq__(self, other):
		if isinstance(other, BaseGlyph):
			return self._getDigest() == other._getDigest()
		return False
	
	def __ne__(self, other):
		return not self.__eq__(other)

	def _getDigest(self, pointsOnly=False):
		"""Calculate a digest of coordinates, points, things in this glyph.
		With pointsOnly == True the digest consists of a flat tuple of all
		coordinate pairs in the glyph, without the order of contours.
		"""
		from robofab.pens.digestPen import DigestPointPen
		mp = DigestPointPen()
		self.drawPoints(mp)
		if pointsOnly:
			return "%s|%d|%s"%(mp.getDigestPointsOnly(), self.width, self.unicode)
		else:
			return "%s|%d|%s"%(mp.getDigest(), self.width, self.unicode)
	
	def _getStructure(self):
		"""Calculate a digest of points, things in this glyph, but NOT coordinates."""
		from robofab.pens.digestPen import DigestPointStructurePen
		mp = DigestPointStructurePen()
		self.drawPoints(mp)
		return mp.getDigest()
	
	def _hasChanged(self):
		"""mark the object and it's parent as changed"""
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()
	
	def _get_box(self):
		bounds = _box(self, fontObject=self.getParent())
		return bounds
	
	box = property(_get_box, doc="the bounding box of the glyph: (xMin, yMin, xMax, yMax)")
			
	def _get_leftMargin(self):
		if self.isEmpty():
			return 0
		xMin, yMin, xMax, yMax = self.box
		return xMin
		
	def _set_leftMargin(self, value):
		if self.isEmpty():
			self.width = self.width + value
		else:
			diff = value - self.leftMargin
			self.move((diff, 0))
			self.width = self.width + diff
	
	leftMargin = property(_get_leftMargin, _set_leftMargin, doc="the left margin")

	def _get_rightMargin(self):
		if self.isEmpty():
			return self.width
		xMin, yMin, xMax, yMax = self.box
		return self.width - xMax
		
	def _set_rightMargin(self, value):
		if self.isEmpty():
			self.width = value
		else:
			xMin, yMin, xMax, yMax = self.box
			self.width = xMax + value

	rightMargin = property(_get_rightMargin, _set_rightMargin, doc="the right margin")
	
	def copy(self, aParent=None):
		"""Duplicate this glyph"""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		dont = ['_object', 'getParent']
		for k in self.__dict__.keys():
			ok = True
			if k in dont:
				continue
			elif k == "contours":
				dup = []
				for i in self.contours:
					dup.append(i.copy(n))
			elif k == "components":
				dup = []
				for i in self.components:
					dup.append(i.copy(n))
			elif k == "anchors":
				dup = []
				for i in self.anchors:
					dup.append(i.copy(n))
			elif k == "psHints":
				dup = self.psHints.copy()
			elif isinstance(self.__dict__[k], (RBaseObject, BaseLib)):
				dup = self.__dict__[k].copy(n)
			else:
				dup = copy.deepcopy(self.__dict__[k])
			if ok:
				setattr(n, k, dup)
		return n
	
	def _setParentTree(self):
		"""Set the parents of all contained and dependent objects (and their dependents) right."""
		for item in self.contours:
			item.setParent(self)
			item._setParentTree()
		for item in self.components:
			item.setParent(self)
		for items in self.anchors:
			item.setParent(self)

	def getGlyph(self, glyphName):
		"""Provided there is a font parent for this glyph, return a sibling glyph."""
		if glyphName == self.name:
			return self
		if self.getParent() is not None:
			return self.getParent()[glyphName]
		return None
		
	def getPen(self):
		"""Return a Pen object for creating an outline in this glyph."""
		from robofab.pens.adapterPens import SegmentToPointPen
		return SegmentToPointPen(self.getPointPen())

	def getPointPen(self):
		"""Return a PointPen object for creating an outline in this glyph."""
		raise NotImplementedError, "getPointPen() must be implemented by subclass"
	
	def deSelect(self):
		"""Set all selected attrs in glyph to False: for the glyph, components, anchors, points."""
		for a in self.anchors:
			a.selected = False
		for a in self.components:
			a.selected = False
		for c in self.contours:
			for p in c.points:
				p.selected = False
		self.selected = False

	def isEmpty(self):
		"""return true if the glyph has no contours or components"""
		if len(self.contours) + len(self.components) == 0:
			return True
		else:
			return False
	
	def _saveToGlyphSet(self, glyphSet, glyphName=None, force=False):
		"""Save the glyph to GlyphSet, a private method that's part of the saving process."""
		# save stuff in the lib first
		if force or self.changed:
			if glyphName is None:
				glyphName = self.name
			glyphSet.writeGlyph(glyphName, self, self.drawPoints)
			
	def update(self):
		"""update the glyph"""
		pass
	
	def draw(self, pen):
		"""draw the object with a RoboFab segment pen"""
		try:
			pen.setWidth(self.width)
			if self.note is not None:
				pen.setNote(self.note)
		except AttributeError:
			# FontTools pens don't have these methods
			pass
		for a in self.anchors:
			a.draw(pen)
		for c in self.contours:
			c.draw(pen)
		for c in self.components:
			c.draw(pen)
		try:
			pen.doneDrawing()
		except AttributeError:
			# FontTools pens don't have a doneDrawing() method
			pass
		
	def drawPoints(self, pen):
		"""draw the object with a point pen"""
		for a in self.anchors:
			a.drawPoints(pen)
		for c in self.contours:
			c.drawPoints(pen)
		for c in self.components:
			c.drawPoints(pen)
	
	def appendContour(self, aContour, offset=(0, 0)):
		"""append a contour to the glyph"""
		x, y = offset
		pen = self.getPointPen()
		aContour.drawPoints(pen)
		self.contours[-1].move((x, y))
	
	def appendGlyph(self, aGlyph, offset=(0, 0)):
		"""append another glyph to the glyph"""
		x, y = offset
		pen = self.getPointPen()
		#to handle the offsets, move the source glyph and then move it back!
		aGlyph.move((x, y))
		aGlyph.drawPoints(pen)
		aGlyph.move((-x, -y))
		
	def round(self):
		"""round all coordinates in all contours, components and anchors"""
		for n in self.contours:
			n.round()
		for n in self.components:
			n.round()
		for n in self.anchors:
			n.round()
		self.width = int(round(self.width))
		
	def autoUnicodes(self):
		"""Using fontTools.agl, assign Unicode list to the glyph"""
		from fontTools.agl import AGL2UV
		if AGL2UV.has_key(self.name):
			self.unicode = AGL2UV[self.name]
			self._hasChanged()
			
	def pointInside(self, pt, evenOdd=0):
		"""determine if the point is in the black or white of the glyph"""
		x, y = pt
		from fontTools.pens.pointInsidePen import PointInsidePen
		font = self.getParent()
		piPen = PointInsidePen(glyphSet=font, testPoint=(x, y), evenOdd=evenOdd)
		self.draw(piPen)
		return piPen.getResult()
	
	def correctDirection(self, trueType=False):
		"""corect the direction of the contours in the glyph."""
		#this is a bit slow, but i'm not sure how much more it can be optimized.
		#it also has a bug somewhere that is causeing some contours to be set incorrectly.
		#try to run it on the copyright symbol to see the problem. hm.
		#
		#establish the default direction that an outer contour should follow
		#i believe for TT this is clockwise and for PS it is counter
		#i could be wrong about this, i need to double check.
		from fontTools.pens.pointInsidePen import PointInsidePen
		baseDirection = 0
		if trueType:
			baseDirection = 1
		#we don't need to do all the work if the contour count is < 2
		count = len(self.contours)
		if count == 0:
			return
		elif count == 1:
			self.contours[0].clockwise = baseDirection
			return
		#store up needed before we start
		#i think the .box calls are eating a big chunk of the time
		contourDict = {}
		for contourIndex in range(len(self.contours)):
			contour = self.contours[contourIndex]
			contourDict[contourIndex] = {'box':contour.box, 'dir':contour.clockwise, 'hit':[], 'notHit':[]}
		#now, for every contour, determine which contours it intersects
		#as we go, we will also store contours that it doesn't intersct
		#and we store this value for both contours
		allIndexes = contourDict.keys()
		for contourIndex in allIndexes:
			for otherContourIndex in allIndexes:
				if otherContourIndex != contourIndex:
					if contourIndex not in contourDict[otherContourIndex]['hit'] and contourIndex not in contourDict[otherContourIndex]['notHit']:
						xMin1, yMin1, xMax1, yMax1 = contourDict[contourIndex]['box']
						xMin2, yMin2, xMax2, yMax2= contourDict[otherContourIndex]['box']	
						hit, pos = sectRect((xMin1, yMin1, xMax1, yMax1), (xMin2, yMin2, xMax2, yMax2))
						if hit == 1:
							contourDict[contourIndex]['hit'].append(otherContourIndex)
							contourDict[otherContourIndex]['hit'].append(contourIndex)
						else:
							contourDict[contourIndex]['notHit'].append(otherContourIndex)
							contourDict[otherContourIndex]['notHit'].append(contourIndex)
		#set up the pen here to shave a bit of time
		font = self.getParent()
		piPen = PointInsidePen(glyphSet=font, testPoint=(0, 0), evenOdd=0)
		#now do the pointInside work
		for contourIndex in allIndexes:
			direction = baseDirection
			contour = self.contours[contourIndex]
			startPoint = contour.segments[0].onCurve
			if startPoint is not None:	#skip TT paths with no onCurve
				if len(contourDict[contourIndex]['hit']) != 0:
					for otherContourIndex in contourDict[contourIndex]['hit']:
						piPen.setTestPoint(testPoint=(startPoint.x, startPoint.y))
						otherContour = self.contours[otherContourIndex]
						otherContour.draw(piPen)
						direction = direction + piPen.getResult()
			newDirection = direction % 2
			#now set the direction if we need to
			if newDirection != contourDict[contourIndex]['dir']:
				contour.reverseContour()
	
	def autoContourOrder(self):
		"""attempt to sort the contours based on their centers"""
		# sort is based on (in this order):
		# - the (negative) point count
		# - the (negative) segment count
		# - fuzzy x value of the center of the contour
		# - fuzzy y value of the center of the contour
		# - the (negative) surface of the bounding box of the contour: width * height
		# the latter is a safety net for for instances like a very thin 'O' where the
		# x centers could be close enough to rely on the y for the sort which could
		# very well be the same for both contours. We use the _negative_ of the surface
		# to ensure that larger contours appear first, which seems more natural.
		tempContourList = []
		contourList = []
		xThreshold = None
		yThreshold = None
		for contour in self.contours:
			xMin, yMin, xMax, yMax = contour.box
			width = xMax - xMin
			height = yMax - yMin
			xC = 0.5 * (xMin + xMax)
			yC = 0.5 * (yMin + yMax)
			xTh = abs(width * .5)
			yTh = abs(height * .5)
			if xThreshold is None or xThreshold > xTh:
				xThreshold = xTh
			if yThreshold is None or yThreshold > yTh:
				yThreshold = yTh
			tempContourList.append((-len(contour.points), -len(contour.segments), xC, yC, -(width * height), contour))
		for points, segments, x, y, surface, contour in tempContourList:
			contourList.append((points, segments, FuzzyNumber(x, xThreshold), FuzzyNumber(y, yThreshold), surface, contour))
		contourList.sort()
		for i in range(len(contourList)):
			points, segments, xO, yO, surface, contour = contourList[i]
			contour.index = i
	
	def rasterize(self, cellSize=50, xMin=None, yMin=None, xMax=None, yMax=None):
		"""
		Slice the glyph into a grid based on the cell size.
		It returns a list of lists containing bool values
		that indicate the black (True) or white (False)
		value of that particular cell.	These lists are
		arranged from top to bottom of the glyph and
		proceed from left to right.
		This is an expensive operation!
		"""
		from fontTools.pens.pointInsidePen import PointInsidePen
		piPen = PointInsidePen(glyphSet=self.getParent(), testPoint=(0, 0), evenOdd=0)
		if xMin is None or yMin is None or xMax is None or yMax is None:
			_xMin, _yMin, _xMax, _yMax = self.box
			if xMin is None:
				xMin = _xMin
			if yMin is None:
				yMin = _yMin
			if xMax is None:
				xMax = _xMax
			if yMax is None:
				yMax = _yMax
		#
		hitXMax = False
		hitYMin = False
		xSlice = 0
		ySlice = 0
		halfCellSize = cellSize / 2.0
		#
		map = []
		#
		while not hitYMin:
			map.append([])
			yScan = -(ySlice * cellSize) + yMax - halfCellSize
			if yScan < yMin:
				hitYMin = True
			while not hitXMax:
				xScan = (xSlice * cellSize) + xMin - halfCellSize
				if xScan > xMax:
					hitXMax = True
				piPen.setTestPoint((xScan, yScan))
				self.draw(piPen)
				test = piPen.getResult()
				if test:
					map[-1].append(True)
				else:
					map[-1].append(False)
				xSlice = xSlice + 1
			hitXMax = False
			xSlice = 0
			ySlice = ySlice + 1
		return map

	def move(self, pt, contours=True, components=True, anchors=True):
		"""Move a glyph's items that are flagged as True"""
		x, y = roundPt(pt)
		if contours:
			for contour in self.contours:
				contour.move((x, y))
		if components:
			for component in self.components:
				component.move((x, y))
		if anchors:
			for anchor in self.anchors:
				anchor.move((x, y))
			
	def scale(self, pt, center=(0, 0)):
		"""scale the glyph"""
		x, y = pt
		for contour in self.contours:
			contour.scale((x, y), center=center)
		for component in self.components:
			offset = component.offset
			component.offset = _scalePointFromCenter(offset, pt, center)
			sX, sY = component.scale
			component.scale = (sX*x, sY*y)
		for anchor in self.anchors:
			anchor.scale((x, y), center=center)

	def transform(self, matrix):
		"""Transform this glyph.
		Use a Transform matrix object from
		robofab.transform"""
		n = []
		for c in self.contours:
			c.transform(matrix)
		for a in self.anchors:
			a.transform(matrix)
			
	def rotate(self, angle, offset=None):
		"""rotate the glyph"""
		from fontTools.misc.transform import Identity
		radAngle = angle / DEGREE	# convert from degrees to radians
		if offset is None:
			offset = (0,0)
		rT = Identity.translate(offset[0], offset[1])
		rT = rT.rotate(radAngle)
		rT = rT.translate(-offset[0], -offset[1])
		self.transform(rT)	
	
	def skew(self, angle, offset=None):
		"""skew the glyph"""
		from fontTools.misc.transform import Identity
		radAngle = angle / DEGREE	# convert from degrees to radians
		if offset is None:
			offset = (0,0)
		rT = Identity.translate(offset[0], offset[1])
		rT = rT.skew(radAngle)
		self.transform(rT)
	
	
class BaseContour(RBaseObject):
	
	"""Base class for all contour objects."""
	
	def __init__(self):
		RBaseObject.__init__(self)
		#self.index = None
		self.changed = False		# if the object needs to be saved
		
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		glyphParent = self.getParent()
		if glyphParent is not None:
			try:
				glyph = glyphParent.name
			except AttributeError: pass
			fontParent = glyphParent.getParent()
			if fontParent is not None:
				try:
					font = fontParent.info.postscriptFullName
				except AttributeError: pass
		try:
			idx = `self.index`
		except ValueError:
			# XXXX
			idx = "XXX"
		return "<RContour for %s.%s[%s]>"%(font, glyph, idx)
		
	def __len__(self):
		return len(self.segments)
	
	def __mul__(self, factor):
		warn("Contour math has been deprecated and is slated for removal.", DeprecationWarning)
		n = self.copy()
		n.segments = []
		for i in range(len(self.segments)):
			n.segments.append(self.segments[i] * factor)
		n._setParentTree()
		return n
	
	__rmul__ = __mul__

	def __add__(self, other):
		warn("Contour math has been deprecated and is slated for removal.", DeprecationWarning)
		n = self.copy()
		n.segments = []
		for i in range(len(self.segments)):
			n.segments.append(self.segments[i] + other.segments[i])
		n._setParentTree()
		return n

	def __sub__(self, other):
		warn("Contour math has been deprecated and is slated for removal.", DeprecationWarning)
		n = self.copy()
		n.segments = []
		for i in range(len(self.segments)):
			n.segments.append(self.segments[i] - other.segments[i])
		n._setParentTree()
		return n
		
	def __getitem__(self, index):
		return self.segments[index]
		
	def _hasChanged(self):
		"""mark the object and it's parent as changed"""
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()
	
	def _nextSegment(self, segmentIndex):
		return self.segments[(segmentIndex + 1) % len(self.segments)]
	
	def _prevSegment(self, segmentIndex):
		segments = self.segments
		return self.segments[(segmentIndex - 1) % len(self.segments)]
		
	def _get_box(self):
		bounds = _box(self)
		return bounds
	
	box = property(_get_box, doc="the bounding box for the contour")

	def _set_clockwise(self, value):
		if self.clockwise != value:
			self.reverseContour()
			
	def _get_clockwise(self):
		pen = AreaPen(self)
		self.draw(pen)
		return pen.value < 0

	clockwise = property(_get_clockwise, _set_clockwise, doc="direction of contour: positive=counterclockwise negative=clockwise")

	def copy(self, aParent=None):
		"""Duplicate this contour"""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		dont = ['_object', 'points', 'bPoints', 'getParent']
		for k in self.__dict__.keys():
			ok = True
			if k in dont:
				continue
			elif k == "segments":
				dup = []
				for i in self.segments:
					dup.append(i.copy(n))
			elif isinstance(self.__dict__[k], (RBaseObject, BaseLib)):
				dup = self.__dict__[k].copy(n)
			else:
				dup = copy.deepcopy(self.__dict__[k])
			if ok:
				setattr(n, k, dup)
		return n
		
	def _setParentTree(self):
		"""Set the parents of all contained and dependent objects (and their dependents) right."""
		for item in self.segments:
			item.setParent(self)

	def round(self):
		"""round the value of all points in the contour"""
		for n in self.points:
			n.round()
	
	def draw(self, pen):
		"""draw the object with a fontTools pen"""
		firstOn = self.segments[0].onCurve
		firstType = self.segments[0].type
		lastOn = self.segments[-1].onCurve
		# this is a special exception for FontLab
		# FL can have a contour that does not contain a move.
		# this will only happen if the contour begins with a qcurve.
		# in this case, we move to the segment's on curve,
		# then we iterate through the rest of the points,
		# then we add the first qcurve and finally we
		# close the path. after this, i say "ugh."
		if firstType == QCURVE:
			pen.moveTo((firstOn.x, firstOn.y))
			for segment in self.segments[1:]:
				segmentType = segment.type
				pt = segment.onCurve.x, segment.onCurve.y
				if segmentType == LINE:
					pen.lineTo(pt)
				elif segmentType == CURVE:
					pts = [(point.x, point.y) for point in segment.points]
					pen.curveTo(*pts)
				elif segmentType == QCURVE:
					pts = [(point.x, point.y) for point in segment.points]
					pen.qCurveTo(*pts)
				else:
					assert 0, "unsupported segment type"
			pts = [(point.x, point.y) for point in self.segments[0].points]
			pen.qCurveTo(*pts)
			pen.closePath()
		else:
			if firstType == MOVE and (firstOn.x, firstOn.y) == (lastOn.x, lastOn.y):
				closed = True
			else:
				closed = True
			for segment in self.segments:
				segmentType = segment.type
				pt = segment.onCurve.x, segment.onCurve.y
				if segmentType == MOVE:
					pen.moveTo(pt)
				elif segmentType == LINE:
					pen.lineTo(pt)
				elif segmentType == CURVE:
					pts = [(point.x, point.y) for point in segment.points]
					pen.curveTo(*pts)
				elif segmentType == QCURVE:
					pts = [(point.x, point.y) for point in segment.points]
					pen.qCurveTo(*pts)
				else:
					assert 0, "unsupported segment type"
			if closed:
				pen.closePath()
			else:
				pen.endPath()
	
	def drawPoints(self, pen):
		"""draw the object with a point pen"""
		pen.beginPath()
		lastOn = self.segments[-1].onCurve
		didLastOn = False
		flQCurveException = False
		lastIndex = len(self.segments) - 1
		for i in range(len(self.segments)):
			segment = self.segments[i]
			segmentType = segment.type
			# the new protocol states that we start with an onCurve
			# so, if we have a move and a nd a last point overlapping,
			# add the last point to the beginning and skip the move
			if segmentType == MOVE and (segment.onCurve.x, segment.onCurve.y) == (lastOn.x, lastOn.y):
				point = self.segments[-1].onCurve
				name = getattr(segment.onCurve, 'name', None)
				pen.addPoint((point.x, point.y), point.type, smooth=self.segments[-1].smooth, name=name)
				didLastOn = True
				continue
			# this is an exception for objectsFL
			# the problem is that quad contours are
			# represented differently that they are in
			# objectsRF:
			#	FL: [qcurve, qcurve, qcurve, qcurve]
			#	RF: [move, qcurve, qcurve, qcurve, qcurve]
			# so, we need to catch this, and shift the offCurves to
			# to the end of the contour
			if i == 0 and segmentType == QCURVE:
				flQCurveException = True
			if segmentType == MOVE:
				segmentType = LINE
			## the offCurves
			if i == 0 and flQCurveException:
				pass
			else:
				for point in segment.offCurve:
					name = getattr(point, 'name', None)
					pen.addPoint((point.x, point.y), segmentType=None, smooth=None, name=name, selected=point.selected)
			## the onCurve
			# skip the last onCurve if it was used as the move
			if i == lastIndex and didLastOn:
				continue
			point = segment.onCurve
			name = getattr(point, 'name', None)
			pen.addPoint((point.x, point.y), segmentType, smooth=segment.smooth, name=name, selected=point.selected)
		# if we have the special qCurve case with objectsFL
		# take care of the offCurves associated with the first contour
		if flQCurveException:
			for point in self.segments[0].offCurve:
				name = getattr(point, 'name', None)
				pen.addPoint((point.x, point.y), segmentType=None, smooth=None, name=name, selected=point.selected)
		pen.endPath()
		
	def move(self, pt):
		"""move the contour"""
		#this will be faster if we go straight to the points
		for point in self.points:
			point.move(pt)
	
	def scale(self, pt, center=(0, 0)):
		"""scale the contour"""
		#this will be faster if we go straight to the points
		for point in self.points:
			point.scale(pt, center=center)
	
	def transform(self, matrix):
		"""Transform this contour.
		Use a Transform matrix object from
		robofab.transform"""
		n = []
		for s in self.segments:
			s.transform(matrix)
			
	def rotate(self, angle, offset=None):
		"""rotate the contour"""
		from fontTools.misc.transform import Identity
		radAngle = angle / DEGREE	# convert from degrees to radians
		if offset is None:
			offset = (0,0)
		rT = Identity.translate(offset[0], offset[1])
		rT = rT.rotate(radAngle)
		self.transform(rT)	
	
	def skew(self, angle, offset=None):
		"""skew the contour"""
		from fontTools.misc.transform import Identity
		radAngle = angle / DEGREE	# convert from degrees to radians
		if offset is None:
			offset = (0,0)
		rT = Identity.translate(offset[0], offset[1])
		rT = rT.skew(radAngle)
		self.transform(rT)
	
	def pointInside(self, pt, evenOdd=0):
		"""determine if the point is inside or ouside of the contour"""
		from fontTools.pens.pointInsidePen import PointInsidePen
		glyph = self.getParent()
		font = glyph.getParent()
		piPen = PointInsidePen(glyphSet=font, testPoint=pt, evenOdd=evenOdd)
		self.draw(piPen)
		return piPen.getResult()
			
	def autoStartSegment(self):
		"""automatically set the lower left point of the contour as the first point."""
		#adapted from robofog
		startIndex = 0
		startSegment = self.segments[0]
		for i in range(len(self.segments)):
			segment = self.segments[i]
			startOn = startSegment.onCurve
			on = segment.onCurve
			if on.y <= startOn.y:
				if on.y == startOn.y:
					if on.x < startOn.x:
						startSegment = segment
						startIndex = i
				else:
					startSegment = segment
					startIndex = i
		if startIndex != 0:
			self.setStartSegment(startIndex)
		
	def appendBPoint(self, pointType, anchor, bcpIn=(0, 0), bcpOut=(0, 0)):
		"""append a bPoint to the contour"""
		self.insertBPoint(len(self.segments), pointType=pointType, anchor=anchor, bcpIn=bcpIn, bcpOut=bcpOut)
		
	def insertBPoint(self, index, pointType, anchor, bcpIn=(0, 0), bcpOut=(0, 0)):
		"""insert a bPoint at index on the contour"""
		#insert a CURVE point that we can work with
		nextSegment = self._nextSegment(index-1)
		if nextSegment.type == QCURVE:
			return	
		if nextSegment.type == MOVE:
			prevSegment = self.segments[index-1]
			prevOn = prevSegment.onCurve
			if bcpIn != (0, 0):
				new = self.appendSegment(CURVE, [(prevOn.x, prevOn.y), absoluteBCPIn(anchor, bcpIn), anchor], smooth=False)
				if pointType == CURVE:
					new.smooth = True
			else:
				new = self.appendSegment(LINE, [anchor], smooth=False)
			#if the user wants an outgoing bcp, we must add a CURVE ontop of the move
			if bcpOut != (0, 0):
				nextOn = nextSegment.onCurve
				self.appendSegment(CURVE, [absoluteBCPOut(anchor, bcpOut), (nextOn.x, nextOn.y), (nextOn.x, nextOn.y)], smooth=False)
		else:
			#handle the bcps
			if nextSegment.type != CURVE:
				prevSegment = self.segments[index-1]
				prevOn = prevSegment.onCurve
				prevOutX, prevOutY = (prevOn.x, prevOn.y)
			else:
				prevOut = nextSegment.offCurve[0]
				prevOutX, prevOutY = (prevOut.x, prevOut.y)
			self.insertSegment(index, segmentType=CURVE, points=[(prevOutX, prevOutY), anchor, anchor], smooth=False)
			newSegment = self.segments[index]
			prevSegment = self._prevSegment(index)
			nextSegment = self._nextSegment(index)
			if nextSegment.type == MOVE:
				raise RoboFabError, 'still working out curving at the end of a contour'
			elif nextSegment.type == QCURVE:
				return
			#set the new incoming bcp
			newIn = newSegment.offCurve[1]
			nIX, nIY = absoluteBCPIn(anchor, bcpIn)
			newIn.x = nIX
			newIn.y = nIY
			#set the new outgoing bcp
			hasCurve = True
			if nextSegment.type != CURVE:
				if bcpOut != (0, 0):
					nextSegment.type = CURVE
					hasCurve = True
				else:
					hasCurve = False
			if hasCurve:
				newOut = nextSegment.offCurve[0]
				nOX, nOY = absoluteBCPOut(anchor, bcpOut)
				newOut.x = nOX
				newOut.y = nOY
			#now check to see if we can convert the CURVE segment to a LINE segment
			newAnchor = newSegment.onCurve
			newA = newSegment.offCurve[0]
			newB = newSegment.offCurve[1]
			nextAnchor = nextSegment.onCurve
			prevAnchor = prevSegment.onCurve
			if (prevAnchor.x, prevAnchor.y) == (newA.x, newA.y) and (newAnchor.x, newAnchor.y) == (newB.x, newB.y):
				newSegment.type = LINE
			#the user wants a smooth segment		
			if pointType == CURVE:
				newSegment.smooth = True


class BaseSegment(RBaseObject):
	
	"""Base class for all segment objects"""
	
	def __init__(self):
		self.changed = False
	
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		contourIndex = "unknown_contour"
		contourParent = self.getParent()
		if contourParent is not None:
			try:
				contourIndex = `contourParent.index`
			except AttributeError: pass
			glyphParent = contourParent.getParent()
			if glyphParent is not None:
				try:
					glyph = glyphParent.name
				except AttributeError: pass
				fontParent = glyphParent.getParent()
				if fontParent is not None:
					try:
						font = fontParent.info.postscriptFullName
					except AttributeError: pass
		try:
			idx = `self.index`
		except ValueError:
			idx = "XXX"
		return "<RSegment for %s.%s[%s][%s]>"%(font, glyph, contourIndex, idx)
		
	def __mul__(self, factor):
		warn("Segment math has been deprecated and is slated for removal.", DeprecationWarning)
		n = self.copy()
		n.points = []
		for i in range(len(self.points)):
			n.points.append(self.points[i] * factor)
		n._setParentTree()
		return n

	__rmul__ = __mul__

	def __add__(self, other):
		warn("Segment math has been deprecated and is slated for removal.", DeprecationWarning)
		n = self.copy()
		n.points = []
		for i in range(len(self.points)):
			n.points.append(self.points[i] + other.points[i])
		return n

	def __sub__(self, other):
		warn("Segment math has been deprecated and is slated for removal.", DeprecationWarning)
		n = self.copy()
		n.points = []
		for i in range(len(self.points)):
			n.points.append(self.points[i] - other.points[i])
		return n
		
	def _hasChanged(self):
		"""mark the object and it's parent as changed"""
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()
	
	def copy(self, aParent=None):
		"""Duplicate this segment"""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		dont = ['_object', 'getParent', 'offCurve', 'onCurve']
		for k in self.__dict__.keys():
			ok = True
			if k in dont:
				continue
			if k == "points":
				dup = []
				for i in self.points:
					dup.append(i.copy(n))
			elif isinstance(self.__dict__[k], (RBaseObject, BaseLib)):
				dup = self.__dict__[k].copy(n)
			else:
				dup = copy.deepcopy(self.__dict__[k])
			if ok:
				setattr(n, k, dup)
		return n
	
	def _setParentTree(self):
		"""Set the parents of all contained and dependent objects (and their dependents) right."""
		for item in self.points:
			item.setParent(self)

	def round(self):
		"""round all points in the segment"""
		for point in self.points:
			point.round()
	
	def move(self, pt):
		"""move the segment"""
		for point in self.points:
			point.move(pt)
	
	def scale(self, pt, center=(0, 0)):
		"""scale the segment"""
		for point in self.points:
			point.scale(pt, center=center)

	def transform(self, matrix):
		"""Transform this segment.
		Use a Transform matrix object from
		robofab.transform"""
		n = []
		for p in self.points:
			p.transform(matrix)
	
	def _get_onCurve(self):
		return self.points[-1]
	
	def _get_offCurve(self):
		return self.points[:-1]
		
	offCurve = property(_get_offCurve, doc="on curve point for the segment")
	onCurve = property(_get_onCurve, doc="list of off curve points for the segment")


		
class BasePoint(RBaseObject):
	
	"""Base class for point objects."""
	
	def __init__(self):
		#RBaseObject.__init__(self)
		self.changed = False		# if the object needs to be saved
		self.selected = False
		
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		contourIndex = "unknown_contour"
		segmentIndex = "unknown_segment"
		segmentParent = self.getParent()
		if segmentParent is not None:
			try:
				segmentIndex = `segmentParent.index`
			except AttributeError: pass
			contourParent = self.getParent().getParent()
			if contourParent is not None:
				try:
					contourIndex = `contourParent.index`
				except AttributeError: pass
				glyphParent = contourParent.getParent()
				if glyphParent is not None:
					try:
						glyph = glyphParent.name
					except AttributeError: pass
					fontParent = glyphParent.getParent()
					if fontParent is not None:
						try:
							font = fontParent.info.postscriptFullName
						except AttributeError: pass
		return "<RPoint for %s.%s[%s][%s]>"%(font, glyph, contourIndex, segmentIndex)
	
	def __add__(self, other):
		warn("Point math has been deprecated and is slated for removal.", DeprecationWarning)
		#Add one point to another
		n = self.copy()
		n.x, n.y = addPt((self.x, self.y), (other.x, other.y))
		return n

	def __sub__(self, other):
		warn("Point math has been deprecated and is slated for removal.", DeprecationWarning)
		#Subtract one point from another
		n = self.copy()
		n.x, n.y = subPt((self.x, self.y), (other.x, other.y))
		return n

	def __mul__(self, factor):
		warn("Point math has been deprecated and is slated for removal.", DeprecationWarning)
		#Multiply the point with factor. Factor can be a tuple of 2 *(f1, f2)
		n = self.copy()
		n.x, n.y = mulPt((self.x, self.y), factor)
		return n
		
	__rmul__ = __mul__

	def _hasChanged(self):
		#mark the object and it's parent as changed
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()
	
	def copy(self, aParent=None):
		"""Duplicate this point"""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		dont = ['getParent', 'offCurve', 'onCurve']
		for k in self.__dict__.keys():
			ok = True
			if k in dont:
				continue
			elif isinstance(self.__dict__[k], (RBaseObject, BaseLib)):
				dup = self.__dict__[k].copy(n)
			else:
				dup = copy.deepcopy(self.__dict__[k])
			if ok:
				setattr(n, k, dup)
		return n

	def select(self, state=True):
		"""Set the selection of this point.
		XXXX This method should be a lot more versatile, dealing with
		different kinds of selection, select the bcp's seperately etc.
		But that's for later when we need it more. For now it's just 
		one flag for the entire thing."""
		self.selected = state
	
	def round(self):
		"""round the values in the point"""
		self.x, self.y = roundPt((self.x, self.y))

	def move(self, pt):
		"""Move the point"""
		self.x, self.y = addPt((self.x, self.y), pt)
		
	def scale(self, pt, center=(0, 0)):
		"""scale the point"""
		nX, nY = _scalePointFromCenter((self.x, self.y), pt, center)
		self.x = nX
		self.y = nY

	def transform(self, matrix):
		"""Transform this point. Use a Transform matrix
		object from fontTools.misc.transform"""
		self.x, self.y = matrix.transformPoint((self.x, self.y))


class BaseBPoint(RBaseObject):

	"""Base class for bPoints objects."""

	def __init__(self):
		RBaseObject.__init__(self)
		self.changed = False		# if the object needs to be saved
		self.selected = False
		
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		contourIndex = "unknown_contour"
		segmentIndex = "unknown_segment"
		segmentParent = self.getParent()
		if segmentParent is not None:
			try:
				segmentIndex = `segmentParent.index`
			except AttributeError: pass
			contourParent = segmentParent.getParent()
			if contourParent is not None:
				try:
					contourIndex = `contourParent.index`
				except AttributeError: pass
				glyphParent = contourParent.getParent()
				if glyphParent is not None:
					try:
						glyph = glyphParent.name
					except AttributeError: pass
					fontParent = glyphParent.getParent()
					if fontParent is not None:
						try:
							font = fontParent.info.postscriptFullName
						except AttributeError: pass
		return "<RBPoint for %s.%s[%s][%s][%s]>"%(font, glyph, contourIndex, segmentIndex, `self.index`)

	
	def __add__(self, other):
		warn("BPoint math has been deprecated and is slated for removal.", DeprecationWarning)
		#Add one bPoint to another
		n = self.copy()
		n.anchor = addPt(self.anchor, other.anchor)
		n.bcpIn = addPt(self.bcpIn, other.bcpIn)
		n.bcpOut = addPt(self.bcpOut, other.bcpOut)
		return n

	def __sub__(self, other):
		warn("BPoint math has been deprecated and is slated for removal.", DeprecationWarning)
		#Subtract one bPoint from another
		n = self.copy()
		n.anchor = subPt(self.anchor, other.anchor)
		n.bcpIn = subPt(self.bcpIn, other.bcpIn)
		n.bcpOut = subPt(self.bcpOut, other.bcpOut)
		return n

	def __mul__(self, factor):
		warn("BPoint math has been deprecated and is slated for removal.", DeprecationWarning)
		#Multiply the bPoint with factor. Factor can be a tuple of 2 *(f1, f2)
		n = self.copy()
		n.anchor = mulPt(self.anchor, factor)
		n.bcpIn = mulPt(self.bcpIn, factor)
		n.bcpOut = mulPt(self.bcpOut, factor)
		return n
		
	__rmul__ = __mul__

	def _hasChanged(self):
		#mark the object and it's parent as changed
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()
	
	def select(self, state=True):
		"""Set the selection of this point.
		XXXX This method should be a lot more versatile, dealing with
		different kinds of selection, select the bcp's seperately etc.
		But that's for later when we need it more. For now it's just 
		one flag for the entire thing."""
		self.selected = state
	
	def round(self):
		"""Round the coordinates to integers"""
		self.anchor = roundPt(self.anchor)
		pSeg = self._parentSegment
		if pSeg.type != MOVE:
			self.bcpIn = roundPt(self.bcpIn)
		if pSeg.getParent()._nextSegment(pSeg.index).type != MOVE:
			self.bcpOut = roundPt(self.bcpOut)
	
	def move(self, pt):
		"""move the bPoint"""
		x, y = pt
		bcpIn = self.bcpIn
		bcpOut = self.bcpOut
		self.anchor = (self.anchor[0] + x, self.anchor[1] + y)
		pSeg = self._parentSegment
		if pSeg.type != MOVE:
			self.bcpIn = bcpIn
		if pSeg.getParent()._nextSegment(pSeg.index).type != MOVE:
			self.bcpOut = bcpOut
	
	def scale(self, pt, center=(0, 0)):
		"""scale the bPoint"""
		x, y = pt
		centerX, centerY = center
		ogCenter = (centerX, centerY)
		scaledCenter = (centerX * x, centerY * y)
		shiftVal = (scaledCenter[0] - ogCenter[0], scaledCenter[1] - ogCenter[1])
		anchor = self.anchor
		bcpIn = self.bcpIn
		bcpOut = self.bcpOut
		self.anchor = ((anchor[0] * x) - shiftVal[0], (anchor[1] * y) - shiftVal[1])
		pSeg = self._parentSegment
		if pSeg.type != MOVE:
			self.bcpIn = ((bcpIn[0] * x), (bcpIn[1] * y))
		if pSeg.getParent()._nextSegment(pSeg.index).type != MOVE:
			self.bcpOut = ((bcpOut[0] * x), (bcpOut[1] * y))
	
	def transform(self, matrix):
		"""Transform this point. Use a Transform matrix
		object from fontTools.misc.transform"""
		self.anchor = matrix.transformPoint(self.anchor)
		pSeg = self._parentSegment
		if pSeg.type != MOVE:
			self.bcpIn = matrix.transformPoint(self.bcpIn)
		if pSeg.getParent()._nextSegment(pSeg.index).type != MOVE:
			self.bcpOut = matrix.transformPoint(self.bcpOut)

	def _get__anchorPoint(self):
		return self._parentSegment.onCurve
	
	_anchorPoint = property(_get__anchorPoint, doc="the oncurve point in the parent segment")

	def _get_anchor(self):
		point = self._anchorPoint
		return (point.x, point.y)
	
	def _set_anchor(self, value):
		x, y = value
		point = self._anchorPoint
		point.x = x
		point.y = y
		
	anchor = property(_get_anchor, _set_anchor, doc="the position of the anchor")

	def _get_bcpIn(self):
		pSeg = self._parentSegment
		pCount = len(pSeg.offCurve)
		if pCount == 2:
			p = pSeg.offCurve[1]
			pOn = pSeg.onCurve
			return relativeBCPIn((pOn.x, pOn.y), (p.x, p.y))
		else:
			return (0, 0)
	
	def _set_bcpIn(self, value):
		x, y = (absoluteBCPIn(self.anchor, value))
		pSeg = self._parentSegment
		if pSeg.type == MOVE:
			#the user wants to have a bcp leading into the MOVE
			if value == (0, 0) and self.bcpOut == (0, 0):
				#we have a straight line between the two anchors
				pass
			else:
				#we need to insert a new CURVE segment ontop of the move
				contour = self._parentSegment.getParent()
				#set the prev segment outgoing bcp to the onCurve
				prevSeg = contour._prevSegment(self._parentSegment.index)
				prevOn = prevSeg.onCurve
				contour.appendSegment(CURVE, [(prevOn.x, prevOn.y), (x, y), self.anchor], smooth=False)
		else:
			pCount = len(pSeg.offCurve)
			if pCount == 2:
				#if the two points in the offCurvePoints list are located at the
				#anchor coordinates we can switch to a LINE segment type
				if value == (0, 0) and self.bcpOut == (0, 0):
					pSeg.type = LINE
					pSeg.smooth = False
				else:
					pSeg.offCurve[1].x = x
					pSeg.offCurve[1].y = y
			elif value != (0, 0):
				pSeg.type = CURVE
				pSeg.offCurve[1].x = x
				pSeg.offCurve[1].y = y
			
	bcpIn = property(_get_bcpIn, _set_bcpIn, doc="the (x,y) for the incoming bcp")

	def _get_bcpOut(self):
		pSeg = self._parentSegment
		nextSeg = pSeg.getParent()._nextSegment(pSeg.index)
		nsCount = len(nextSeg.offCurve)
		if nsCount == 2:
			p = nextSeg.offCurve[0]
			return relativeBCPOut(self.anchor, (p.x, p.y))
		else:
			return (0, 0)
			
	def _set_bcpOut(self, value):
		x, y = (absoluteBCPOut(self.anchor, value))
		pSeg = self._parentSegment
		nextSeg = pSeg.getParent()._nextSegment(pSeg.index)
		if nextSeg.type == MOVE:
			if value == (0, 0) and self.bcpIn == (0, 0):
				pass
			else:				
				#we need to insert a new CURVE segment ontop of the move
				contour = self._parentSegment.getParent()
				nextOn = nextSeg.onCurve
				contour.appendSegment(CURVE, [(x, y), (nextOn.x, nextOn.y), (nextOn.x, nextOn.y)], smooth=False)
		else:
			nsCount = len(nextSeg.offCurve)
			if nsCount == 2:
				#if the two points in the offCurvePoints list are located at the
				#anchor coordinates we can switch to a LINE segment type
				if value == (0, 0) and self.bcpIn == (0, 0):
					nextSeg.type = LINE
					nextSeg.smooth = False
				else:
					nextSeg.offCurve[0].x = x
					nextSeg.offCurve[0].y = y
			elif value != (0, 0):
				nextSeg.type = CURVE
				nextSeg.offCurve[0].x = x
				nextSeg.offCurve[0].y = y
		
	bcpOut = property(_get_bcpOut, _set_bcpOut, doc="the (x,y) for the outgoing bcp")

	def _get_type(self):
		pType = self._parentSegment.type
		bpType = CORNER
		if pType == CURVE:
			if self._parentSegment.smooth:
				bpType = CURVE
		return bpType
	
	def _set_type(self, pointType):
		pSeg = self._parentSegment
		segType = pSeg.type
		#user wants a curve where there is a line
		if pointType == CURVE and segType == LINE:
			pSeg.type = CURVE
			pSeg.smooth = True
		#the anchor is a curve segment. so, all we need to do is turn the smooth off
		elif pointType == CORNER and segType == CURVE:
			pSeg.smooth = False

	type = property(_get_type, _set_type, doc="the type of bPoint, either 'corner' or 'curve'")

	
class BaseComponent(RBaseObject):
	
	"""Base class for all component objects."""
	
	def __init__(self):
		RBaseObject.__init__(self)
		self.changed = False		# if the object needs to be saved
		self.selected = False
		
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		glyphParent = self.getParent()
		if glyphParent is not None:
			try:
				glyph = glyphParent.name
			except AttributeError: pass
			fontParent = glyphParent.getParent()
			if fontParent is not None:
				try:
					font = fontParent.info.postscriptFullName
				except AttributeError: pass
		return "<RComponent for %s.%s.components[%s]>"%(font, glyph, `self.index`)
		
	def _hasChanged(self):
		"""mark the object and it's parent as changed"""
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()
	
	def copy(self, aParent=None):
		"""Duplicate this component."""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		dont = ['getParent', '_object']
		for k in self.__dict__.keys():
			if k in dont:
				continue
			elif isinstance(self.__dict__[k], (RBaseObject, BaseLib)):
				dup = self.__dict__[k].copy(n)
			else:
				dup = copy.deepcopy(self.__dict__[k])
			setattr(n, k, dup)
		return n

	def __add__(self, other):
		warn("Component math has been deprecated and is slated for removal.", DeprecationWarning)
		#Add one Component to another
		n = self.copy()
		n.offset = addPt(self.offset, other.offset)
		n.scale = addPt(self.scale, other.scale)
		return n

	def __sub__(self, other):
		warn("Component math has been deprecated and is slated for removal.", DeprecationWarning)
		#Subtract one Component from another
		n = self.copy()
		n.offset = subPt(self.offset, other.offset)
		n.scale = subPt(self.scale, other.scale)
		return n

	def __mul__(self, factor):
		warn("Component math has been deprecated and is slated for removal.", DeprecationWarning)
		#Multiply the Component with factor. Factor can be a tuple of 2 *(f1, f2)
		n = self.copy()
		n.offset = mulPt(self.offset, factor)
		n.scale = mulPt(self.scale, factor)
		return n
		
	__rmul__ = __mul__
	
	def _get_box(self):
		parentGlyph = self.getParent()
		# the component is an orphan
		if parentGlyph is None:
			return None
		parentFont = parentGlyph.getParent()
		# the glyph that contains the component
		# does not hae a parent
		if parentFont is None:
			return None
		# the font does not have a glyph
		# that matches the glyph that
		# this component references
		if not parentFont.has_key(self.baseGlyph):
			return None
		return _box(self, parentFont)
	
	box = property(_get_box, doc="the bounding box of the component: (xMin, yMin, xMax, yMax)")

	def round(self):
		"""round the offset values"""
		self.offset = roundPt(self.offset)
		self._hasChanged()
	
	def draw(self, pen):
		"""Segment pen drawing method."""
		if isinstance(pen, AbstractPen):
			# It's a FontTools pen, which for addComponent is identical
			# to PointPen.
			self.drawPoints(pen)
		else:
			# It's an "old" 'Fab pen
			pen.addComponent(self.baseGlyph, self.offset, self.scale)
	
	def drawPoints(self, pen):
		"""draw the object with a point pen"""
		oX, oY = self.offset
		sX, sY = self.scale
		#xScale, xyScale, yxScale, yScale, xOffset, yOffset
		pen.addComponent(self.baseGlyph, (sX, 0, 0, sY, oX, oY))


class BaseAnchor(RBaseObject):
	
	"""Base class for all anchor point objects."""
	
	def __init__(self):
		RBaseObject.__init__(self)
		self.changed = False		# if the object needs to be saved
		self.selected = False
	
	def __repr__(self):
		font = "unnamed_font"
		glyph = "unnamed_glyph"
		glyphParent = self.getParent()
		if glyphParent is not None:
			try:
				glyph = glyphParent.name
			except AttributeError: pass
			fontParent = glyphParent.getParent()
			if fontParent is not None:
				try:
					font = fontParent.info.postscriptFullName
				except AttributeError: pass
		return "<RAnchor for %s.%s.anchors[%s]>"%(font, glyph, `self.index`)

	def __add__(self, other):
		warn("Anchor math has been deprecated and is slated for removal.", DeprecationWarning)
		#Add one anchor to another
		n = self.copy()
		n.x, n.y = addPt((self.x, self.y), (other.x, other.y))
		return n

	def __sub__(self, other):
		warn("Anchor math has been deprecated and is slated for removal.", DeprecationWarning)
		#Substract one anchor from another
		n = self.copy()
		n.x, n.y = subPt((self.x, self.y), (other.x, other.y))
		return n

	def __mul__(self, factor):
		warn("Anchor math has been deprecated and is slated for removal.", DeprecationWarning)
		#Multiply the anchor with factor. Factor can be a tuple of 2 *(f1, f2)
		n = self.copy()
		n.x, n.y = mulPt((self.x, self.y), factor)
		return n
		
	__rmul__ = __mul__

	def _hasChanged(self):
		#mark the object and it's parent as changed
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()

	def copy(self, aParent=None):
		"""Duplicate this anchor."""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		dont = ['getParent', '_object']
		for k in self.__dict__.keys():
			if k in dont:
				continue
			elif isinstance(self.__dict__[k], (RBaseObject, BaseLib)):
				dup = self.__dict__[k].copy(n)
			else:
				dup = copy.deepcopy(self.__dict__[k])
			setattr(n, k, dup)
		return n

	def round(self):
		"""round the values in the anchor"""
		self.x, self.y = roundPt((self.x, self.y))
		self._hasChanged()
		
	def draw(self, pen):
		"""Draw the object onto a segment pen"""
		if isinstance(pen, AbstractPen):
			# It's a FontTools pen
			pen.moveTo((self.x, self.y))
			pen.endPath()
		else:
			# It's an "old" 'Fab pen
			pen.addAnchor(self.name, (self.x, self.y))
	
	def drawPoints(self, pen):
		"""draw the object with a point pen"""
		pen.beginPath()
		pen.addPoint((self.x, self.y), segmentType="move", smooth=False, name=self.name)
		pen.endPath()
		
	def move(self, pt):
		"""Move the anchor"""
		x, y = pt
		pX, pY = self.position
		self.position = (pX+x, pY+y)
		
	def scale(self, pt, center=(0, 0)):
		"""scale the anchor"""
		pos = self.position
		self.position = _scalePointFromCenter(pos, pt, center)

	def transform(self, matrix):
		"""Transform this anchor. Use a Transform matrix
		object from fontTools.misc.transform"""
		self.x, self.y = matrix.transformPoint((self.x, self.y))


class BaseGuide(RBaseObject):
	
	"""Base class for all guide objects."""
	
	def __init__(self):
		RBaseObject.__init__(self)
		self.changed = False		# if the object needs to be saved
		self.selected = False


class BaseInfo(RBaseObject):

	_baseAttributes = ["_object", "changed", "selected", "getParent"]
	_deprecatedAttributes = ufoLib.deprecatedFontInfoAttributesVersion2
	_infoAttributes = ufoLib.fontInfoAttributesVersion2
	# subclasses may define a list of environment
	# specific attributes that can be retrieved or set.
	_environmentAttributes = []
	# subclasses may define a list of attributes
	# that should not follow the standard get/set
	# order provided by __setattr__ and __getattr__.
	# for these attributes, the environment specific
	# set and get methods must handle this value
	# without any pre-call validation.
	# (yeah. this is because of some FontLab dumbness.)
	_environmentOverrides = []

	def __setattr__(self, attr, value):
		# check to see if the attribute has been
		# deprecated. if so, warn the caller and
		# update the attribute and value.
		if attr in self._deprecatedAttributes:
			newAttr, newValue = ufoLib.convertFontInfoValueForAttributeFromVersion1ToVersion2(attr, value)
			note = "The %s attribute has been deprecated. Use the new %s attribute." % (attr, newAttr)
			warn(note, DeprecationWarning)
			attr = newAttr
			value = newValue
		# setting a known attribute
		if attr in self._infoAttributes or attr in self._environmentAttributes:
			# lightly test the validity of the value
			if value is not None:
				isValidValue = ufoLib.validateFontInfoVersion2ValueForAttribute(attr, value)
				if not isValidValue:
					raise RoboFabError("Invalid value (%s) for attribute (%s)." % (repr(value), attr))
			# use the environment specific info attr set
			# method if it is defined.
			if hasattr(self, "_environmentSetAttr"):
				self._environmentSetAttr(attr, value)
			# fallback to super
			else:
				super(BaseInfo, self).__setattr__(attr, value)
		# unknown attribute, test to see if it is a python attr
		elif attr in self.__dict__ or attr in self._baseAttributes:
			super(BaseInfo, self).__setattr__(attr, value)
		# raise an attribute error
		else:
			raise AttributeError("Unknown attribute %s." % attr)

	# subclasses with environment specific attr setting can
	# implement this method. __setattr__ will call it if present.
	# def _environmentSetAttr(self, attr, value):
	# 	pass

	def __getattr__(self, attr):
		if attr in self._environmentOverrides:
			return self._environmentGetAttr(attr)
		# check to see if the attribute has been
		# deprecated. if so, warn the caller and
		# flag the value as needing conversion.
		needValueConversionTo1 = False
		if attr in self._deprecatedAttributes:
			oldAttr = attr
			oldValue = attr
			newAttr, x = ufoLib.convertFontInfoValueForAttributeFromVersion1ToVersion2(attr, None)
			note = "The %s attribute has been deprecated. Use the new %s attribute." % (attr, newAttr)
			warn(note, DeprecationWarning)
			attr = newAttr
			needValueConversionTo1 = True
		# getting a known attribute
		if attr in self._infoAttributes or attr in self._environmentAttributes:
			# use the environment specific info attr get
			# method if it is defined.
			if hasattr(self, "_environmentGetAttr"):
				value = self._environmentGetAttr(attr)
			# fallback to super
			else:
				try:
					value = super(BaseInfo, self).__getattribute__(attr)
				except AttributeError:
					return None
			if needValueConversionTo1:
				oldAttr, value = ufoLib.convertFontInfoValueForAttributeFromVersion2ToVersion1(attr, value)
			return value
		# raise an attribute error
		else:
			raise AttributeError("Unknown attribute %s." % attr)

		# subclasses with environment specific attr retrieval can
		# implement this method. __getattr__ will call it if present.
		# it should return the requested value.
		# def _environmentGetAttr(self, attr):
		# 	pass

class BaseFeatures(RBaseObject):

	def __init__(self):
		RBaseObject.__init__(self)
		self._text = ""

	def _get_text(self):
		return self._text

	def _set_text(self, value):
		assert isinstance(value, basestring)
		self._text = value

	text = property(_get_text, _set_text, doc="raw feature text.")


class BaseGroups(dict):
	
	"""Base class for all RFont.groups objects"""
	
	def __init__(self):
		pass
		
	def __repr__(self):
		font = "unnamed_font"
		fontParent = self.getParent()
		if fontParent is not None:
			try:
				font = fontParent.info.postscriptFullName
			except AttributeError: pass
		return "<RGroups for %s>"%font

	def getParent(self):
		"""this method will be overwritten with a weakref if there is a parent."""
		pass
	
	def setParent(self, parent):
		import weakref
		self.__dict__['getParent'] = weakref.ref(parent)
	
	def __setitem__(self, key, value):
		#override base class to insure proper data is being stored
		if not isinstance(key, str):
			raise RoboFabError, 'key must be a string'
		if not isinstance(value, list):
			raise RoboFabError, 'group must be a list'
		super(BaseGroups, self).__setitem__(key, value)
		
	def findGlyph(self, glyphName):
		"""return a list of all groups contianing glyphName"""
		found = []
		for i in self.keys():
			l = self[i]
			if glyphName in l:
				found.append(i)
		return found
		

class BaseLib(dict):
	
	"""Base class for all lib objects"""
	
	def __init__(self):
		pass
	
	def __repr__(self):
		#this is a doozy!
		parent = "unknown_parent"
		parentObject = self.getParent()
		if parentObject is not None:
			#do we have a font?
			try:
				parent = parentObject.info.postscriptFullName
			except AttributeError:
				#or do we have a glyph?
				try:
					parent = parentObject.name
				#we must be an orphan
				except AttributeError: pass
		return "<RLib for %s>"%parent

	def getParent(self):
		"""this method will be overwritten with a weakref if there is a parent."""
		pass
	
	def setParent(self, parent):
		import weakref
		self.__dict__['getParent'] = weakref.ref(parent)

	def copy(self, aParent=None):
		"""Duplicate this lib."""
		n = self.__class__()
		if aParent is not None:
			n.setParent(aParent)
		elif self.getParent() is not None:
			n.setParent(self.getParent())
		for k in self.keys():
			n[k] = copy.deepcopy(self[k])
		return n
	
		
class BaseKerning(RBaseObject):
	
	"""Base class for all kerning objects. Object behaves like a dict but has
	some special kerning specific tricks."""
	
	def __init__(self, kerningDict=None):
		if not kerningDict:
			kerningDict = {}
		self._kerning = kerningDict
		self.changed = False		# if the object needs to be saved
	
	def __repr__(self):
		font = "unnamed_font"
		fontParent = self.getParent()
		if fontParent is not None:
			try:
				font = fontParent.info.postscriptFullName
			except AttributeError: pass
		return "<RKerning for %s>"%font
			
	def __getitem__(self, key):
		if isinstance(key, tuple):
			pair = key
			return self.get(pair)
		elif isinstance(key, str):
			raise RoboFabError, 'kerning pair must be a tuple: (left, right)'
		else:
			keys = self.keys()
			if key > len(keys):
				raise IndexError
			keys.sort()
			pair = keys[key]
		if not self._kerning.has_key(pair):
			raise IndexError
		else:
			return pair
	
	def __setitem__(self, pair, value):
		if not isinstance(pair, tuple):
			raise RoboFabError, 'kerning pair must be a tuple: (left, right)'
		else:
			if len(pair) != 2:
				raise RoboFabError, 'kerning pair must be a tuple: (left, right)'
			else:
				if value == 0:
					if self._kerning.get(pair) is not None:
						del self._kerning[pair]
				else:
					self._kerning[pair] = value
				self._hasChanged()
		
	def __len__(self):
		return len(self._kerning.keys())
		
	def _hasChanged(self):
		"""mark the object and it's parent as changed"""
		self.setChanged(True)
		if self.getParent() is not None:
			self.getParent()._hasChanged()
	
	def keys(self):
		"""return list of kerning pairs"""
		return self._kerning.keys()
		
	def values(self):
		"""return a list of kerning values"""
		return self._kerning.values()
	
	def items(self):
		"""return a list of kerning items"""
		return self._kerning.items()
	
	def has_key(self, pair):
		return self._kerning.has_key(pair)
	
	def get(self, pair, default=None):
		"""get a value. return None if the pair does not exist"""
		value = self._kerning.get(pair, default)
		return value
		
	def remove(self, pair):
		"""remove a kerning pair"""
		self[pair] = 0
	
	def getAverage(self):
		"""return average of all kerning pairs"""
		if len(self) == 0:
			return 0
		value = 0
		for i in self.values():
			value = value + i
		return value / float(len(self))
	
	def getExtremes(self):
		"""return the lowest and highest kerning values"""
		if len(self) == 0:
			return 0
		values = self.values()
		values.append(0)
		values.sort() 
		return (values[0], values[-1])
		
	def update(self, kerningDict):
		"""replace kerning data with the data in the given kerningDict"""
		for pair in kerningDict.keys():
			self[pair] = kerningDict[pair]
	
	def clear(self):
		"""clear all kerning"""
		self._kerning = {}
		
	def add(self, value):
		"""add value to all kerning pairs"""
		for pair in self.keys():
			self[pair] = self[pair] + value
		
	def scale(self, value):
		"""scale all kernng pairs by value"""
		for pair in self.keys():
			self[pair] = self[pair] * value
			
	def minimize(self, minimum=10):
		"""eliminate pairs with value less than minimum"""
		for pair in self.keys():
			if abs(self[pair]) < minimum:
				self[pair] = 0
	
	def eliminate(self, leftGlyphsToEliminate=None, rightGlyphsToEliminate=None, analyzeOnly=False):
		"""eliminate pairs containing a left glyph that is in the leftGlyphsToEliminate list
		or a right glyph that is in the rightGlyphsToELiminate list.
		sideGlyphsToEliminate can be a string: 'a' or list: ['a', 'b'].
		analyzeOnly will not remove pairs. it will return a count
		of all pairs that would be removed."""
		if analyzeOnly:
			count = 0
		lgte = leftGlyphsToEliminate
		rgte = rightGlyphsToEliminate
		if isinstance(lgte, str):
			lgte = [lgte]
		if isinstance(rgte, str):
			rgte = [rgte]
		for pair in self.keys():
			left, right = pair
			if left in lgte or right in rgte:
				if analyzeOnly:
					count = count + 1
				else:
					self[pair] = 0
		if analyzeOnly:
			return count
		else:
			return None
				
	def interpolate(self, sourceDictOne, sourceDictTwo, value, clearExisting=True):
		"""interpolate the kerning between sourceDictOne
		and sourceDictTwo. clearExisting will clear existing
		kerning first."""
		if isinstance(value, tuple):
			# in case the value is a x, y tuple: use the x only.
			value = value[0]
		if clearExisting:
			self.clear()
		pairs = set(sourceDictOne.keys()) | set(sourceDictTwo.keys())
		for pair in pairs:
			s1 = sourceDictOne.get(pair, 0)
			s2 = sourceDictTwo.get(pair, 0)
			self[pair] = _interpolate(s1, s2, value)
	
	def round(self, multiple=10):
		"""round the kerning pair values to increments of multiple"""
		for pair in self.keys():
			value = self[pair]
			self[pair] = int(round(value / float(multiple))) * multiple
	
	def occurrenceCount(self, glyphsToCount):
		"""return a dict with glyphs as keys and the number of 
		occurances of that glyph in the kerning pairs as the value
		glyphsToCount can be a string: 'a' or list: ['a', 'b']"""
		gtc = glyphsToCount
		if isinstance(gtc, str):
			gtc = [gtc]
		gtcDict = {}
		for glyph in gtc:
			gtcDict[glyph] = 0
		for pair in self.keys():
			left, right = pair
			if not gtcDict.get(left):
				gtcDict[left] = 0
			if not gtcDict.get(right):
				gtcDict[right] = 0
			gtcDict[left] = gtcDict[left] + 1
			gtcDict[right] = gtcDict[right] + 1
		found = {}
		for glyphName in gtc:
			found[glyphName] = gtcDict[glyphName]
		return found
	
	def getLeft(self, glyphName):
		"""Return a list of kerns with glyphName as left character."""
		hits = []
		for k, v in self.items():
			if k[0] == glyphName:
				hits.append((k, v))
		return hits
				
	def getRight(self, glyphName):
		"""Return a list of kerns with glyphName as left character."""
		hits = []
		for k, v in self.items():
			if k[1] == glyphName:
				hits.append((k, v))
		return hits
		
	def combine(self, kerningDicts, overwriteExisting=True):
		"""combine two or more kerning dictionaries.
		overwrite exsisting duplicate pairs if overwriteExisting=True"""
		if isinstance(kerningDicts, dict):
			kerningDicts = [kerningDicts]
		for kd in kerningDicts:
			for pair in kd.keys():
				exists = self.has_key(pair)
				if exists and overwriteExisting:
					self[pair] = kd[pair]
				elif not exists:
					self[pair] = kd[pair]
					
	def swapNames(self, swapTable):
		"""change glyph names in all kerning pairs based on swapTable.
		swapTable = {'BeforeName':'AfterName', ...}"""
		for pair in self.keys():
			foundInstance = False
			left, right = pair
			if swapTable.has_key(left):
				left = swapTable[left]
				foundInstance = True
			if swapTable.has_key(right):
				right = swapTable[right]
				foundInstance = True
			if foundInstance:
				self[(left, right)] = self[pair]
				self[pair] = 0
				
	def explodeClasses(self, leftClassDict=None, rightClassDict=None, analyzeOnly=False):
		"""turn class kerns into real kerning pairs. classes should
		be defined in dicts: {'O':['C', 'G', 'Q'], 'H':['B', 'D', 'E', 'F', 'I']}.
		analyzeOnly will not remove pairs. it will return a count
		of all pairs that would be added"""
		if not leftClassDict:
			leftClassDict = {}
		if not rightClassDict:
			rightClassDict = {}
		if analyzeOnly:
			count = 0
		for pair in self.keys():
			left, right = pair
			value = self[pair]
			if leftClassDict.get(left) and rightClassDict.get(right):
				allLeft = leftClassDict[left] + [left]
				allRight = rightClassDict[right] + [right]
				for leftSub in allLeft:
					for rightSub in allRight:
						if analyzeOnly:
							count = count + 1
						else:
							self[(leftSub, rightSub)] = value
			elif leftClassDict.get(left) and not rightClassDict.get(right):
				allLeft = leftClassDict[left] + [left]
				for leftSub in allLeft:
					if analyzeOnly:
						count = count + 1
					else:
						self[(leftSub, right)] = value
			elif rightClassDict.get(right) and not leftClassDict.get(left):
				allRight = rightClassDict[right] + [right]
				for rightSub in allRight:
					if analyzeOnly:
						count = count + 1
					else:
						self[(left, rightSub)] = value
		if analyzeOnly:
			return count
		else:
			return None
					
	def implodeClasses(self, leftClassDict=None, rightClassDict=None, analyzeOnly=False):
		"""condense the number of kerning pairs by applying classes.
		this will eliminate all pairs containg the classed glyphs leaving
		pairs that contain the key glyphs behind. analyzeOnly will not
		remove pairs. it will return a count of all pairs that would be removed."""
		if not leftClassDict:
			leftClassDict = {}
		if not rightClassDict:
			rightClassDict = {}
		leftImplode = []
		rightImplode = []
		for value in leftClassDict.values():
			leftImplode = leftImplode + value
		for value in rightClassDict.values():
			rightImplode = rightImplode + value
		analyzed = self.eliminate(leftGlyphsToEliminate=leftImplode, rightGlyphsToEliminate=rightImplode, analyzeOnly=analyzeOnly)
		if analyzeOnly:
			return analyzed
		else:
			return None
		
	def importAFM(self, path, clearExisting=True):
		"""Import kerning pairs from an AFM file. clearExisting=True will
		clear all exising kerning"""
		from fontTools.afmLib import AFM
		#a nasty hack to fix line ending problems
		f = open(path, 'rb')
		text = f.read().replace('\r', '\n')
		f.close()
		f = open(path, 'wb')
		f.write(text)
		f.close()
		#/nasty hack
		kerning = AFM(path)._kerning
		if clearExisting:
			self.clear()
		for pair in kerning.keys():
			self[pair] = kerning[pair]	
				
	def asDict(self, returnIntegers=True):
		"""return the object as a dictionary"""
		if not returnIntegers:
			return self._kerning
		else:
			#duplicate the kerning dict so that we aren't destroying it
			kerning = {}
			for pair in self.keys():
				kerning[pair] = int(round(self[pair]))
			return kerning

	def __add__(self, other):
		new = self.__class__()
		k = set(self.keys()) | set(other.keys())
		for key in k:
			new[key] = self.get(key, 0) + other.get(key, 0)
		return new
	
	def __sub__(self, other):
		new = self.__class__()
		k = set(self.keys()) | set(other.keys())
		for key in k:
			new[key] = self.get(key, 0) - other.get(key, 0)
		return new

	def __mul__(self, factor):
		new = self.__class__()
		for name, value in self.items():
			new[name] = value * factor
		return new
	
	__rmul__ = __mul__

	def __div__(self, factor):
		if factor == 0:
			raise ZeroDivisionError
		return self.__mul__(1.0/factor)
	
