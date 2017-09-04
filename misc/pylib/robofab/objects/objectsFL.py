"""UFO implementation for the objects as used by FontLab 4.5 and higher"""

from FL import *	

from robofab.tools.toolsFL import GlyphIndexTable, NewGlyph
from robofab.objects.objectsBase import BaseFont, BaseGlyph, BaseContour, BaseSegment,\
		BasePoint, BaseBPoint, BaseAnchor, BaseGuide, BaseComponent, BaseKerning, BaseInfo, BaseFeatures, BaseGroups, BaseLib,\
		roundPt, addPt, _box,\
		MOVE, LINE, CORNER, CURVE, QCURVE, OFFCURVE,\
		relativeBCPIn, relativeBCPOut, absoluteBCPIn, absoluteBCPOut,\
		BasePostScriptFontHintValues, postScriptHintDataLibKey, BasePostScriptGlyphHintValues
from robofab.misc import arrayTools
from robofab.pens.flPen import FLPointPen, FLPointContourPen
from robofab import RoboFabError
import os
from robofab.plistlib import Data, Dict, readPlist, writePlist
from StringIO import StringIO
from robofab import ufoLib
from warnings import warn
import datetime
from robofab.tools.fontlabFeatureSplitter import splitFeaturesForFontLab


try:
	set
except NameError:
	from sets import Set as set

# local encoding
if os.name in ["mac", "posix"]:
	LOCAL_ENCODING = "macroman"
else:
	LOCAL_ENCODING = "latin-1"

_IN_UFO_EXPORT = False

# a list of attributes that are to be copied when copying a glyph.
# this is used by glyph.copy and font.insertGlyph
GLYPH_COPY_ATTRS = [
	"name",
	"width",
	"unicodes",
	"note",
	"lib",
	]

# Generate Types
PC_TYPE1 = 'pctype1'
PC_MM = 'pcmm'
PC_TYPE1_ASCII = 'pctype1ascii'
PC_MM_ASCII = 'pcmmascii'
UNIX_ASCII = 'unixascii'
MAC_TYPE1 = 'mactype1'
OTF_CFF = 'otfcff'
OTF_TT = 'otfttf'
MAC_TT = 'macttf'
MAC_TT_DFONT = 'macttdfont'

# doc for these functions taken from: http://dev.fontlab.net/flpydoc/
#			internal name			(FontLab name,		extension)
_flGenerateTypes ={	PC_TYPE1		:	(ftTYPE1,			'pfb'),		# PC Type 1 font (binary/PFB)
			PC_MM		:	(ftTYPE1_MM,		'mm'),		# PC MultipleMaster font (PFB)
			PC_TYPE1_ASCII	:	(ftTYPE1ASCII,		'pfa'),		# PC Type 1 font (ASCII/PFA)
			PC_MM_ASCII		:	(ftTYPE1ASCII_MM,		'mm'),		# PC MultipleMaster font (ASCII/PFA)
			UNIX_ASCII		:	(ftTYPE1ASCII,		'pfa'),		# UNIX ASCII font (ASCII/PFA)
			OTF_TT		:	(ftTRUETYPE,			'ttf'),		# PC TrueType/TT OpenType font (TTF)
			OTF_CFF		:	(ftOPENTYPE,			'otf'),		# PS OpenType (CFF-based) font (OTF)
			MAC_TYPE1		:	(ftMACTYPE1,			'suit'),		# Mac Type 1 font (generates suitcase  and LWFN file, optionally AFM)
			MAC_TT		:	(ftMACTRUETYPE,		'ttf'),		# Mac TrueType font (generates suitcase)
			MAC_TT_DFONT	:	(ftMACTRUETYPE_DFONT,	'dfont'),	# Mac TrueType font (generates suitcase with resources in data fork) 
			}

## FL Hint stuff
# this should not be referenced outside of this module
# since we may be changing the way this works in the future.


"""

	FontLab implementation of psHints objects
	
	Most of the FL methods relating to ps hints return a list of 16 items.
	These values are for the 16 corners of a 4 axis multiple master.
	The odd thing is that even single masters get these 16 values.
	RoboFab doesn't access the MM masters, so by default, the psHints
	object only works with the first element. If you want to access the other
	values in the list, give a value between 0 and 15 for impliedMasterIndex
	when creating the object.

	From the FontLab docs:
	http://dev.fontlab.net/flpydoc/

	blue_fuzz
	blue_scale
	blue_shift

	blue_values_num(integer)             - number of defined blue values
	blue_values[integer[integer]]        - two-dimentional array of BlueValues
                                         master index is top-level index

	other_blues_num(integer)             - number of defined OtherBlues values
	other_blues[integer[integer]]        - two-dimentional array of OtherBlues
	                                       master index is top-level index

	family_blues_num(integer)            - number of FamilyBlues records
	family_blues[integer[integer]]       - two-dimentional array of FamilyBlues
	                                       master index is top-level index

	family_other_blues_num(integer)      - number of FamilyOtherBlues records
	family_other_blues[integer[integer]] - two-dimentional array of FamilyOtherBlues
	                                       master index is top-level index

	force_bold[integer]                  - list of Force Bold values, one for 
	                                       each master
	stem_snap_h_num(integer)
	stem_snap_h
	stem_snap_v_num(integer)
	stem_snap_v
 """

class PostScriptFontHintValues(BasePostScriptFontHintValues):
	"""	Wrapper for font-level PostScript hinting information for FontLab.
		Blues values, stem values. 
	"""
	def __init__(self, font=None, impliedMasterIndex=0):
		self._object = font.naked()
		self._masterIndex = impliedMasterIndex
	
	def copy(self):
		from robofab.objects.objectsRF import PostScriptFontHintValues as _PostScriptFontHintValues
		return _PostScriptFontHintValues(data=self.asDict())


class PostScriptGlyphHintValues(BasePostScriptGlyphHintValues):
	"""	Wrapper for glyph-level PostScript hinting information for FontLab.
		vStems, hStems.
	"""
	def __init__(self, glyph=None):
		self._object = glyph.naked()

	def copy(self):
		from robofab.objects.objectsRF import PostScriptGlyphHintValues as _PostScriptGlyphHintValues
		return _PostScriptGlyphHintValues(data=self.asDict())

	def _hintObjectsToList(self, item):
		data = []
		done = []
		for hint in item:
			p = (hint.position, hint.width)
			if p in done:
				continue
			data.append(p)
			done.append(p)
		data.sort()
		return data
		
	def _listToHintObjects(self, item):
		hints = []
		done = []
		for pos, width in item:
			if (pos, width) in done:
				# we don't want to set duplicates
				continue
			hints.append(Hint(pos, width))
			done.append((pos,width))
		return hints

	def _getVHints(self):
		return self._hintObjectsToList(self._object.vhints)

	def _setVHints(self, values):
		# 1 = horizontal hints and links,
		# 2 = vertical hints and links
		# 3 = all hints and links
		self._object.RemoveHints(2)
		if values is None:
			# just clearing it then
			return
		values.sort()
		for hint in self._listToHintObjects(values):
			self._object.vhints.append(hint)

	def _getHHints(self):
		return self._hintObjectsToList(self._object.hhints)

	def _setHHints(self, values):
		# 1 = horizontal hints and links,
		# 2 = vertical hints and links
		# 3 = all hints and links
		self._object.RemoveHints(1)
		if values is None:
			# just clearing it then
			return
		values.sort()
		for hint in self._listToHintObjects(values):
			self._object.hhints.append(hint)

	vHints = property(_getVHints, _setVHints, doc="postscript hints: vertical hint zones")
	hHints = property(_getHHints, _setHHints, doc="postscript hints: horizontal hint zones")



def _glyphHintsToDict(glyph):
	data = {}
	##
	## horizontal and vertical hints
	##
	# glyph.hhints and glyph.vhints returns a list of Hint objects.
	# Hint objects have position and width attributes.
	data['hHints'] = []
	for index in xrange(len(glyph.hhints)):
		hint = glyph.hhints[index]
		data['hHints'].append((hint.position, hint.width))
	if not data['hHints']:
		del data['hHints']
	data['vHints'] = []
	for index in xrange(len(glyph.vhints)):
		hint = glyph.vhints[index]
		data['vHints'].append((hint.position, hint.width))
	if not data['vHints']:
		del data['vHints']
	##
	## horizontal and vertical links
	##
	# glyph.hlinks and glyph.vlinks returns a list of Link objects.
	# Link objects have node1 and node2 attributes.
	data['hLinks'] = []
	for index in xrange(len(glyph.hlinks)):
		link = glyph.hlinks[index]
		d = {	'node1' : link.node1,
			'node2' : link.node2,
			}
		data['hLinks'].append(d)
	if not data['hLinks']:
		del data['hLinks']
	data['vLinks'] = []
	for index in xrange(len(glyph.vlinks)):
		link = glyph.vlinks[index]
		d = {	'node1' : link.node1,
			'node2' : link.node2,
			}
		data['vLinks'].append(d)
	if not data['vLinks']:
		del data['vLinks']
	##
	## replacement table
	##
	# glyph.replace_table returns a list of Replace objects.
	# Replace objects have type and index attributes.
	data['replaceTable'] = []
	for index in xrange(len(glyph.replace_table)):
		replace = glyph.replace_table[index]
		d = {	'type' : replace.type,
			'index' : replace.index,
			}
		data['replaceTable'].append(d)
	if not data['replaceTable']:
		del data['replaceTable']
	# XXX
	# need to support glyph.instructions and glyph.hdmx?
	# they are not documented very well.
	return data

def _dictHintsToGlyph(glyph, aDict):
	# clear existing hints first
	# RemoveHints requires an "integer mode" argument
	# but it is not documented. from some simple experiments
	# i deduced that
	# 1 = horizontal hints and links,
	# 2 = vertical hints and links
	# 3 = all hints and links
	glyph.RemoveHints(3)
	##
	## horizontal and vertical hints
	##
	if aDict.has_key('hHints'):
		for d in aDict['hHints']:
			glyph.hhints.append(Hint(d[0], d[1]))
	if aDict.has_key('vHints'):
		for d in aDict['vHints']:
			glyph.vhints.append(Hint(d[0], d[1]))
	##
	## horizontal and vertical links
	##
	if aDict.has_key('hLinks'):
		for d in aDict['hLinks']:
			glyph.hlinks.append(Link(d['node1'], d['node2']))
	if aDict.has_key('vLinks'):
		for d in aDict['vLinks']:
			glyph.vlinks.append(Link(d['node1'], d['node2']))
	##
	## replacement table
	##
	if aDict.has_key('replaceTable'):
		for d in aDict['replaceTable']:
			glyph.replace_table.append(Replace(d['type'], d['index']))
	
# FL Node Types
flMOVE = 17			
flLINE = 1
flCURVE = 35
flOFFCURVE = 65
flSHARP = 0
# I have no idea what the difference between
# "smooth" and "fixed" is, but booth values
# are returned by FL
flSMOOTH = 4096
flFIXED = 12288


_flToRFSegmentDict = {	flMOVE		:	MOVE,
				flLINE		:	LINE,
				flCURVE	:	CURVE,
				flOFFCURVE	:	OFFCURVE
			}

_rfToFLSegmentDict = {}
for k, v in _flToRFSegmentDict.items():
	_rfToFLSegmentDict[v] = k
		
def _flToRFSegmentType(segmentType):
	return _flToRFSegmentDict[segmentType]

def _rfToFLSegmentType(segmentType):
	return _rfToFLSegmentDict[segmentType]
		
def _scalePointFromCenter((pointX, pointY), (scaleX, scaleY), (centerX, centerY)):
	ogCenter = (centerX, centerY)
	scaledCenter = (centerX * scaleX, centerY * scaleY)
	shiftVal = (scaledCenter[0] - ogCenter[0], scaledCenter[1] - ogCenter[1])
	scaledPointX = (pointX * scaleX) - shiftVal[0]
	scaledPointY = (pointY * scaleY) - shiftVal[1]
	return (scaledPointX, scaledPointY)

# Nostalgia code:
def CurrentFont():
	"""Return a RoboFab font object for the currently selected font."""
	f = fl.font
	if f is not None:
		return RFont(fl.font)
	return None
	
def CurrentGlyph():
	"""Return a RoboFab glyph object for the currently selected glyph."""
	currentPath = fl.font.file_name
	if fl.glyph is None:
		return None
	glyphName = fl.glyph.name
	currentFont = None
	# is this font already loaded as an RFont?
	for font in AllFonts():
		# ugh this won't work because AllFonts sees non RFonts as well....
		if font.path == currentPath:
			currentFont = font
			break
	xx =  currentFont[glyphName]
	#print "objectsFL.CurrentGlyph parent for %d"% id(xx), xx.getParent()
 	return xx
	
def OpenFont(path=None, note=None):
	"""Open a font from a path."""
	if path == None:
		from robofab.interface.all.dialogs import GetFile
		path = GetFile(note)
	if path:
		if path[-4:].lower() in ['.vfb', '.VFB', '.bak', '.BAK']:
			f = Font(path)
			fl.Add(f)
			return RFont(f)
	return None
	
def NewFont(familyName=None, styleName=None):
	"""Make a new font"""
	from FL import fl, Font
	f = Font()
	fl.Add(f)
	rf = RFont(f)
	if familyName is not None:
		rf.info.familyName = familyName
	if styleName is not None:
		rf.info.styleName = styleName
	return rf

def AllFonts():
	"""Return a list of all open fonts."""
	fontCount = len(fl)
	all = []
	for index in xrange(fontCount):
		naked = fl[index]
		all.append(RFont(naked))
	return all
	
	from robofab.world import CurrentGlyph

def getGlyphFromMask(g):
	"""Get a Fab glyph object for the data in the mask layer."""
	from robofab.objects.objectsFL import RGlyph as FL_RGlyph
	from robofab.objects.objectsRF import RGlyph as RF_RGlyph
	n = g.naked()
	mask = n.mask
	fg = FL_RGlyph(mask)
	rf = RF_RGlyph()
	pen = rf.getPointPen()
	fg.drawPoints(pen)
	rf.width = g.width	# can we get to the mask glyph width without flipping the UI?
	return rf

def setMaskToGlyph(maskGlyph, targetGlyph, clear=True):
	"""Set the maskGlyph as a mask layer in targetGlyph.
	maskGlyph is a FontLab or RoboFab RGlyph, orphaned or not.
	targetGlyph is a FontLab RGLyph.
	clear is a bool. False: keep the existing mask data, True: clear the existing mask data.
	"""
	from robofab.objects.objectsFL import RGlyph as FL_RGlyph
	from FL import Glyph as FL_NakedGlyph
	flGlyph = FL_NakedGlyph()		# new, orphaned FL glyph
	wrapped = FL_RGlyph(flGlyph)	# rf wrapper for FL glyph
	if not clear:
		# copy the existing mask data first
		existingMask = getGlyphFromMask(targetGlyph)
		if existingMask is not None:
			pen = FLPointContourPen(existingMask)
			existingMask.drawPoints(pen)
	pen = FLPointContourPen(wrapped)
	maskGlyph.drawPoints(pen)		# draw the data
	targetGlyph.naked().mask = wrapped .naked()	
	targetGlyph.update()

# the lib getter and setter are shared by RFont and RGlyph	
def _get_lib(self):
	data = self._object.customdata
	if data:
		f = StringIO(data)
		try:
			pList = readPlist(f)
		except: # XXX ugh, plistlib can raise lots of things
			# Anyway, customdata does not contain valid plist data,
			# but we don't need to toss it!
			pList = {"org.robofab.fontlab.customdata": Data(data)}
	else:
		pList = {}
	# pass it along to the lib object
	l = RLib(pList)
	l.setParent(self)
	return l
		
def _set_lib(self, aDict):
	l = RLib({})
	l.setParent(self)
	l.update(aDict)


def _normalizeLineEndings(s):
	return s.replace("\r\n", "\n").replace("\r", "\n")


class RFont(BaseFont):
	"""RoboFab UFO wrapper for FL Font object"""

	_title = "FLFont"

	def __init__(self, font=None):
		BaseFont.__init__(self)
		if font is None:
			from FL import fl, Font
			# rather than raise an error we could just start a new font.
			font = Font()
			fl.Add(font)
			#raise RoboFabError, "RFont: there's nothing to wrap!?"
		self._object = font
		self._lib = {}
		self._supportHints = True
		self.psHints = PostScriptFontHintValues(self)
		self.psHints.setParent(self)

	def keys(self):
		keys = {}
		for glyph in self._object.glyphs:
			glyphName = glyph.name
			if glyphName in keys:
				n = 1
				while ("%s#%s" % (glyphName, n)) in keys:
					n += 1
				newGlyphName = "%s#%s" % (glyphName, n)
				print "RoboFab encountered a duplicate glyph name, renaming %r to %r" % (glyphName, newGlyphName)
				glyphName = newGlyphName
				glyph.name = glyphName
			keys[glyphName] = None
		return keys.keys()

	def has_key(self, glyphName):
		glyph = self._object[glyphName]
		if glyph is None:
			return False
		else:
			return True

	__contains__ = has_key

	def __setitem__(self, glyphName, glyph):
		self._object[glyphName] = glyph.naked()
		
	def __cmp__(self, other):
		if not hasattr(other, '_object'):
			return -1
		return self._compare(other)
	#	if self._object.file_name == other._object.file_name:
	#		# so, names match.
	#		# this will falsely identify two distinct "Untitled"
	#		# let's check some more
	#		return 0
	#	else:
	#		return -1
	

#	def _get_psHints(self):
#		h = PostScriptFontHintValues(self)
#		h.setParent(self)
#		return h
#
#	psHints = property(_get_psHints, doc="font level postscript hint data")

	def _get_info(self):
		return RInfo(self._object)
	
	info = property(_get_info, doc="font info object")

	def _get_features(self):
		return RFeatures(self._object)

	features = property(_get_features, doc="features object")

	def _get_kerning(self):
		kerning = {}
		f = self._object
		for g in f.glyphs:
			for p in g.kerning:
				try:
					key = (g.name, f[p.key].name)
					kerning[key] = p.value
				except AttributeError: pass #catch for TT exception
		rk = RKerning(kerning)
		rk.setParent(self)
		return rk
		
	kerning = property(_get_kerning, doc="a kerning object")
	
	def _set_groups(self, aDict):
		g = RGroups({})
		g.setParent(self)
		g.update(aDict)
	
	def _get_groups(self):
		groups = {}
		for i in self._object.classes:
			# test to make sure that the class is properly formatted
			if i.find(':') == -1:
				continue
			key = i.split(':')[0]
			value = i.split(':')[1].lstrip().split(' ')
			groups[key] = value
		rg = RGroups(groups)
		rg.setParent(self)
		return rg
		
	groups = property(_get_groups, _set_groups, doc="a group object")
	
	lib = property(_get_lib, _set_lib, doc="font lib object")
	
	#
	# attributes
	#
	
	def _get_fontIndex(self):
		# find the index of the font
		# by comparing the file_name
		# to all open fonts. if the
		# font has no file_name, meaning
		# it is a new, unsaved font,
		# return the index of the first
		# font with no file_name.
		selfFileName = self._object.file_name
		fontCount = len(fl)
		for index in xrange(fontCount):
			other = fl[index]
			if other.file_name == selfFileName:
				return index
	
	fontIndex = property(_get_fontIndex, doc="the fontindex for this font")
	
	def _get_path(self):
		return self._object.file_name

	path = property(_get_path, doc="path to the font")
	
	def _get_fileName(self):
		if self.path is None:
			return None
		return os.path.split(self.path)
	
	fileName = property(_get_fileName, doc="the font's file name")
	
	def _get_selection(self):
		# return a list of glyph names for glyphs selected in the font window
		l=[]
		for i in range(len(self._object.glyphs)):
			if fl.Selected(i) == 1:
				l.append(self._object[i].name)
		return l
		
	def _set_selection(self, list):
		fl.Unselect()
		for i in list:
			fl.Select(i)
	
	selection = property(_get_selection, _set_selection, doc="the glyph selection in the font window")
	
		
	def _makeGlyphlist(self):
		# To allow iterations through Font.glyphs. Should become really big in fonts with lotsa letters.
		gl = []
		for c in self:
			gl.append(c)
		return gl
	
	def _get_glyphs(self):
		return self._makeGlyphlist()
	
	glyphs = property(_get_glyphs, doc="A list of all glyphs in the font, to allow iterations through Font.glyphs")
			
	def update(self):
		"""Don't forget to update the font when you are done."""
		fl.UpdateFont(self.fontIndex)

	def save(self, path=None):
		"""Save the font, path is required."""
		if not path:
			if not self._object.file_name:
				raise RoboFabError, "No destination path specified."
			else:
				path = self._object.file_name
		fl.Save(self.fontIndex, path)
	
	def close(self, save=False):
		"""Close the font, saving is optional."""
		if save:
			self.save()
		else:
			self._object.modified = 0
		fl.Close(self.fontIndex)
	
	def getGlyph(self, glyphName):
		# XXX may need to become private
		flGlyph = self._object[glyphName]
		if flGlyph is not None:
			glyph = RGlyph(flGlyph)
			glyph.setParent(self)
			return glyph
		return self.newGlyph(glyphName)

	def newGlyph(self, glyphName, clear=True):
		"""Make a new glyph."""
		# the old implementation always updated the font.
		# that proved to be very slow. so, the updating is
		# now left up to the caller where it can be more
		# efficiently managed.
		g = NewGlyph(self._object, glyphName, clear, updateFont=False)
		return RGlyph(g)
	
	def insertGlyph(self, glyph, name=None):
		"""Returns a new glyph that has been inserted into the font.
		name = another glyphname if you want to insert as with that."""
		from robofab.objects.objectsRF import RFont as _RFont
		from robofab.objects.objectsRF import RGlyph as _RGlyph
		oldGlyph = glyph
		if name is None:
			name = oldGlyph.name
		# clear the destination glyph if it exists.
		if self.has_key(name):
			self[name].clear()
		# get the parent for the glyph
		otherFont = oldGlyph.getParent()
		# in some cases we will use the native
		# FL method for appending a glyph.
		useNative = True
		testingNative = True
		while testingNative:
			# but, maybe it is an orphan glyph.
			# in that case we should not use the native method.
			if otherFont is None:
				useNative = False
				testingNative = False
			# or maybe the glyph is coming from a NoneLab font
			if otherFont is not None:
				if isinstance(otherFont, _RFont):
					useNative = False
					testingNative = False
				# but, it could be a copied FL glyph
				# which is a NoneLab glyph that
				# has a FontLab font as the parent
				elif isinstance(otherFont, RFont):
					useNative = False
					testingNative = False
			# or, maybe the glyph is being replaced, in which
			# case the native method should not be used
			# since FL will destroy any references to the glyph
			if self.has_key(name):
				useNative = False
				testingNative = False
			# if the glyph contains components the native
			# method should not be used since FL does
			# not reference glyphs in components by
			# name, but by index (!!!).
			if len(oldGlyph.components) != 0:
				useNative = False
				testingNative = False
			testingNative = False
		# finally, insert the glyph.
		if useNative:
			font = self.naked()
			otherFont = oldGlyph.getParent().naked()
			self.naked().glyphs.append(otherFont[name])
			newGlyph = self.getGlyph(name)
		else:	
			newGlyph = self.newGlyph(name)
			newGlyph.appendGlyph(oldGlyph)
			for attr in GLYPH_COPY_ATTRS:
				if attr == "name":
					value = name
				else:
					value = getattr(oldGlyph, attr)
				setattr(newGlyph, attr, value)
		if self._supportHints:
			# now we need to transfer the hints from
			# the old glyph to the new glyph. we'll do this
			# via the dict to hint functions.
			hintDict = {}
			# if the glyph is a NoneLab glyph, then we need
			# to extract the ps hints from the lib
			if isinstance(oldGlyph, _RGlyph):
				hintDict = oldGlyph.lib.get(postScriptHintDataLibKey, {})
			# otherwise we need to extract the hint dict from the glyph
			else:
				hintDict = _glyphHintsToDict(oldGlyph.naked())
			# now apply the hint data
			if hintDict:
				_dictHintsToGlyph(newGlyph.naked(), hintDict)
			# delete any remaining hint data from the glyph lib
			if newGlyph.lib.has_key(postScriptHintDataLibKey):
				del newGlyph.lib[postScriptHintDataLibKey]
		return newGlyph
	
	def removeGlyph(self, glyphName):
		"""remove a glyph from the font"""
		index = self._object.FindGlyph(glyphName)
		if index != -1:
			del self._object.glyphs[index]

	#
	# opentype
	#

	def getOTClasses(self):
		"""Return all OpenType classes as a dict. Relies on properly formatted classes."""
		classes = {}
		c = self._object.ot_classes
		if c is None:
			return classes
		c = c.replace('\r', '').replace('\n', '').split(';')
		for i in c:
			if i.find('=') != -1:
				value = []
				i = i.replace(' = ', '=')
				name = i.split('=')[0]
				v = i.split('=')[1].replace('[', '').replace(']', '').split(' ')
				#catch double spaces?
				for j in v:
					if len(j) > 0:
						value.append(j)
				classes[name] = value
		return classes
		
	def setOTClasses(self, dict):
		"""Set all OpenType classes."""
		l = []
		for i in dict.keys():
			l.append(''.join([i, ' = [', ' '.join(dict[i]), '];']))
		self._object.ot_classes = '\n'.join(l)
		
	def getOTClass(self, name):
		"""Get a specific OpenType class."""
		classes = self.getOTClasses()
		return classes[name]
	
	def setOTClass(self, name, list):
		"""Set a specific OpenType class."""
		classes = self.getOTClasses()
		classes[name] = list
		self.setOTClasses(classes)
	
	def getOTFeatures(self):
		"""Return all OpenType features as a dict keyed by name.
		The value is a string of the text of the feature."""
		features = {}
		for i in self._object.features:
			v = []
			for j in i.value.replace('\r', '\n').split('\n'):
				if j.find(i.tag) == -1:
					v.append(j)
			features[i.tag] = '\n'.join(v)
		return features
	
	def setOTFeatures(self, dict):
		"""Set all OpenType features in the font."""
		features= {}
		for i in dict.keys():
			f = []
			f.append('feature %s {'%i)
			f.append(dict[i])
			f.append('} %s;'%i)
			features[i] = '\n'.join(f)
		self._object.features.clean()
		for i in features.keys():
			self._object.features.append(Feature(i, features[i]))
			
	def getOTFeature(self, name):
		"""return a specific OpenType feature."""
		features = self.getOTFeatures()
		return features[name]
	
	def setOTFeature(self, name, text):
		"""Set a specific OpenType feature."""
		features = self.getOTFeatures()
		features[name] = text
		self.setOTFeatures(features)
		
	#
	# guides
	#
	
	def getVGuides(self):
		"""Return a list of wrapped vertical guides in this RFont"""
		vguides=[]
		for i in range(len(self._object.vguides)):
			g = RGuide(self._object.vguides[i], i)
			g.setParent(self)
			vguides.append(g)
		return vguides
	
	def getHGuides(self):
		"""Return a list of wrapped horizontal guides in this RFont"""
		hguides=[]
		for i in range(len(self._object.hguides)):
			g = RGuide(self._object.hguides[i], i)
			g.setParent(self)
			hguides.append(g)
		return hguides
		
	def appendHGuide(self, position, angle=0):
		"""Append a horizontal guide"""
		position = int(round(position))
		angle = int(round(angle))
		g=Guide(position, angle)
		self._object.hguides.append(g)
		
	def appendVGuide(self, position, angle=0):
		"""Append a horizontal guide"""
		position = int(round(position))
		angle = int(round(angle))
		g=Guide(position, angle)
		self._object.vguides.append(g)
		
	def removeHGuide(self, guide):
		"""Remove a horizontal guide."""
		pos = (guide.position, guide.angle)
		for g in self.getHGuides():
			if  (g.position, g.angle) == pos:
				del self._object.hguides[g.index]
				break
				
	def removeVGuide(self, guide):
		"""Remove a vertical guide."""
		pos = (guide.position, guide.angle)
		for g in self.getVGuides():
			if  (g.position, g.angle) == pos:
				del self._object.vguides[g.index]
				break

	def clearHGuides(self):
		"""Clear all horizontal guides."""
		self._object.hguides.clean()
	
	def clearVGuides(self):
		"""Clear all vertical guides."""
		self._object.vguides.clean()


	#
	# generators
	#
	
	def generate(self, outputType, path=None):
		"""
		generate the font. outputType is the type of font to ouput.
		--Ouput Types:
		'pctype1'	:	PC Type 1 font (binary/PFB)
		'pcmm'		:	PC MultipleMaster font (PFB)
		'pctype1ascii'	:	PC Type 1 font (ASCII/PFA)
		'pcmmascii'	:	PC MultipleMaster font (ASCII/PFA)
		'unixascii'	:	UNIX ASCII font (ASCII/PFA)
		'mactype1'	:	Mac Type 1 font (generates suitcase  and LWFN file)
		'otfcff'		:	PS OpenType (CFF-based) font (OTF)
		'otfttf'		:	PC TrueType/TT OpenType font (TTF)
		'macttf'	:	Mac TrueType font (generates suitcase)
		'macttdfont'	:	Mac TrueType font (generates suitcase with resources in data fork)
					(doc adapted from http://dev.fontlab.net/flpydoc/)
		
		path can be a directory or a directory file name combo:
		path="DirectoryA/DirectoryB"
		path="DirectoryA/DirectoryB/MyFontName"
		if no path is given, the file will be output in the same directory
		as the vfb file. if no file name is given, the filename will be the
		vfb file name with the appropriate suffix.
		"""
		outputType = outputType.lower()
		if not _flGenerateTypes.has_key(outputType):
			raise RoboFabError, "%s output type is not supported"%outputType
		flOutputType, suffix = _flGenerateTypes[outputType]
		if path is None:
			filePath, fileName = os.path.split(self.path)
			fileName = fileName.replace('.vfb', '')
		else:
			if os.path.isdir(path):
				filePath = path
				fileName = os.path.split(self.path)[1].replace('.vfb', '')
			else:
				filePath, fileName = os.path.split(path)
		if '.' in fileName:
			raise RoboFabError, "filename cannot contain periods.", fileName
		fileName = '.'.join([fileName, suffix])
		finalPath = os.path.join(filePath, fileName)
		if isinstance(finalPath, unicode):
			finalPath = finalPath.encode("utf-8")
		# generate is (oddly) an application level method
		# rather than a font level method. because of this,
		# the font must be the current font. so, make it so.
		fl.ifont = self.fontIndex
		fl.GenerateFont(flOutputType, finalPath)

	def writeUFO(self, path=None, doProgress=False, glyphNameToFileNameFunc=None,
		doHints=False, doInfo=True, doKerning=True, doGroups=True, doLib=True, doFeatures=True, glyphs=None, formatVersion=2):
		from robofab.interface.all.dialogs import ProgressBar, Message
		# special glyph name to file name conversion
		if glyphNameToFileNameFunc is None:
			glyphNameToFileNameFunc = self.getGlyphNameToFileNameFunc()
			if glyphNameToFileNameFunc is None:
				from robofab.tools.glyphNameSchemes import glyphNameToShortFileName
				glyphNameToFileNameFunc = glyphNameToShortFileName
		# get a valid path
		if not path:
			if self.path is None:
				Message("Please save this font first before exporting to UFO...")
				return
			else:
				path = ufoLib.makeUFOPath(self.path)
		# get the glyphs to export
		if glyphs is None:
			glyphs = self.keys()
		# if the file exists, check the format version.
		# if the format version being written is different
		# from the format version of the existing UFO
		# and only some files are set to be written
		# raise an error.
		if os.path.exists(path):
			if os.path.exists(os.path.join(path, "metainfo.plist")):
				reader = ufoLib.UFOReader(path)
				existingFormatVersion = reader.formatVersion
				if formatVersion != existingFormatVersion:
					if False in [doInfo, doKerning, doGroups, doLib, doFeatures, set(glyphs) == set(self.keys())]:
						Message("When overwriting an existing UFO with a different format version all files must be written.")
						return
		# the lib must be written if format version is 1
		if not doLib and formatVersion == 1:
			Message("The lib must be written when exporting format version 1.")
			return
		# set up the progress bar
		nonGlyphCount = [doInfo, doKerning, doGroups, doLib, doFeatures].count(True)
		bar = None
		if doProgress:
			bar = ProgressBar("Exporting UFO", nonGlyphCount + len(glyphs))
		# try writing
		try:
			writer = ufoLib.UFOWriter(path, formatVersion=formatVersion)
			## We make a shallow copy if lib, since we add some stuff for export
			## that doesn't need to be retained in memory.
			fontLib = dict(self.lib)
			# write the font info
			if doInfo:
				global _IN_UFO_EXPORT
				_IN_UFO_EXPORT = True
				writer.writeInfo(self.info)
				_IN_UFO_EXPORT = False
				if bar:
					bar.tick()
			# write the kerning
			if doKerning:
				writer.writeKerning(self.kerning.asDict())
				if bar:
					bar.tick()
			# write the groups
			if doGroups:
				writer.writeGroups(self.groups)
				if bar:
					bar.tick()
			# write the features
			if doFeatures:
				if formatVersion == 2:
					writer.writeFeatures(self.features.text)
				else:
					self._writeOpenTypeFeaturesToLib(fontLib)
				if bar:
					bar.tick()
			# write the lib
			if doLib:
				## Always export the postscript font hint values to the lib in format version 1
				if formatVersion == 1:
					d = self.psHints.asDict()
					fontLib[postScriptHintDataLibKey] = d
				## Export the glyph order to the lib
				glyphOrder = [nakedGlyph.name for nakedGlyph in self.naked().glyphs]
				fontLib["public.glyphOrder"] = glyphOrder
				## export the features
				if doFeatures and formatVersion == 1:
					self._writeOpenTypeFeaturesToLib(fontLib)
					if bar:
						bar.tick()
				writer.writeLib(fontLib)
				if bar:
					bar.tick()
			# write the glyphs
			if glyphs:
				glyphSet = writer.getGlyphSet(glyphNameToFileNameFunc)
				count = nonGlyphCount
				for nakedGlyph in self.naked().glyphs:
					if nakedGlyph.name not in glyphs:
						continue
					glyph = RGlyph(nakedGlyph)
					if doHints:
						hintStuff = _glyphHintsToDict(glyph.naked())
						if hintStuff:
							glyph.lib[postScriptHintDataLibKey] = hintStuff
					glyphSet.writeGlyph(glyph.name, glyph, glyph.drawPoints)
					# remove the hint dict from the lib
					if doHints and glyph.lib.has_key(postScriptHintDataLibKey):
						del glyph.lib[postScriptHintDataLibKey]
					if bar and not count % 10:
						bar.tick(count)
					count = count + 1
				glyphSet.writeContents()
		# only blindly stop if the user says to
		except KeyboardInterrupt:
			if bar:
				bar.close()
			bar = None
		# kill the bar
		if bar:
			bar.close()

	def _writeOpenTypeFeaturesToLib(self, fontLib):
		# this should only be used for UFO format version 1
		flFont = self.naked()
		cls = flFont.ot_classes
		if cls is not None:
			fontLib["org.robofab.opentype.classes"] = _normalizeLineEndings(cls).rstrip() + "\n"
		if flFont.features:
			features = {}
			order = []
			for feature in flFont.features:
				order.append(feature.tag)
				features[feature.tag] = _normalizeLineEndings(feature.value).rstrip() + "\n"
			fontLib["org.robofab.opentype.features"] = features
			fontLib["org.robofab.opentype.featureorder"] = order

	def readUFO(self, path, doProgress=False,
		doHints=False, doInfo=True, doKerning=True, doGroups=True, doLib=True, doFeatures=True, glyphs=None):
		"""read a .ufo into the font"""
		from robofab.pens.flPen import FLPointPen
		from robofab.interface.all.dialogs import ProgressBar
		# start up the reader
		reader = ufoLib.UFOReader(path)
		glyphSet = reader.getGlyphSet()
		# get a list of glyphs that should be imported
		if glyphs is None:
			glyphs = glyphSet.keys()
		# set up the progress bar
		nonGlyphCount = [doInfo, doKerning, doGroups, doLib, doFeatures].count(True)
		bar = None
		if doProgress:
			bar = ProgressBar("Importing UFO", nonGlyphCount + len(glyphs))
		# start reading
		try:
			fontLib = reader.readLib()
			# info
			if doInfo:
				reader.readInfo(self.info)
				if bar:
					bar.tick()
			# glyphs
			count = 1
			glyphOrder = self._getGlyphOrderFromLib(fontLib, glyphSet)
			for glyphName in glyphOrder:
				if glyphName not in glyphs:
					continue
				glyph = self.newGlyph(glyphName, clear=True)
				pen = FLPointPen(glyph.naked())
				glyphSet.readGlyph(glyphName=glyphName, glyphObject=glyph, pointPen=pen)
				if doHints:
					hintData = glyph.lib.get(postScriptHintDataLibKey)
					if hintData:
						_dictHintsToGlyph(glyph.naked(), hintData)
					# now that the hints have been extracted from the glyph
					# there is no reason to keep the location in the lib.
					if glyph.lib.has_key(postScriptHintDataLibKey):
						del glyph.lib[postScriptHintDataLibKey]
				if bar and not count % 10:
					bar.tick(count)
				count = count + 1
			# features
			if doFeatures:
				if reader.formatVersion == 1:
					self._readOpenTypeFeaturesFromLib(fontLib)
				else:
					featureText = reader.readFeatures()
					self.features.text = featureText
				if bar:
					bar.tick()
			else:
				# remove features stored in the lib
				self._readOpenTypeFeaturesFromLib(fontLib, setFeatures=False)
			# kerning
			if doKerning:
				self.kerning.clear()
				self.kerning.update(reader.readKerning())
				if bar:
					bar.tick()
			# groups
			if doGroups:
				self.groups.clear()
				self.groups.update(reader.readGroups())
				if bar:
					bar.tick()
			# hints in format version 1
			if doHints and reader.formatVersion == 1:
				self.psHints._loadFromLib(fontLib)
			else:
				# remove hint data stored in the lib
				if fontLib.has_key(postScriptHintDataLibKey):
					del fontLib[postScriptHintDataLibKey]
			# lib
			if doLib:
				self.lib.clear()
				self.lib.update(fontLib)
				if bar:
					bar.tick()
			# update the font
			self.update()
		# only blindly stop if the user says to
		except KeyboardInterrupt:
			bar.close()
			bar = None
		# kill the bar
		if bar:
			bar.close()

	def _getGlyphOrderFromLib(self, fontLib, glyphSet):
		key = "public.glyphOrder"  
		glyphOrder = fontLib.get(key)
		if glyphOrder is None:
			key = "org.robofab.glyphOrder"
		glyphOrder = fontLib.get(key)
		if glyphOrder is not None:
			# no need to keep track if the glyph order in lib once the font is loaded.
			del fontLib[key]
			glyphNames = []
			done = {}
			for glyphName in glyphOrder:
				if glyphName in glyphSet:
					glyphNames.append(glyphName)
					done[glyphName] = 1
			allGlyphNames = glyphSet.keys()
			allGlyphNames.sort()
			for glyphName in allGlyphNames:
				if glyphName not in done:
					glyphNames.append(glyphName)
		else:
			glyphNames = glyphSet.keys()
			glyphNames.sort()
		return glyphNames
	
	def _readOpenTypeFeaturesFromLib(self, fontLib, setFeatures=True):
		# setFeatures may be False. in this case, this method
		# should only clear the data from the lib.
		classes = fontLib.get("org.robofab.opentype.classes")
		if classes is not None:
			del fontLib["org.robofab.opentype.classes"]
			if setFeatures:
				self.naked().ot_classes = classes
		features = fontLib.get("org.robofab.opentype.features")
		if features is not None:
			order = fontLib.get("org.robofab.opentype.featureorder")
			if order is None:
				# for UFOs saved without the feature order, do the same as before.
				order = features.keys()
				order.sort()
			else:
				del fontLib["org.robofab.opentype.featureorder"]
			del fontLib["org.robofab.opentype.features"]
			#features = features.items()
			orderedFeatures = []
			for tag in order:
				oneFeature = features.get(tag)
				if oneFeature is not None:
					orderedFeatures.append((tag, oneFeature))
			if setFeatures:
				self.naked().features.clean()
				for tag, src in orderedFeatures:
					self.naked().features.append(Feature(tag, src))



class RGlyph(BaseGlyph):
	"""RoboFab wrapper for FL Glyph object"""

	_title = "FLGlyph"

	def __init__(self, flGlyph):
		#BaseGlyph.__init__(self)
		if flGlyph is None:
			raise RoboFabError, "RGlyph: there's nothing to wrap!?"
		self._object = flGlyph
		self._lib = {}
		self._contours = None
		
	def __getitem__(self, index):
		return self.contours[index]
			
	def __delitem__(self, index):
		self._object.DeleteContour(index)
		self._invalidateContours()
	
	def __len__(self):
		return len(self.contours)
		
	lib = property(_get_lib, _set_lib, doc="glyph lib object")
	
	def _invalidateContours(self):
		self._contours = None
	
	def _buildContours(self):
		self._contours = []
		for contourIndex in range(self._object.GetContoursNumber()):
			c = RContour(contourIndex)
			c.setParent(self)
			c._buildSegments()
			self._contours.append(c)
		
	#
	# attribute handlers
	#
	
	def _get_index(self):
		return self._object.parent.FindGlyph(self.name)
	
	index = property(_get_index, doc="return the index of the glyph in the font")
	
	def _get_name(self):
		return self._object.name

	def _set_name(self, value):
		self._object.name = value

	name = property(_get_name, _set_name, doc="name")
	
	def _get_psName(self):
		return self._object.name

	def _set_psName(self, value):
		self._object.name = value

	psName = property(_get_psName, _set_psName, doc="name")
	
	def _get_baseName(self):
		return self._object.name.split('.')[0]
	
	baseName = property(_get_baseName, doc="")
	
	def _get_unicode(self):
		return self._object.unicode

	def _set_unicode(self, value):
		self._object.unicode = value

	unicode = property(_get_unicode, _set_unicode, doc="unicode")
	
	def _get_unicodes(self):
		return self._object.unicodes

	def _set_unicodes(self, value):
		self._object.unicodes = value

	unicodes = property(_get_unicodes, _set_unicodes, doc="unicodes")

	def _get_width(self):
		return self._object.width
	
	def _set_width(self, value):
		value = int(round(value))
		self._object.width = value
		
	width = property(_get_width, _set_width, doc="the width")
	
	def _get_box(self):
		if not len(self.contours) and not len(self.components):
			return (0, 0, 0, 0)
		r = self._object.GetBoundingRect()
		return (int(round(r.ll.x)), int(round(r.ll.y)), int(round(r.ur.x)), int(round(r.ur.y)))
			
	box = property(_get_box, doc="box of glyph as a tuple (xMin, yMin, xMax, yMax)")
	
	def _get_selected(self):
		if fl.Selected(self._object.parent.FindGlyph(self._object.name)):
			return 1
		else:
			return 0
			
	def _set_selected(self, value):
		fl.Select(self._object.name, value)
	
	selected = property(_get_selected, _set_selected, doc="Select or deselect the glyph in the font window")
	
	def _get_mark(self):
		return self._object.mark

	def _set_mark(self, value):
		self._object.mark = value

	mark = property(_get_mark, _set_mark, doc="mark")
	
	def _get_note(self):
		s = self._object.note
		if s is None:
			return s
		return unicode(s, LOCAL_ENCODING)

	def _set_note(self, value):
		if value is None:
			value = ''
		if type(value) == type(u""):
			value = value.encode(LOCAL_ENCODING)
		self._object.note = value

	note = property(_get_note, _set_note, doc="note")
	
	def _get_psHints(self):
		# get an object representing the postscript zone information
		return PostScriptGlyphHintValues(self)
		
	psHints = property(_get_psHints, doc="postscript hint data")
	
	#
	#	necessary evil
	#
			
	def update(self):
		"""Don't forget to update the glyph when you are done."""
		fl.UpdateGlyph(self._object.parent.FindGlyph(self._object.name))
	
	#
	#	methods to make RGlyph compatible with FL.Glyph
	#	##are these still needed?
	#
	
	def GetBoundingRect(self, masterIndex):
		"""FL compatibility"""
		return self._object.GetBoundingRect(masterIndex)
		
	def GetMetrics(self, masterIndex):
		"""FL compatibility"""
		return self._object.GetMetrics(masterIndex)
		
	def SetMetrics(self, value, masterIndex):
		"""FL compatibility"""
		return self._object.SetMetrics(value, masterIndex)
	
	#
	# object builders
	#
	
	def _get_anchors(self):
		return self.getAnchors()
	
	anchors = property(_get_anchors, doc="allow for iteration through glyph.anchors")
		
	def _get_components(self):
		return self.getComponents()
		
	components = property(_get_components, doc="allow for iteration through glyph.components")

	def _get_contours(self):
		if self._contours is None:
			self._buildContours()
		return self._contours
	
	contours = property(_get_contours, doc="allow for iteration through glyph.contours")

	def getAnchors(self):
		"""Return a list of wrapped anchors in this RGlyph."""
		anchors=[]
		for i in range(len(self._object.anchors)):
			a = RAnchor(self._object.anchors[i], i)
			a.setParent(self)
			anchors.append(a)
		return anchors
	
	def getComponents(self):
		"""Return a list of wrapped components in this RGlyph."""
		components=[]
		for i in range(len(self._object.components)):
			c = RComponent(self._object.components[i], i)
			c.setParent(self)
			components.append(c)
		return components
	
	def getVGuides(self):
		"""Return a list of wrapped vertical guides in this RGlyph"""
		vguides=[]
		for i in range(len(self._object.vguides)):
			g = RGuide(self._object.vguides[i], i)
			g.setParent(self)
			vguides.append(g)
		return vguides
	
	def getHGuides(self):
		"""Return a list of wrapped horizontal guides in this RGlyph"""
		hguides=[]
		for i in range(len(self._object.hguides)):
			g = RGuide(self._object.hguides[i], i)
			g.setParent(self)
			hguides.append(g)
		return hguides	
	
	#
	# tools
	#

	def getPointPen(self):
		self._invalidateContours()
		# Now just don't muck with glyph.contours before you're done drawing...
		return FLPointPen(self)

	def appendComponent(self, baseGlyph, offset=(0, 0), scale=(1, 1)):
		"""Append a component to the glyph. x and y are optional offset values"""
		offset = roundPt((offset[0], offset[1]))
		p = FLPointPen(self.naked())
		xx, yy = scale
		dx, dy = offset
		p.addComponent(baseGlyph, (xx, 0, 0, yy, dx, dy))
		
	def appendAnchor(self, name, position):
		"""Append an anchor to the glyph"""
		value = roundPt((position[0], position[1]))
		anchor = Anchor(name, value[0], value[1])
		self._object.anchors.append(anchor)
	
	def appendHGuide(self, position, angle=0):
		"""Append a horizontal guide"""
		position = int(round(position))
		g = Guide(position, angle)
		self._object.hguides.append(g)
		
	def appendVGuide(self, position, angle=0):
		"""Append a horizontal guide"""
		position = int(round(position))
		g = Guide(position, angle)
		self._object.vguides.append(g)

	def clearContours(self):
		self._object.Clear()
		self._invalidateContours()

	def clearComponents(self):
		"""Clear all components."""
		self._object.components.clean()
	
	def clearAnchors(self):
		"""Clear all anchors."""
		self._object.anchors.clean()
	
	def clearHGuides(self):
		"""Clear all horizontal guides."""
		self._object.hguides.clean()
	
	def clearVGuides(self):
		"""Clear all vertical guides."""
		self._object.vguides.clean()
		
	def removeComponent(self, component):
		"""Remove a specific component from the glyph. This only works
		if the glyph does not have duplicate components in the same location."""
		pos = (component.baseGlyph, component.offset, component.scale)
		a = self.getComponents()
		found = []
		for i in a:
			if (i.baseGlyph, i.offset, i.scale) == pos:
				found.append(i)
		if len(found) > 1:
			raise RoboFabError, 'Found more than one possible component to remove'
		elif len(found) == 1:
			del self._object.components[found[0].index]
		else:
			raise RoboFabError, 'Component does not exist'
	
	def removeContour(self, index):
		"""remove a specific contour  from the glyph"""
		self._object.DeleteContour(index)
		self._invalidateContours()
		
	def removeAnchor(self, anchor):
		"""Remove a specific anchor from the glyph. This only works
		if the glyph does not have anchors with duplicate names
		in exactly the same location with the same mark."""
		pos = (anchor.name, anchor.position, anchor.mark)
		a = self.getAnchors()
		found = []
		for i in a:
			if (i.name, i.position, i.mark) == pos:
				found.append(i)
		if len(found) > 1:
			raise RoboFabError, 'Found more than one possible anchor to remove'
		elif len(found) == 1:
			del self._object.anchors[found[0].index]
		else:
			raise RoboFabError, 'Anchor does not exist'
		
	def removeHGuide(self, guide):
		"""Remove a horizontal guide."""
		pos = (guide.position, guide.angle)
		for g in self.getHGuides():
			if  (g.position, g.angle) == pos:
				del self._object.hguides[g.index]
				break
				
	def removeVGuide(self, guide):
		"""Remove a vertical guide."""
		pos = (guide.position, guide.angle)
		for g in self.getVGuides():
			if  (g.position, g.angle) == pos:
				del self._object.vguides[g.index]
				break

	def center(self, padding=None):
		"""Equalise sidebearings, set to padding if wanted."""
		left = self.leftMargin
		right = self.rightMargin
		if padding:
			e_left = e_right = padding
		else:
			e_left = (left + right)/2
			e_right = (left + right) - e_left
		self.leftMargin= e_left
		self.rightMargin= e_right
		
	def removeOverlap(self):
		"""Remove overlap"""
		self._object.RemoveOverlap()
		self._invalidateContours()
	
	def decompose(self):
		"""Decompose all components"""
		self._object.Decompose()
		self._invalidateContours()
	
	##broken!
	#def removeHints(self):
	#	"""Remove the hints."""
	#	self._object.RemoveHints()
		
	def autoHint(self):
		"""Automatically generate type 1 hints."""
		self._object.Autohint()
		
	def move(self, (x, y), contours=True, components=True, anchors=True):
		"""Move a glyph's items that are flagged as True"""
		x, y = roundPt((x, y))
		self._object.Shift(Point(x, y))
		for c in self.getComponents():
			c.move((x, y))
		for a in self.getAnchors():
			a.move((x, y))
	
	def clear(self, contours=True, components=True, anchors=True, guides=True, hints=True):
		"""Clear all items marked as true from the glyph"""
		if contours:
			self._object.Clear()
			self._invalidateContours()
		if components:
			self._object.components.clean()
		if anchors:
			self._object.anchors.clean()
		if guides:
			self._object.hguides.clean()
			self._object.vguides.clean()
		if hints:
			# RemoveHints requires an "integer mode" argument
			# but it is not documented. from some simple experiments
			# i deduced that
			# 1 = horizontal hints and links,
			# 2 = vertical hints and links
			# 3 = all hints and links
			self._object.RemoveHints(3)
	
	#
	#	special treatment for GlyphMath support in FontLab
	#
	
	def _getMathDestination(self):
		from robofab.objects.objectsRF import RGlyph as _RGlyph
		return _RGlyph()
	
	def copy(self, aParent=None):
		"""Make a copy of this glyph.
		Note: the copy is not a duplicate fontlab glyph, but
		a RF RGlyph with the same outlines. The new glyph is
		not part of the fontlab font in any way. Use font.appendGlyph(glyph)
		to get it in a FontLab glyph again."""
		from robofab.objects.objectsRF import RGlyph as _RGlyph
		newGlyph = _RGlyph()
		newGlyph.appendGlyph(self)
		for attr in GLYPH_COPY_ATTRS:
			value = getattr(self, attr)
			setattr(newGlyph, attr, value)
		# hints
		doHints = False
		parent = self.getParent()
		if parent is not None and parent._supportHints:
			hintStuff = _glyphHintsToDict(self.naked())
			if hintStuff:
				newGlyph.lib[postScriptHintDataLibKey] = hintStuff
		if aParent is not None:
			newGlyph.setParent(aParent)
		elif self.getParent() is not None:
			newGlyph.setParent(self.getParent())
		return newGlyph
	
	def __mul__(self, factor):
		return self.copy() *factor
	
	__rmul__ = __mul__

	def __sub__(self, other):
		return self.copy() - other.copy()
	
	def __add__(self, other):
		return self.copy() + other.copy()
	


class RContour(BaseContour):
	
	"""RoboFab wrapper for non FL contour object"""
		
	_title = "FLContour"
	
	def __init__(self, index):
		self._index = index
		self._parentGlyph = None
		self.segments = []
	
	def __len__(self):
		return len(self.points)
		
	def _buildSegments(self):		
		#######################
		# Notes about FL node contour structure
		#######################
		# for TT curves, FL lists them as seperate nodes:
		#	[move, off, off, off, line, off, off]
		# and, this list is sequential. after the last on curve,
		# it is possible (and likely) that there will be more offCurves
		# in our segment object, these should be associated with the
		# first segment in the contour.
		#
		# for PS curves, it is a very different scenerio.
		# curve nodes contain points:
		#	[on, off, off]
		# and the list is not in sequential order. the first point in
		# the list is the on curve and the subsequent points are the off
		# curve points leading up to that on curve.
		#
		# it is very important to remember these structures when trying
		# to understand the code below
		
		self.segments = []
		offList = []
		nodes = self._nakedParent.nodes
		for index in range(self._nodeLength):
			x = index + self._startNodeIndex
			node = nodes[x]
			# we do have a loose off curve. deal with it.
			if node.type == flOFFCURVE:
				offList.append(x)
			# we are not dealing with a loose off curve
			else:
				s = RSegment(x)
				s.setParent(self)
				# but do we have a collection of loose off curves above?
				# if so, apply them to the segment, and clear the list
				if len(offList) != 0:
					s._looseOffCurve = offList
				offList = []
				self.segments.append(s)
		# do we have some off curves now that the contour is complete?
		if len(offList) != 0:
			# ugh. apply them to the first segment
			self.segments[0]._looseOffCurve = offList
	
	def setParent(self, parentGlyph):
		self._parentGlyph = parentGlyph
		
	def getParent(self):
		return self._parentGlyph
		
	def _get__nakedParent(self):
		return self._parentGlyph.naked()
	
	_nakedParent = property(_get__nakedParent, doc="")
	
	def _get__startNodeIndex(self):
		return self._nakedParent.GetContourBegin(self._index)
	
	_startNodeIndex = property(_get__startNodeIndex, doc="")
	
	def _get__nodeLength(self):
		return self._nakedParent.GetContourLength(self._index)
		
	_nodeLength = property(_get__nodeLength, doc="")

	def _get__lastNodeIndex(self):
		return self._startNodeIndex + self._nodeLength - 1
		
	_lastNodeIndex = property(_get__lastNodeIndex, doc="")

	def _previousNodeIndex(self, index):
		return (index - 1) % self._nodeLength

	def _nextNodeIndex(self, index):
		return (index + 1) % self._nodeLength
	
	def _getNode(self, index):
		return self._nodes[index]
	
	def _get__nodes(self):
		nodes = []
		for node in self._nakedParent.nodes[self._startNodeIndex:self._startNodeIndex+self._nodeLength-1]:
			nodes.append(node)
		return nodes
	
	_nodes = property(_get__nodes, doc="")

	def _get_points(self):
		points = []
		for segment in self.segments:
			for point in segment.points:
				points.append(point)
		return points
		
	points = property(_get_points, doc="")

	def _get_bPoints(self):
		bPoints = []
		for segment in self.segments:
			bp = RBPoint(segment.index)
			bp.setParent(self)
			bPoints.append(bp)
		return bPoints
		
	bPoints = property(_get_bPoints, doc="")
	
	def _get_index(self):
		return self._index

	def _set_index(self, index):
		if index != self._index:
			self._nakedParent.ReorderContour(self._index, index)
			# reorder and set the _index of the existing RContour objects
			# this will be a better solution than reconstructing all the objects
			# segment objects will still, sadly, have to be reconstructed
			contourList = self.getParent().contours
			contourList.insert(index, contourList.pop(self._index))
			for i in range(len(contourList)):
				contourList[i]._index = i
				contourList[i]._buildSegments()
		
	
	index = property(_get_index, _set_index, doc="the index of the contour")

	def _get_selected(self):
		selected = 0
		nodes = self._nodes
		for node in nodes:
			if node.selected == 1:
				selected = 1
				break
		return selected
		
	def _set_selected(self, value):
		if value == 1:
			self._nakedParent.SelectContour(self._index)
		else:
			for node in self._nodes:
				node.selected = value

	selected = property(_get_selected, _set_selected, doc="selection of the contour: 1-selected or 0-unselected")

	def appendSegment(self, segmentType, points, smooth=False):
		segment = self.insertSegment(index=self._nodeLength, segmentType=segmentType, points=points, smooth=smooth)
		return segment
		
	def insertSegment(self, index, segmentType, points, smooth=False):
		"""insert a seggment into the contour"""
		# do a  qcurve insertion
		if segmentType == QCURVE:
			count = 0
			for point in points[:-1]:
				newNode = Node(flOFFCURVE, Point(point[0], point[1]))
				self._nakedParent.Insert(newNode, self._startNodeIndex + index + count)
				count = count + 1
			newNode = Node(flLINE, Point(points[-1][0], points[-1][1]))
			self._nakedParent.Insert(newNode, self._startNodeIndex + index +len(points) - 1)
		# do a regular insertion
		else:	
			onX, onY = points[-1]
			newNode = Node(_rfToFLSegmentType(segmentType), Point(onX, onY))
			# fix the off curves in case the user is inserting a curve
			# but is not specifying off curve points
			if segmentType == CURVE and len(points) == 1:
				pSeg = self._prevSegment(index)
				pOn = pSeg.onCurve
				newNode.points[1].Assign(Point(pOn.x, pOn.y))
				newNode.points[2].Assign(Point(onX, onY))
			for pointIndex in range(len(points[:-1])):
				x, y = points[pointIndex]
				newNode.points[1 + pointIndex].Assign(Point(x, y))
			if smooth:
				newNode.alignment = flSMOOTH
			self._nakedParent.Insert(newNode, self._startNodeIndex + index)
		self._buildSegments()
		return self.segments[index]
		
	def removeSegment(self, index):
		"""remove a segment from the contour"""
		segment = self.segments[index]
		# we have a qcurve. umph.
		if segment.type == QCURVE:
			indexList = [segment._nodeIndex] + segment._looseOffCurve
			indexList.sort()
			indexList.reverse()
			parent = self._nakedParent
			for nodeIndex in indexList:
				parent.DeleteNode(nodeIndex)
		# we have a more sane structure to follow
		else:
			# store some info for later
			next = self._nextSegment(index)
			nextOffA = None
			nextOffB = None
			nextType = next.type
			if nextType != LINE and nextType != MOVE:
				pA = next.offCurve[0]
				nextOffA = (pA.x, pA.y)
				pB = next.offCurve[-1]
				nextOffB = (pB.x, pB.y)
			nodeIndex = segment._nodeIndex
			self._nakedParent.DeleteNode(nodeIndex)
			self._buildSegments()
			# now we must override FL guessing about offCurves
			next = self._nextSegment(index - 1)
			nextType = next.type
			if nextType != LINE and nextType != MOVE:
				pA = next.offCurve[0]
				pB = next.offCurve[-1]
				pA.x, pA.y = nextOffA
				pB.x, pB.y = nextOffB
		
	def reverseContour(self):
		"""reverse contour direction"""
		self._nakedParent.ReverseContour(self._index)
		self._buildSegments()
			
	def setStartSegment(self, segmentIndex):
		"""set the first node on the contour"""
		self._nakedParent.SetStartNode(self._startNodeIndex + segmentIndex)
		self.getParent()._invalidateContours()
		self.getParent()._buildContours()

	def copy(self, aParent=None):
		"""Copy this object -- result is an ObjectsRF flavored object.
		There is no way to make this work using FontLab objects.
		Copy is mainly used for glyphmath.
		"""
		raise RoboFabError, "copy() for objectsFL.RContour is not implemented."
		


class RSegment(BaseSegment):
	
	_title = "FLSegment"
	
	def __init__(self, flNodeIndex):
		BaseSegment.__init__(self)
		self._nodeIndex = flNodeIndex
		self._looseOffCurve = []	#a list of indexes to loose off curve nodes
	
	def _get__node(self):
		glyph = self.getParent()._nakedParent
		return glyph.nodes[self._nodeIndex]
	
	_node = property(_get__node, doc="")
	
	def _get_qOffCurve(self):
		nodes = self.getParent()._nakedParent.nodes
		off = []
		for x in self._looseOffCurve:
			off.append(nodes[x])
		return off
		
	_qOffCurve = property(_get_qOffCurve, doc="free floating off curve nodes in the segment")

	def _get_index(self):
		contour = self.getParent()
		return self._nodeIndex - contour._startNodeIndex
		
	index = property(_get_index, doc="")
	
	def _isQCurve(self):
		# loose off curves only appear in q curves
		if len(self._looseOffCurve) != 0:
			return True
		return False

	def _get_type(self):
		if self._isQCurve():
			return QCURVE
		return _flToRFSegmentType(self._node.type)
	
	def _set_type(self, segmentType):
		if self._isQCurve():
			raise RoboFabError, 'qcurve point types cannot be changed'
		oldNode = self._node
		oldType = oldNode.type
		oldPointType = _flToRFSegmentType(oldType)
		if oldPointType == MOVE:
			raise RoboFabError, '%s point types cannot be changed'%oldPointType
		if segmentType == MOVE or segmentType == OFFCURVE:
			raise RoboFabError, '%s point types cannot be assigned'%oldPointType
		if oldPointType == segmentType:
			return
		oldNode.type = _rfToFLSegmentType(segmentType)
		
	type = property(_get_type, _set_type, doc="")
			
	def _get_smooth(self):
		alignment = self._node.alignment
		if alignment == flSMOOTH or alignment == flFIXED:
			return True
		return False
	
	def _set_smooth(self, value):
		if value:
			self._node.alignment = flSMOOTH
		else:
			self._node.alignment = flSHARP
		
	smooth = property(_get_smooth, _set_smooth, doc="")

	def _get_points(self):
		points = []
		node = self._node
		# gather the off curves
		#
		# are we dealing with a qCurve? ugh.
		# gather the loose off curves
		if self._isQCurve():
			off = self._qOffCurve
			x = 0
			for n in off:
				p = RPoint(0)
				p.setParent(self)
				p._qOffIndex = x
				points.append(p)
				x = x + 1
		# otherwise get the points associated with the node
		else:
			index = 1
			for point in node.points[1:]:
				p = RPoint(index)
				p.setParent(self)
				points.append(p)
				index = index + 1
		# the last point should always be the on curve
		p = RPoint(0)
		p.setParent(self)
		points.append(p)
		return points
		
	points = property(_get_points, doc="")

	def _get_selected(self):
		return self._node.selected
	
	def _set_selected(self, value):
		self._node.selected = value
	
	selected = property(_get_selected, _set_selected, doc="")

	def move(self, (x, y)):
		x, y = roundPt((x, y))
		self._node.Shift(Point(x, y))
		if self._isQCurve():
			qOff = self._qOffCurve
			for node in qOff:
				node.Shift(Point(x, y))

	def copy(self, aParent=None):
		"""Copy this object -- result is an ObjectsRF flavored object.
		There is no way to make this work using FontLab objects.
		Copy is mainly used for glyphmath.
		"""
		raise RoboFabError, "copy() for objectsFL.RSegment is not implemented."

		

class RPoint(BasePoint):
				
	_title = "FLPoint"
	
	def __init__(self, pointIndex):
		#BasePoint.__init__(self)
		self._pointIndex = pointIndex
		self._qOffIndex = None
		
	def _get__parentGlyph(self):
		return self._parentContour.getParent()
	
	_parentGlyph = property(_get__parentGlyph, doc="")

	def _get__parentContour(self):
		return self._parentSegment.getParent()
		
	_parentContour = property(_get__parentContour, doc="")

	def _get__parentSegment(self):
		return self.getParent()
	
	_parentSegment = property(_get__parentSegment, doc="")

	def _get__node(self):
		if self._qOffIndex is not None:
			return self.getParent()._qOffCurve[self._qOffIndex]
		return self.getParent()._node
	
	_node = property(_get__node, doc="")

	def _get__point(self):
		return self._node.points[self._pointIndex]

	_point = property(_get__point, doc="")

	def _get_x(self):
		return self._point.x
		
	def _set_x(self, value):
		value = int(round(value))
		self._point.x = value
	
	x = property(_get_x, _set_x, doc="")

	def _get_y(self):
		return self._point.y
	
	def _set_y(self, value):
		value = int(round(value))
		self._point.y = value

	y = property(_get_y, _set_y, doc="")

	def _get_type(self):
		if self._pointIndex == 0:
			# FL store quad contour data as a list of off curves and lines
			# (see note in RContour._buildSegments). So, we need to do
			# a bit of trickery to return a decent point type.
			# if the straight FL node type is off curve, it is a loose
			# quad off curve. return that.
			tp = _flToRFSegmentType(self._node.type)
			if tp == OFFCURVE:
				return OFFCURVE
			# otherwise we are dealing with an on curve. in this case,
			# we attempt to get the parent segment type and return it.
			segment = self.getParent()
			if segment is not None:
				return segment.type
			# we must not have a segment, fall back to straight conversion
			return tp
		return OFFCURVE
	
	type = property(_get_type, doc="")
	
	def _set_selected(self, value):
		if self._pointIndex == 0:
			self._node.selected = value
	
	def _get_selected(self):
		if self._pointIndex == 0:
			return self._node.selected
		return False
		
	selected = property(_get_selected, _set_selected, doc="")

	def move(self, (x, y)):
		x, y = roundPt((x, y))
		self._point.Shift(Point(x, y))
	
	def scale(self, (x, y), center=(0, 0)):
		centerX, centerY = roundPt(center)
		point = self._point
		point.x, point.y = _scalePointFromCenter((point.x, point.y), (x, y), (centerX, centerY))
	
	def copy(self, aParent=None):
		"""Copy this object -- result is an ObjectsRF flavored object.
		There is no way to make this work using FontLab objects.
		Copy is mainly used for glyphmath.
		"""
		raise RoboFabError, "copy() for objectsFL.RPoint is not implemented."
		

class RBPoint(BaseBPoint):
	
	_title = "FLBPoint"
	
	def __init__(self, segmentIndex):
		#BaseBPoint.__init__(self)
		self._segmentIndex = segmentIndex
		
	def _get__parentSegment(self):
		return self.getParent().segments[self._segmentIndex]
	
	_parentSegment = property(_get__parentSegment, doc="")
	
	def _get_index(self):
		return self._segmentIndex
	
	index = property(_get_index, doc="")
	
	def _get_selected(self):
		return self._parentSegment.selected
	
	def _set_selected(self, value):
		self._parentSegment.selected = value
		
	selected = property(_get_selected, _set_selected, doc="")

	def copy(self, aParent=None):
		"""Copy this object -- result is an ObjectsRF flavored object.
		There is no way to make this work using FontLab objects.
		Copy is mainly used for glyphmath.
		"""
		raise RoboFabError, "copy() for objectsFL.RBPoint is not implemented."
			
		
class RComponent(BaseComponent):
	
	"""RoboFab wrapper for FL Component object"""

	_title = "FLComponent"

	def __init__(self, flComponent, index):
		BaseComponent.__init__(self)
		self._object =  flComponent
		self._index=index
		
	def _get_index(self):
		return self._index
		
	index = property(_get_index, doc="index of component")

	def _get_baseGlyph(self):
		return self._object.parent.parent[self._object.index].name
		
	baseGlyph = property(_get_baseGlyph, doc="")

	def _get_offset(self):
		return (int(self._object.delta.x), int(self._object.delta.y))
	
	def _set_offset(self, value):
		value = roundPt((value[0], value[1]))
		self._object.delta=Point(value[0], value[1])
		
	offset = property(_get_offset, _set_offset, doc="the offset of the component")

	def _get_scale(self):
		return (self._object.scale.x, self._object.scale.y)
	
	def _set_scale(self, (x, y)):
		self._object.scale=Point(x, y)
		
	scale = property(_get_scale, _set_scale, doc="the scale of the component")

	def move(self, (x, y)):
		"""Move the component"""
		x, y = roundPt((x, y))
		self._object.delta=Point(self._object.delta.x+x, self._object.delta.y+y)
	
	def decompose(self):
		"""Decompose the component"""
		self._object.Paste()

	def copy(self, aParent=None):
		"""Copy this object -- result is an ObjectsRF flavored object.
		There is no way to make this work using FontLab objects.
		Copy is mainly used for glyphmath.
		"""
		raise RoboFabError, "copy() for objectsFL.RComponent is not implemented."
		


class RAnchor(BaseAnchor):
	"""RoboFab wrapper for FL Anchor object"""

	_title = "FLAnchor"

	def __init__(self, flAnchor, index):
		BaseAnchor.__init__(self)
		self._object =  flAnchor
		self._index = index
	
	def _get_y(self):
		return self._object.y

	def _set_y(self, value):
		self._object.y = int(round(value))

	y = property(_get_y, _set_y, doc="y")
	
	def _get_x(self):
		return self._object.x

	def _set_x(self, value):
		self._object.x = int(round(value))

	x = property(_get_x, _set_x, doc="x")
	
	def _get_name(self):
		return self._object.name

	def _set_name(self, value):
		self._object.name = value

	name = property(_get_name, _set_name, doc="name")
	
	def _get_mark(self):
		return self._object.mark

	def _set_mark(self, value):
		self._object.mark = value

	mark = property(_get_mark, _set_mark, doc="mark")
	
	def _get_index(self):
		return self._index
		
	index = property(_get_index, doc="index of the anchor")

	def _get_position(self):
		return (self._object.x, self._object.y)
		
	def _set_position(self, value):
		value = roundPt((value[0], value[1]))
		self._object.x=value[0]
		self._object.y=value[1]

	position = property(_get_position, _set_position, doc="position of the anchor")



class RGuide(BaseGuide):
	
	"""RoboFab wrapper for FL Guide object"""

	_title = "FLGuide"

	def __init__(self, flGuide, index):
		BaseGuide.__init__(self)
		self._object = flGuide
		self._index = index
		
	def __repr__(self):
		# this is a doozy!
		parent = "unknown_parent"
		parentObject = self.getParent()
		if parentObject is not None:
			# do we have a font?
			try:
				parent = parentObject.info.postscriptFullName
			except AttributeError:
				# or do we have a glyph?
				try:
					parent = parentObject.name
				# we must be an orphan
				except AttributeError: pass
		return "<Robofab guide wrapper for %s>"%parent
		
	def _get_position(self):
		return self._object.position

	def _set_position(self, value):
		self._object.position = value

	position = property(_get_position, _set_position, doc="position")
	
	def _get_angle(self):
		return self._object.angle

	def _set_angle(self, value):
		self._object.angle = value

	angle = property(_get_angle, _set_angle, doc="angle")
	
	def _get_index(self):
		return self._index

	index = property(_get_index, doc="index of the guide")
	

class RGroups(BaseGroups):
	
	"""RoboFab wrapper for FL group data"""
	
	_title = "FLGroups"
	
	def __init__(self, aDict):
		self.update(aDict)
	
	def __setitem__(self, key, value):
		# override baseclass so that data is stored in FL classes
		if not isinstance(key, str):
			raise RoboFabError, 'key must be a string'
		if not isinstance(value, list):
			raise RoboFabError, 'group must be a list'
		super(RGroups, self).__setitem__(key, value)
		self._setFLGroups()
			
	def __delitem__(self, key):
		# override baseclass so that data is stored in FL classes
		super(RGroups, self).__delitem__(key)
		self._setFLGroups()
		
	def _setFLGroups(self):
		# set the group data into the font.
		if self.getParent() is not None:
			groups = []
			for i in self.keys():
				value = ' '.join(self[i])
				groups.append(': '.join([i, value]))
			groups.sort()
			self.getParent().naked().classes = groups
	
	def update(self, aDict):
		# override baseclass so that data is stored in FL classes
		super(RGroups, self).update(aDict)
		self._setFLGroups()

	def clear(self):
		# override baseclass so that data is stored in FL classes
		super(RGroups, self).clear()
		self._setFLGroups()
			
	def pop(self, key):
		# override baseclass so that data is stored in FL classes
		i = super(RGroups, self).pop(key)
		self._setFLGroups()
		return i
		
	def popitem(self):
		# override baseclass so that data is stored in FL classes
		i = super(RGroups, self).popitem()
		self._setFLGroups()
		return i
	
	def setdefault(self, key, value=None):
		# override baseclass so that data is stored in FL classes
		i = super(RGroups, self).setdefault(key, value)
		self._setFLGroups()
		return i


class RKerning(BaseKerning):
	
	"""RoboFab wrapper for FL Kerning data"""
	
	_title = "FLKerning"

	def __setitem__(self, pair, value):
		if not isinstance(pair, tuple):
			raise RoboFabError, 'kerning pair must be a tuple: (left, right)'
		else:
			if len(pair) != 2:
				raise RoboFabError, 'kerning pair must be a tuple: (left, right)'
			else:
				if value == 0:
					if self._kerning.get(pair) is not None:
						#see note about setting kerning values to 0 below
						self._setFLKerning(pair, 0)
						del self._kerning[pair]
				else:
					#self._kerning[pair] = value
					self._setFLKerning(pair, value)
					
	def _setFLKerning(self, pair, value):
		# write a pair back into the font
		#
		# this is fairly speedy, but setting a pair to 0 is roughly
		# 2-3 times slower than setting a real value. this is because
		# of all the hoops that must be jumped through to keep FL
		# from storing kerning pairs with a value of 0.
		parentFont = self.getParent().naked()
		left = parentFont[pair[0]]
		right = parentFont.FindGlyph(pair[1])
		# the left glyph doesn not exist
		if left is None:
			return
		# the right glyph doesn not exist
		if right == -1:
			return
		self._kerning[pair] = value
		leftName = pair[0]
		value = int(round(value))
		# pairs set to 0 need to be handled carefully. FL will allow
		# for pairs to have a value of 0 (!?), so we must catch them
		# when they pop up and make sure that the pair is actually
		# removed from the font.
		if value == 0:
			foundPair = False
			# if the value is 0, we don't need to construct a pair
			# we just need to make sure that the pair is not in the list
			pairs = []
			# so, go through all the pairs and add them to a new list
			for flPair in left.kerning:
				# we have found the pair. flag it.
				if flPair.key == right:
					foundPair = True
				# not the pair. add it to the list.
				else:
					pairs.append((flPair.key, flPair.value))
			# if we found it, write it back to the glyph.
			if foundPair:
				left.kerning = []
				for p in pairs:
					new = KerningPair(p[0], p[1])
					left.kerning.append(new)
		else:
			# non-zero pairs are a bit easier to handle
			# we just need to look to see if the pair exists
			# if so, change the value and stop the loop.
			# if not, add a new pair to the glyph
			self._kerning[pair] = value
			foundPair = False
			for flPair in left.kerning:
				if flPair.key == right:
					flPair.value = value
					foundPair = True
					break
			if not foundPair:
				p = KerningPair(right, value)
				left.kerning.append(p)
		
	def update(self, kerningDict):
		"""replace kerning data with the data in the given kerningDict"""
		# override base class here for speed
		parentFont = self.getParent().naked()
		# add existing data to the new kerning dict is not being replaced
		for pair in self.keys():
			if not kerningDict.has_key(pair):
				kerningDict[pair] = self._kerning[pair]
		# now clear the existing kerning to make sure that
		# all the kerning in residing in the glyphs is gone
		self.clear()
		self._kerning = kerningDict
		kDict = {}
		# nest the pairs into a dict keyed by the left glyph
		# {'A':{'A':-10, 'B':20, ...}, 'B':{...}, ...}
		for left, right in kerningDict.keys():
			value = kerningDict[left, right]
			if not left in kDict:
				kDict[left] = {}
			kDict[left][right] = value
		for left in kDict.keys():
			leftGlyph = parentFont[left]
			if leftGlyph is not None:
				for right in kDict[left].keys():
					value = kDict[left][right]
					if value != 0:
						rightIndex = parentFont.FindGlyph(right)
						if rightIndex != -1:
							p = KerningPair(rightIndex, value)
							leftGlyph.kerning.append(p)
				
	def clear(self):
		"""clear all kerning"""
		# override base class here for speed
		self._kerning = {}
		for glyph in self.getParent().naked().glyphs:
			glyph.kerning = []

	def __add__(self, other):
		"""Math operations on FL Kerning objects return RF Kerning objects
		as they need to be orphaned objects and FL can't deal with that."""
		from sets import Set
		from robofab.objects.objectsRF import RKerning as _RKerning
		new = _RKerning()
		k = Set(self.keys()) | Set(other.keys())
		for key in k:
			new[key] = self.get(key, 0) + other.get(key, 0)
		return new
	
	def __sub__(self, other):
		"""Math operations on FL Kerning objects return RF Kerning objects
		as they need to be orphaned objects and FL can't deal with that."""
		from sets import Set
		from robofab.objects.objectsRF import RKerning as _RKerning
		new = _RKerning()
		k = Set(self.keys()) | Set(other.keys())
		for key in k:
			new[key] = self.get(key, 0) - other.get(key, 0)
		return new

	def __mul__(self, factor):
		"""Math operations on FL Kerning objects return RF Kerning objects
		as they need to be orphaned objects and FL can't deal with that."""
		from robofab.objects.objectsRF import RKerning as _RKerning
		new = _RKerning()
		for name, value in self.items():
			new[name] = value * factor
		return new
	
	__rmul__ = __mul__

	def __div__(self, factor):
		"""Math operations on FL Kerning objects return RF Kerning objects
		as they need to be orphaned objects and FL can't deal with that."""
		if factor == 0:
			raise ZeroDivisionError
		return self.__mul__(1.0/factor)
			

class RLib(BaseLib):
	
	"""RoboFab wrapper for FL lib"""
	
	# XXX: As of FL 4.6 the customdata field in glyph objects is busted.
	# storing anything there causes the glyph to become uneditable.
	# however, the customdata field in font objects is stable.
	
	def __init__(self, aDict):
		self.update(aDict)
		
	def __setitem__(self, key, value):
		# override baseclass so that data is stored in customdata field
		super(RLib, self).__setitem__(key, value)
		self._stashLib()
			
	def __delitem__(self, key):
		# override baseclass so that data is stored in customdata field
		super(RLib, self).__delitem__(key)
		self._stashLib()
		
	def _stashLib(self):
		# write the plist into the customdata field of the FL object
		if self.getParent() is None:
			return
		if not self:
			data = None
		elif len(self) == 1 and "org.robofab.fontlab.customdata" in self:
			data = self["org.robofab.fontlab.customdata"].data
		else:
			f = StringIO()
			writePlist(self, f)
			data = f.getvalue()
			f.close()
		parent = self.getParent()
		parent.naked().customdata = data
	
	def update(self, aDict):
		# override baseclass so that data is stored in customdata field
		super(RLib, self).update(aDict)
		self._stashLib()

	def clear(self):
		# override baseclass so that data is stored in customdata field
		super(RLib, self).clear()
		self._stashLib()
			
	def pop(self, key):
		# override baseclass so that data is stored in customdata field
		i = super(RLib, self).pop(key)
		self._stashLib()
		return i
		
	def popitem(self):
		# override baseclass so that data is stored in customdata field
		i = super(RLib, self).popitem()
		self._stashLib()
		return i
	
	def setdefault(self, key, value=None):
		# override baseclass so that data is stored in customdata field
		i = super(RLib, self).setdefault(key, value)
		self._stashLib()
		return i


def _infoMapDict(**kwargs):
	default = dict(
		nakedAttribute=None,
		type=None,
		requiresSetNum=False,
		masterSpecific=False,
		libLocation=None,
		specialGetSet=False
	)
	default.update(kwargs)
	return default

def _flipDict(d):
	f = {}
	for k, v in d.items():
		f[v] = k
	return f

_styleMapStyleName_fromFL = {
	64 : "regular",
	1  : "italic",
	32 : "bold",
	33 : "bold italic"
}
_styleMapStyleName_toFL = _flipDict(_styleMapStyleName_fromFL)

_postscriptWindowsCharacterSet_fromFL = {
	0   : 1,
	1   : 2,
	2   : 3,
	77  : 4,
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
	255 : 20,
}
_postscriptWindowsCharacterSet_toFL = _flipDict(_postscriptWindowsCharacterSet_fromFL)

_openTypeOS2Type_toFL = {
	1 : 0x0002,
	2 : 0x0004,
	3 : 0x0008,
	8 : 0x0100,
	9 : 0x0200,
}
_openTypeOS2Type_fromFL = _flipDict(_openTypeOS2Type_toFL)

_openTypeOS2WidthClass_fromFL = {
	"Ultra-condensed" : 1,
	"Extra-condensed" : 2,
	"Condensed"		  : 3,
	"Semi-condensed"  : 4,
	"Medium (normal)" : 5,
	"Semi-expanded"	  : 6,
	"Expanded"		  : 7,
	"Extra-expanded"  : 8,
	"Ultra-expanded"  : 9,
}
_openTypeOS2WidthClass_toFL = _flipDict(_openTypeOS2WidthClass_fromFL)

_postscriptHintAttributes = set((
	"postscriptBlueValues",
	"postscriptOtherBlues",
	"postscriptFamilyBlues",
	"postscriptFamilyOtherBlues",
	"postscriptStemSnapH",
	"postscriptStemSnapV",
))


class RInfo(BaseInfo):

	"""RoboFab wrapper for FL Font Info"""

	_title = "FLInfo"

	_ufoToFLAttrMapping = {
		"familyName"							: _infoMapDict(valueType=str, nakedAttribute="family_name"),
		"styleName"								: _infoMapDict(valueType=str, nakedAttribute="style_name"),
		"styleMapFamilyName"					: _infoMapDict(valueType=str, nakedAttribute="menu_name"),
		"styleMapStyleName"						: _infoMapDict(valueType=str, nakedAttribute="font_style", specialGetSet=True),
		"versionMajor"							: _infoMapDict(valueType=int, nakedAttribute="version_major"),
		"versionMinor"							: _infoMapDict(valueType=int, nakedAttribute="version_minor"),
		"year"									: _infoMapDict(valueType=int, nakedAttribute="year"),
		"copyright"								: _infoMapDict(valueType=str, nakedAttribute="copyright"),
		"trademark"								: _infoMapDict(valueType=str, nakedAttribute="trademark"),
		"unitsPerEm"							: _infoMapDict(valueType=int, nakedAttribute="upm"),
		"descender"								: _infoMapDict(valueType=int, nakedAttribute="descender", masterSpecific=True),
		"xHeight"								: _infoMapDict(valueType=int, nakedAttribute="x_height", masterSpecific=True),
		"capHeight"								: _infoMapDict(valueType=int, nakedAttribute="cap_height", masterSpecific=True),
		"ascender"								: _infoMapDict(valueType=int, nakedAttribute="ascender", masterSpecific=True),
		"italicAngle"							: _infoMapDict(valueType=float, nakedAttribute="italic_angle"),
		"note"									: _infoMapDict(valueType=str, nakedAttribute="note"),
		"openTypeHeadCreated"					: _infoMapDict(valueType=str, nakedAttribute=None, specialGetSet=True), # i can't figure out the ttinfo.head_creation values
		"openTypeHeadLowestRecPPEM"				: _infoMapDict(valueType=int, nakedAttribute="ttinfo.head_lowest_rec_ppem"),
		"openTypeHeadFlags"						: _infoMapDict(valueType="intList", nakedAttribute=None), # There is an attribute (ttinfo.head_flags), but no user interface.
		"openTypeHheaAscender"					: _infoMapDict(valueType=int, nakedAttribute="ttinfo.hhea_ascender"),
		"openTypeHheaDescender"					: _infoMapDict(valueType=int, nakedAttribute="ttinfo.hhea_descender"),
		"openTypeHheaLineGap"					: _infoMapDict(valueType=int, nakedAttribute="ttinfo.hhea_line_gap"),
		"openTypeHheaCaretSlopeRise"			: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeHheaCaretSlopeRun"				: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeHheaCaretOffset"				: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeNameDesigner"					: _infoMapDict(valueType=str, nakedAttribute="designer"),
		"openTypeNameDesignerURL"				: _infoMapDict(valueType=str, nakedAttribute="designer_url"),
		"openTypeNameManufacturer"				: _infoMapDict(valueType=str, nakedAttribute="source"),
		"openTypeNameManufacturerURL"			: _infoMapDict(valueType=str, nakedAttribute="vendor_url"),
		"openTypeNameLicense"					: _infoMapDict(valueType=str, nakedAttribute="license"),
		"openTypeNameLicenseURL"				: _infoMapDict(valueType=str, nakedAttribute="license_url"),
		"openTypeNameVersion"					: _infoMapDict(valueType=str, nakedAttribute="tt_version"),
		"openTypeNameUniqueID"					: _infoMapDict(valueType=str, nakedAttribute="tt_u_id"),
		"openTypeNameDescription"				: _infoMapDict(valueType=str, nakedAttribute="notice"),
		"openTypeNamePreferredFamilyName"		: _infoMapDict(valueType=str, nakedAttribute="pref_family_name"),
		"openTypeNamePreferredSubfamilyName"	: _infoMapDict(valueType=str, nakedAttribute="pref_style_name"),
		"openTypeNameCompatibleFullName"		: _infoMapDict(valueType=str, nakedAttribute="mac_compatible"),
		"openTypeNameSampleText"				: _infoMapDict(valueType=str, nakedAttribute=None),
		"openTypeNameWWSFamilyName"				: _infoMapDict(valueType=str, nakedAttribute=None),
		"openTypeNameWWSSubfamilyName"			: _infoMapDict(valueType=str, nakedAttribute=None),
		"openTypeOS2WidthClass"					: _infoMapDict(valueType=int, nakedAttribute="width"),
		"openTypeOS2WeightClass"				: _infoMapDict(valueType=int, nakedAttribute="weight_code", specialGetSet=True),
		"openTypeOS2Selection"					: _infoMapDict(valueType="intList", nakedAttribute=None), # ttinfo.os2_fs_selection only returns 0
		"openTypeOS2VendorID"					: _infoMapDict(valueType=str, nakedAttribute="vendor"),
		"openTypeOS2Panose"						: _infoMapDict(valueType="intList", nakedAttribute="panose", specialGetSet=True),
		"openTypeOS2FamilyClass"				: _infoMapDict(valueType="intList", nakedAttribute="ttinfo.os2_s_family_class", specialGetSet=True),
		"openTypeOS2UnicodeRanges"				: _infoMapDict(valueType="intList", nakedAttribute="unicoderanges"),
		"openTypeOS2CodePageRanges"				: _infoMapDict(valueType="intList", nakedAttribute="codepages"),
		"openTypeOS2TypoAscender"				: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_s_typo_ascender"),
		"openTypeOS2TypoDescender"				: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_s_typo_descender"),
		"openTypeOS2TypoLineGap"				: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_s_typo_line_gap"),
		"openTypeOS2WinAscent"					: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_us_win_ascent"),
		"openTypeOS2WinDescent"					: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_us_win_descent", specialGetSet=True),
		"openTypeOS2Type"						: _infoMapDict(valueType="intList", nakedAttribute="ttinfo.os2_fs_type", specialGetSet=True),
		"openTypeOS2SubscriptXSize"				: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_subscript_x_size"),
		"openTypeOS2SubscriptYSize"				: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_subscript_y_size"),
		"openTypeOS2SubscriptXOffset"			: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_subscript_x_offset"),
		"openTypeOS2SubscriptYOffset"			: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_subscript_y_offset"),
		"openTypeOS2SuperscriptXSize"			: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_superscript_x_size"),
		"openTypeOS2SuperscriptYSize"			: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_superscript_y_size"),
		"openTypeOS2SuperscriptXOffset"			: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_superscript_x_offset"),
		"openTypeOS2SuperscriptYOffset"			: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_superscript_y_offset"),
		"openTypeOS2StrikeoutSize"				: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_strikeout_size"),
		"openTypeOS2StrikeoutPosition"			: _infoMapDict(valueType=int, nakedAttribute="ttinfo.os2_y_strikeout_position"),
		"openTypeVheaVertTypoAscender"			: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeVheaVertTypoDescender"			: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeVheaVertTypoLineGap"			: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeVheaCaretSlopeRise"			: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeVheaCaretSlopeRun"				: _infoMapDict(valueType=int, nakedAttribute=None),
		"openTypeVheaCaretOffset"				: _infoMapDict(valueType=int, nakedAttribute=None),
		"postscriptFontName"					: _infoMapDict(valueType=str, nakedAttribute="font_name"),
		"postscriptFullName"					: _infoMapDict(valueType=str, nakedAttribute="full_name"),
		"postscriptSlantAngle"					: _infoMapDict(valueType=float, nakedAttribute="slant_angle"),
		"postscriptUniqueID"					: _infoMapDict(valueType=int, nakedAttribute="unique_id"),
		"postscriptUnderlineThickness"			: _infoMapDict(valueType=int, nakedAttribute="underline_thickness"),
		"postscriptUnderlinePosition"			: _infoMapDict(valueType=int, nakedAttribute="underline_position"),
		"postscriptIsFixedPitch"				: _infoMapDict(valueType="boolint", nakedAttribute="is_fixed_pitch"),
		"postscriptBlueValues"					: _infoMapDict(valueType="intList", nakedAttribute="blue_values", masterSpecific=True, requiresSetNum=True),
		"postscriptOtherBlues"					: _infoMapDict(valueType="intList", nakedAttribute="other_blues", masterSpecific=True, requiresSetNum=True),
		"postscriptFamilyBlues"					: _infoMapDict(valueType="intList", nakedAttribute="family_blues", masterSpecific=True, requiresSetNum=True),
		"postscriptFamilyOtherBlues"			: _infoMapDict(valueType="intList", nakedAttribute="family_other_blues", masterSpecific=True, requiresSetNum=True),
		"postscriptStemSnapH"					: _infoMapDict(valueType="intList", nakedAttribute="stem_snap_h", masterSpecific=True, requiresSetNum=True),
		"postscriptStemSnapV"					: _infoMapDict(valueType="intList", nakedAttribute="stem_snap_v", masterSpecific=True, requiresSetNum=True),
		"postscriptBlueFuzz"					: _infoMapDict(valueType=int, nakedAttribute="blue_fuzz", masterSpecific=True),
		"postscriptBlueShift"					: _infoMapDict(valueType=int, nakedAttribute="blue_shift", masterSpecific=True),
		"postscriptBlueScale"					: _infoMapDict(valueType=float, nakedAttribute="blue_scale", masterSpecific=True),
		"postscriptForceBold"					: _infoMapDict(valueType="boolint", nakedAttribute="force_bold", masterSpecific=True),
		"postscriptDefaultWidthX"				: _infoMapDict(valueType=int, nakedAttribute="default_width", masterSpecific=True),
		"postscriptNominalWidthX"				: _infoMapDict(valueType=int, nakedAttribute=None),
		"postscriptWeightName"					: _infoMapDict(valueType=str, nakedAttribute="weight"),
		"postscriptDefaultCharacter"			: _infoMapDict(valueType=str, nakedAttribute="default_character"),
		"postscriptWindowsCharacterSet"			: _infoMapDict(valueType=int, nakedAttribute="ms_charset", specialGetSet=True),
		"macintoshFONDFamilyID"					: _infoMapDict(valueType=int, nakedAttribute="fond_id"),
		"macintoshFONDName"						: _infoMapDict(valueType=str, nakedAttribute="apple_name"),
	}
	_environmentOverrides = ["width", "openTypeOS2WidthClass"] # ugh.

	def __init__(self, font):
		super(RInfo, self).__init__()
		self._object = font

	def _environmentSetAttr(self, attr, value):
		# special fontlab workarounds
		if attr == "width":
			warn("The width attribute has been deprecated. Use the new openTypeOS2WidthClass attribute.", DeprecationWarning)
			attr = "openTypeOS2WidthClass"
		if attr == "openTypeOS2WidthClass":
			if isinstance(value, basestring) and value not in _openTypeOS2WidthClass_toFL:
				print "The openTypeOS2WidthClass value \"%s\" cannot be found in the OpenType OS/2 usWidthClass specification. The value will be set into the FontLab file for now." % value
				self._object.width = value
			else:
				self._object.width = _openTypeOS2WidthClass_toFL[value]
			return
		# get the attribute data
		data = self._ufoToFLAttrMapping[attr]
		flAttr = data["nakedAttribute"]
		valueType = data["valueType"]
		masterSpecific = data["masterSpecific"]
		requiresSetNum = data["requiresSetNum"]
		specialGetSet = data["specialGetSet"]
		# warn about setting attributes not supported by FL
		if flAttr is None:
			print "The attribute %s is not supported by FontLab. This data will not be set." % attr
			return
		# make sure that the value is the proper type for FL
		if valueType == "intList":
			value = [int(i) for i in value]
		elif valueType == "boolint":
			value = int(bool(value))
		elif valueType == str:
			if value is None:
				value = ""
			value = value.encode(LOCAL_ENCODING)
		elif valueType == int and not isinstance(value, int):
			value = int(round(value))
		elif not isinstance(value, valueType):
			value = valueType(value)
		# handle postscript hint bug in FL
		if attr in _postscriptHintAttributes:
			value = self._handlePSHintBug(attr, value)
		# handle special cases
		if specialGetSet:
			attr = "_set_%s" % attr
			method = getattr(self, attr)
			return method(value)
		# set the value
		obj = self._object
		if len(flAttr.split(".")) > 1:
			flAttrList = flAttr.split(".")
			for i in flAttrList[:-1]:
				obj = getattr(obj, i)
			flAttr = flAttrList[-1]
		## set the foo_num attribute if necessary
		if requiresSetNum:
			numAttr = flAttr + "_num"
			setattr(obj, numAttr, len(value))
		## set master 0 if the data is master specific
		if masterSpecific:
			subObj = getattr(obj, flAttr)
			if valueType == "intList":
				for index, v in enumerate(value):
					subObj[0][index] = v
			else:
				subObj[0] = value
		## otherwise use a regular set
		else:
			setattr(obj, flAttr, value)

	def _environmentGetAttr(self, attr):
		# special fontlab workarounds
		if attr == "width":
			warn("The width attribute has been deprecated. Use the new openTypeOS2WidthClass attribute.", DeprecationWarning)
			attr = "openTypeOS2WidthClass"
		if attr == "openTypeOS2WidthClass":
			value = self._object.width
			if value not in _openTypeOS2WidthClass_fromFL:
				print "The existing openTypeOS2WidthClass value \"%s\" cannot be found in the OpenType OS/2 usWidthClass specification." % value
				return
			else:
				return _openTypeOS2WidthClass_fromFL[value]
		# get the attribute data
		data = self._ufoToFLAttrMapping[attr]
		flAttr = data["nakedAttribute"]
		valueType = data["valueType"]
		masterSpecific = data["masterSpecific"]
		specialGetSet = data["specialGetSet"]
		# warn about setting attributes not supported by FL
		if flAttr is None:
			if not _IN_UFO_EXPORT:
				print "The attribute %s is not supported by FontLab." % attr
			return
		# handle special cases
		if specialGetSet:
			attr = "_get_%s" % attr
			method = getattr(self, attr)
			return method()
		# get the value
		if len(flAttr.split(".")) > 1:
			flAttrList = flAttr.split(".")
			obj = self._object
			for i in flAttrList:
				obj = getattr(obj, i)
			value = obj
		else:
			value = getattr(self._object, flAttr)
		# grab the first master value if necessary
		if masterSpecific:
			value = value[0]
		# convert if necessary
		if valueType == "intList":
			value = [int(i) for i in value]
		elif valueType == "boolint":
			value = bool(value)
		elif valueType == str:
			if value is None:
				pass
			else:
				value = unicode(value, LOCAL_ENCODING)
		elif not isinstance(value, valueType):
			value = valueType(value)
		return value

	# ------------------------------
	# individual attribute overrides
	# ------------------------------

	# styleMapStyleName

	def _get_styleMapStyleName(self):
		return _styleMapStyleName_fromFL[self._object.font_style]

	def _set_styleMapStyleName(self, value):
		value = _styleMapStyleName_toFL[value]
		self._object.font_style = value

#	# openTypeHeadCreated
#
#	# fontlab epoch: 1969-12-31 19:00:00
#
#	def _get_openTypeHeadCreated(self):
#		value = self._object.ttinfo.head_creation
#		epoch = datetime.datetime(1969, 12, 31, 19, 0, 0)
#		delta = datetime.timedelta(seconds=value[0])
#		t = epoch - delta
#		string = "%s-%s-%s %s:%s:%s" % (str(t.year).zfill(4), str(t.month).zfill(2), str(t.day).zfill(2), str(t.hour).zfill(2), str(t.minute).zfill(2), str(t.second).zfill(2))
#		return string
#
#	def _set_openTypeHeadCreated(self, value):
#		date, time = value.split(" ")
#		year, month, day = [int(i) for i in date.split("-")]
#		hour, minute, second = [int(i) for i in time.split(":")]
#		value = datetime.datetime(year, month, day, hour, minute, second)
#		epoch = datetime.datetime(1969, 12, 31, 19, 0, 0)
#		delta = epoch - value
#		seconds = delta.seconds
#		self._object.ttinfo.head_creation[0] = seconds

	# openTypeOS2WeightClass

	def _get_openTypeOS2WeightClass(self):
		value = self._object.weight_code
		if value == -1:
			value = None
		return value

	def _set_openTypeOS2WeightClass(self, value):
		self._object.weight_code = value

	# openTypeOS2WinDescent

	def _get_openTypeOS2WinDescent(self):
		return self._object.ttinfo.os2_us_win_descent

	def _set_openTypeOS2WinDescent(self, value):
		if value < 0:
			warn("FontLab can only handle positive values for openTypeOS2WinDescent.")
			value = abs(value)
		self._object.ttinfo.os2_us_win_descent = value

	# openTypeOS2Type

	def _get_openTypeOS2Type(self):
		value = self._object.ttinfo.os2_fs_type
		intList = []
		for bit, bitNumber in _openTypeOS2Type_fromFL.items():
			if value & bit:
				intList.append(bitNumber)
		return intList

	def _set_openTypeOS2Type(self, values):
		value = 0
		for bitNumber in values:
			bit = _openTypeOS2Type_toFL[bitNumber]
			value = value | bit
		self._object.ttinfo.os2_fs_type = value

	# openTypeOS2Panose

	def _get_openTypeOS2Panose(self):
		return [i for i in self._object.panose]

	def _set_openTypeOS2Panose(self, values):
		for index, value in enumerate(values):
			self._object.panose[index] = value

	# openTypeOS2FamilyClass

	def _get_openTypeOS2FamilyClass(self):
		value = self._object.ttinfo.os2_s_family_class
		for classID in range(15):
			classValue = classID * 256
			if classValue > value:
				classID -= 1
				classValue = classID * 256
				break
		subclassID = value - classValue
		return [classID, subclassID]

	def _set_openTypeOS2FamilyClass(self, values):
		classID, subclassID = values
		classID = classID * 256
		value = classID + subclassID
		self._object.ttinfo.os2_s_family_class = value

	# postscriptWindowsCharacterSet

	def _get_postscriptWindowsCharacterSet(self):
		value = self._object.ms_charset
		value = _postscriptWindowsCharacterSet_fromFL[value]
		return value

	def _set_postscriptWindowsCharacterSet(self, value):
		value = _postscriptWindowsCharacterSet_toFL[value]
		self._object.ms_charset = value

	# -----------------
	# FL bug workaround
	# -----------------

	def _handlePSHintBug(self, attribute, values):
		"""Function to handle problems with FontLab not allowing the max number of
		alignment zones to be set to the max number.
		Input:  the name of the zones and the values to be set
		Output: a warning when there are too many values to be set
				and the max values which FontLab will allow.
		"""
		originalValues = values
		truncatedLength = None
		if attribute in ("postscriptStemSnapH", "postscriptStemSnapV"):
			if len(values) > 10:
				values = values[:10]
				truncatedLength = 10
		elif attribute in ("postscriptBlueValues", "postscriptFamilyBlues"):
			if len(values) > 12:
				values = values[:12]
				truncatedLength = 12
		elif attribute in ("postscriptOtherBlues", "postscriptFamilyOtherBlues"):
			if len(values) > 8:
				values = values[:8]
				truncatedLength = 8
		if truncatedLength is not None:
			 print "* * * WARNING: FontLab will only accept %d %s items maximum from Python. Dropping values: %s." % (truncatedLength, attribute, str(originalValues[truncatedLength:]))
		return values


class RFeatures(BaseFeatures):

	_title = "FLFeatures"

	def __init__(self, font):
		super(RFeatures, self).__init__()
		self._object = font

	def _get_text(self):
		naked = self._object
		features = []
		if naked.ot_classes:
			features.append(_normalizeLineEndings(naked.ot_classes))
		for feature in naked.features:
			features.append(_normalizeLineEndings(feature.value))
		return "".join(features)

	def _set_text(self, value):
		classes, features = splitFeaturesForFontLab(value)
		naked = self._object
		naked.ot_classes = classes
		naked.features.clean()
		for featureName, featureText in features:
			f = Feature(featureName, featureText)
			naked.features.append(f)

	text = property(_get_text, _set_text, doc="raw feature text.")

