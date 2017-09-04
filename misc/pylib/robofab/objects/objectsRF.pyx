"""UFO for GlifLib"""

from robofab import RoboFabError, RoboFabWarning
from robofab.objects.objectsBase import BaseFont, BaseKerning, BaseGroups, BaseInfo, BaseFeatures, BaseLib,\
		BaseGlyph, BaseContour, BaseSegment, BasePoint, BaseBPoint, BaseAnchor, BaseGuide, BaseComponent, \
		relativeBCPIn, relativeBCPOut, absoluteBCPIn, absoluteBCPOut, _box,\
		_interpolate, _interpolatePt, roundPt, addPt,\
		MOVE, LINE, CORNER, CURVE, QCURVE, OFFCURVE,\
		BasePostScriptFontHintValues, postScriptHintDataLibKey, BasePostScriptGlyphHintValues

import os


__all__ = [	"CurrentFont", 
		"CurrentGlyph", 'OpenFont',
		'RFont', 'RGlyph', 'RContour',
		'RPoint', 'RBPoint', 'RAnchor',
		'RComponent'
		]



def CurrentFont():
	return None

def CurrentGlyph():
	return None

def OpenFont(path=None, note=None):
	"""Open a font from a path. If path is not given, present the user with a dialog."""
	if not note:
		note = 'select a .ufo directory'
	if not path:
		from robofab.interface.all.dialogs import GetFolder
		path = GetFolder(note)
	if path:
		try:
			return RFont(path)
		except OSError:
			from robofab.interface.all.dialogs import Message
			Message("%s is not a valid .UFO font. But considering it's all XML, why don't  you have a look inside with a simple text editor."%(path))
	else:
		return None
		
def NewFont(familyName=None, styleName=None):
	"""Make a new font"""
	new = RFont()
	if familyName is not None:
		new.info.familyName = familyName
	if styleName is not None:
		new.info.styleName = styleName
	return new
	
def AllFonts():
	"""AllFonts can't work in plain python usage. It's really up to some sort of application
	to keep track of which fonts are open."""
	raise NotImplementedError
	

class PostScriptFontHintValues(BasePostScriptFontHintValues):
	"""	Font level PostScript hints object for objectsRF usage.
		If there are values in the lib, use those.
		If there are no values in the lib, use defaults.
		
		The psHints attribute for objectsRF.RFont is basically just the
		data read from the Lib. When the object saves to UFO, the 
		hints are written back to the lib, which is then saved.
		
	"""
	
	def __init__(self, aFont=None, data=None):
		self.setParent(aFont)
		BasePostScriptFontHintValues.__init__(self)
		if aFont is not None:
			# in version 1, this data was stored in the lib
			# if it is still there, guess that it is correct
			# move it to font info and remove it from the lib.
			libData = aFont.lib.get(postScriptHintDataLibKey)
			if libData is not None:
				self.fromDict(libData)
				del libData[postScriptHintDataLibKey]
		if data is not None:
			self.fromDict(data)

def getPostScriptHintDataFromLib(aFont, fontLib):
	hintData = fontLib.get(postScriptHintDataLibKey)
	psh = PostScriptFontHintValues(aFont)
	psh.fromDict(hintData)
	return psh
	
class PostScriptGlyphHintValues(BasePostScriptGlyphHintValues):
	"""	Glyph level PostScript hints object for objectsRF usage.
		If there are values in the lib, use those.
		If there are no values in the lib, be empty.
		
	"""
	def __init__(self, aGlyph=None, data=None):
		# read the data from the glyph.lib, it won't be anywhere else
		BasePostScriptGlyphHintValues.__init__(self)
		if aGlyph is not None:
			self.setParent(aGlyph)
			self._loadFromLib(aGlyph.lib)
		if data is not None:
			self.fromDict(data)
			
			
class RFont(BaseFont):
	"""UFO font object which reads and writes glif, and keeps the data in memory in between.
	Bahviour:
		- comparable to Font
		- comparable to GlyphSet so that it can be passed to Glif widgets
	"""
	
	_title = "RoboFabFont"
	
	def __init__(self, path=None):
		BaseFont.__init__(self)
		if path is not None:
			self._path = os.path.normpath(os.path.abspath(path))
		else:
			self._path = None
		self._object = {}
		
		self._glyphSet = None
		self._scheduledForDeletion = []	# this is a place for storing glyphs that need to be removed when the font is saved
		
		self.kerning = RKerning()
		self.kerning.setParent(self)
		self.info = RInfo()
		self.info.setParent(self)
		self.features = RFeatures()
		self.features.setParent(self)
		self.groups = RGroups()
		self.groups.setParent(self)
		self.lib = RLib()
		self.lib.setParent(self)
		if path:
			self._loadData(path)
		else:
			self.psHints = PostScriptFontHintValues(self)
			self.psHints.setParent(self)
		
	def __setitem__(self, glyphName, glyph):
		"""Set a glyph at key."""
		self._object[glyphName] = glyph
	
	def __cmp__(self, other):
		"""Compare this font with another, compare if they refer to the same file."""
		if not hasattr(other, '_path'):
			return -1
		if self._object._path == other._object._path and self._object._path is not None: 
			return 0
		else:
			return -1
	
	def __len__(self):
		if self._glyphSet is None:
			return 0
		return len(self._glyphSet)
	
	def _loadData(self, path):
		from robofab.ufoLib import UFOReader
		reader = UFOReader(path)
		fontLib = reader.readLib()
		# info
		reader.readInfo(self.info)
		# kerning
		self.kerning.update(reader.readKerning())
		self.kerning.setChanged(False)
		# groups
		self.groups.update(reader.readGroups())
		# features
		if reader.formatVersion == 1:
			# migrate features from the lib
			features = []
			classes = fontLib.get("org.robofab.opentype.classes")
			if classes is not None:
				del fontLib["org.robofab.opentype.classes"]
				features.append(classes)
			splitFeatures = fontLib.get("org.robofab.opentype.features")
			if splitFeatures is not None:
				order = fontLib.get("org.robofab.opentype.featureorder")
				if order is None:
					order = splitFeatures.keys()
					order.sort()
				else:
					del fontLib["org.robofab.opentype.featureorder"]
				del fontLib["org.robofab.opentype.features"]
				for tag in order:
					oneFeature = splitFeatures.get(tag)
					if oneFeature is not None:
						features.append(oneFeature)
			features = "\n".join(features)
		else:
			features = reader.readFeatures()
		self.features.text = features
		# hint data
		self.psHints = PostScriptFontHintValues(self)
		if postScriptHintDataLibKey in fontLib:
			del fontLib[postScriptHintDataLibKey]
		# lib
		self.lib.update(fontLib)
		# glyphs
		self._glyphSet = reader.getGlyphSet()
		self._hasNotChanged(doGlyphs=False)

	def _loadGlyph(self, glyphName):
		"""Load a single glyph from the glyphSet, on request."""
		from robofab.pens.rfUFOPen import RFUFOPointPen
		g =  RGlyph()
		g.name = glyphName
		pen = RFUFOPointPen(g)
		self._glyphSet.readGlyph(glyphName=glyphName, glyphObject=g, pointPen=pen)
		g.setParent(self)
		g.psHints._loadFromLib(g.lib)
		self._object[glyphName] = g
		self._object[glyphName]._hasNotChanged()
		return g
		
	#def _prepareSaveDir(self, dir):
	#	path = os.path.join(dir, 'glyphs')
	#	if not os.path.exists(path):
	#		os.makedirs(path)

	def _hasNotChanged(self, doGlyphs=True):
		#set the changed state of the font
		if doGlyphs:
			for glyph in self:
				glyph._hasNotChanged()
		self.setChanged(False)
	
	#
	# attributes
	#
	
	def _get_path(self):
		return self._path
	
	path = property(_get_path, doc="path of the font")
		
	#
	# methods for imitating GlyphSet?
	#
			
	def keys(self):
		# the keys are the superset of self._objects.keys() and
		# self._glyphSet.keys(), minus self._scheduledForDeletion
		keys = self._object.keys()
		if self._glyphSet is not None:
			keys.extend(self._glyphSet.keys())
		d = dict()
		for glyphName in keys:
			d[glyphName] = None
		for glyphName in self._scheduledForDeletion:
			if glyphName in d:
				del d[glyphName]
		return d.keys()

	def has_key(self, glyphName):
		# XXX ditto, see above.
		if self._glyphSet is not None:
			hasGlyph = glyphName in self._object or glyphName in self._glyphSet
		else:
			hasGlyph = glyphName in self._object
		return hasGlyph and not glyphName in self._scheduledForDeletion
	
	__contains__ = has_key
	
	def getWidth(self, glyphName):
		if self._object.has_key(glyphName):
			return self._object[glyphName].width
		raise IndexError		# or return None?
		
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
		# a NON-REVERESED map is stored in the lib.
		# this is done because a reveresed map could
		# contain faulty data. for example: "Aacute" contains
		# a component that references "A". Glyph "Aacute" is
		# then deleted. The reverse map would still say that
		# "A" is referenced by "Aacute" even though the
		# glyph has been deleted. So, the stored lib works like this:
		# {
		# 'Aacute' : [
		#		# the last known mod time of the GLIF
		#		1098706856.75,
		#		# component references in a glyph
		#		['A', 'acute']
		#		]
		# }
		import time
		import os
		import re
		componentSearch_RE = re.compile(
			"<component\s+"		# <component
			"[^>]*?"			# anything EXCEPT >
			"base\s*=\s*[\"\']"		# base="
			"(.*?)"			# foo
			"[\"\']"			# "
			)
		rightNow = time.time()
		libKey = "org.robofab.componentMapping"
		previousMap = None
		if self.lib.has_key(libKey):
			previousMap = self.lib[libKey]
		basicMap = {}
		reverseMap = {}
		for glyphName in self.keys():
			componentsToMap = None
			modTime = None
			# get the previous bits of data
			previousModTime = None
			previousList = None
			if previousMap is not None and previousMap.has_key(glyphName):
				previousModTime, previousList = previousMap[glyphName]
			# the glyph has been loaded.
			# simply get the components from it.
			if self._object.has_key(glyphName):
				componentsToMap = [component.baseGlyph for component in self._object[glyphName].components]
			# the glyph has not been loaded.
			else:
				glyphPath = os.path.join(self._glyphSet.dirName, self._glyphSet.contents[glyphName])
				scanGlyph = True
				# test the modified time of the GLIF
				fileModTime = os.path.getmtime(glyphPath)
				if previousModTime is not None and fileModTime == previousModTime:
					# the GLIF almost* certianly has not changed.
					# *theoretically, a user could replace a GLIF
					# with another GLIF that has precisely the same
					# mod time. 
					scanGlyph = False
					componentsToMap = previousList
					modTime = previousModTime
				else:
					# the GLIF is different
					modTime = fileModTime
				if scanGlyph:
					# use regex to extract component
					# base glyphs from the file
					f = open(glyphPath, 'rb')
					data = f.read()
					f.close()
					componentsToMap = componentSearch_RE.findall(data)
			if componentsToMap is not None:
				# store the non-reversed map
				basicMap[glyphName] = (modTime, componentsToMap)
				# reverse the map for the user
				if componentsToMap:
					for baseGlyphName in componentsToMap:
						if not reverseMap.has_key(baseGlyphName):
							reverseMap[baseGlyphName] = []
						reverseMap[baseGlyphName].append(glyphName)
				# if a glyph has been loaded, we do not store data about it in the lib.
				# this is done becuase there is not way to determine the proper mod time
				# for a loaded glyph.
				if modTime is None:
					del basicMap[glyphName]
		# store the map in the lib for re-use
		self.lib[libKey] = basicMap
		return reverseMap
		

	def save(self, destDir=None, doProgress=False, formatVersion=2):
		"""Save the Font in UFO format."""
		# XXX note that when doing "save as" by specifying the destDir argument
		# _all_ glyphs get loaded into memory. This could be optimized by either
		# copying those .glif files that have not been edited or (not sure how
		# well that would work) by simply clearing out self._objects after the
		# save.
		from robofab.ufoLib import UFOWriter
		from robofab.tools.fontlabFeatureSplitter import splitFeaturesForFontLab
		# if no destination is given, or if
		# the given destination is the current
		# path, this is not a save as operation
		if destDir is None or destDir == self._path:
			saveAs = False
			destDir = self._path
		else:
			saveAs = True
		# start a progress bar
		nonGlyphCount = 5
		bar = None
		if doProgress:
			from robofab.interface.all.dialogs import ProgressBar
			bar = ProgressBar("Exporting UFO", nonGlyphCount + len(self._object.keys()))
		# write
		writer = UFOWriter(destDir, formatVersion=formatVersion)
		try:
			# make a shallow copy of the lib. stuff may be added to it.
			fontLib = dict(self.lib)
			# info
			if bar:
				bar.label("Saving info...")
			writer.writeInfo(self.info)
			if bar:
				bar.tick()
			# kerning
			if self.kerning.changed or saveAs:
				if bar:
					bar.label("Saving kerning...")
				writer.writeKerning(self.kerning.asDict())
				if bar:
					bar.tick()
			# groups
			if bar:
				bar.label("Saving groups...")
			writer.writeGroups(self.groups)
			if bar:
				bar.tick()
			# features
			if bar:
				bar.label("Saving features...")
			features = self.features.text
			if features is None:
				features = ""
			if formatVersion == 2:
				writer.writeFeatures(features)
			elif formatVersion == 1:
				classes, features = splitFeaturesForFontLab(features)
				if classes:
					fontLib["org.robofab.opentype.classes"] = classes.strip() + "\n"
				if features:
					featureDict = {}
					for featureName, featureText in features:
						featureDict[featureName] = featureText.strip() + "\n"
					fontLib["org.robofab.opentype.features"] = featureDict
					fontLib["org.robofab.opentype.featureorder"] = [featureName for featureName, featureText in features]
			if bar:
				bar.tick()
			# lib
			if formatVersion == 1:
				fontLib[postScriptHintDataLibKey] = self.psHints.asDict()
			if bar:
				bar.label("Saving lib...")
			writer.writeLib(fontLib)
			if bar:
				bar.tick()
			# glyphs
			glyphNameToFileNameFunc = self.getGlyphNameToFileNameFunc()

			glyphSet = writer.getGlyphSet(glyphNameToFileNameFunc)
			if len(self._scheduledForDeletion) != 0:
				if bar:
					bar.label("Removing deleted glyphs...")
				for glyphName in self._scheduledForDeletion:
					if glyphSet.has_key(glyphName):
						glyphSet.deleteGlyph(glyphName)
				if bar:
					bar.tick()
			if bar:
				bar.label("Saving glyphs...")
			count = nonGlyphCount
			if saveAs:
				glyphNames = self.keys()
			else:
				glyphNames = self._object.keys()
			for glyphName in glyphNames:
				glyph = self[glyphName]
				glyph.psHints._saveToLib(glyph.lib)
				glyph._saveToGlyphSet(glyphSet, glyphName=glyphName, force=saveAs)
				if bar and not count % 10:
					bar.tick(count)
				count = count + 1
			glyphSet.writeContents()
			self._glyphSet = glyphSet
		# only blindly stop if the user says to
		except KeyboardInterrupt:
			bar.close()
			bar = None
		# kill the progress bar
		if bar:
			bar.close()
		# reset internal stuff
		self._path = destDir
		self._scheduledForDeletion = []
		self.setChanged(False)

	def newGlyph(self, glyphName, clear=True):
		"""Make a new glyph with glyphName
		if the glyph exists and clear=True clear the glyph"""
		if clear and glyphName in self:
			g = self[glyphName]
			g.clear()
			w = self.info.postscriptDefaultWidthX
			if w is None:
				w = 0
			g.width = w
			return g
		g = RGlyph()
		g.setParent(self)
		g.name = glyphName
		w = self.info.postscriptDefaultWidthX
		if w is None:
			w = 0
		g.width = w
		g._hasChanged()
		self._object[glyphName] = g
		# is the user adding a glyph that has the same
		# name as one that was deleted earlier?
		if glyphName in self._scheduledForDeletion:
			self._scheduledForDeletion.remove(glyphName)
		return self.getGlyph(glyphName)
		
	def insertGlyph(self, glyph, name=None):
		"""returns a new glyph that has been inserted into the font"""
		if name is None:
			name = glyph.name
		glyph = glyph.copy()
		glyph.name = name
		glyph.setParent(self)
		glyph._hasChanged()
		self._object[name] = glyph
		# is the user adding a glyph that has the same
		# name as one that was deleted earlier?
		if name in self._scheduledForDeletion:
			self._scheduledForDeletion.remove(name)
		return self.getGlyph(name)
		
	def removeGlyph(self, glyphName):
		"""remove a glyph from the font"""
		# XXX! Potential issue with removing glyphs.
		# if a glyph is removed from a font, but it is still referenced
		# by a component, it will give pens some trouble.
		# where does the resposibility for catching this fall?
		# the removeGlyph method? the addComponent method
		# of the various pens? somewhere else? hm... tricky.
		#
		#we won't actually remove it, we will just store it for removal
		# but only if the glyph does exist
		if self.has_key(glyphName) and glyphName not in self._scheduledForDeletion:
			self._scheduledForDeletion.append(glyphName)
		# now delete the object
		if self._object.has_key(glyphName):
			del self._object[glyphName]
		self._hasChanged()
		
	def getGlyph(self, glyphName):
		# XXX getGlyph may have to become private, to avoid duplication
		# with __getitem__
		n = None
		if self._object.has_key(glyphName):
			# have we served this glyph before? it should be in _object
			n = self._object[glyphName]
		else:
			# haven't served it before, is it in the glyphSet then?
			if self._glyphSet is not None and glyphName in self._glyphSet:
				# yes, read the .glif file from disk
				n = self._loadGlyph(glyphName)
		if n is None:
			raise KeyError, glyphName
		return n


class RGlyph(BaseGlyph):
	
	_title = "RGlyph"
	
	def __init__(self):
		BaseGlyph.__init__(self)
		self.contours = []
		self.components = []
		self.anchors = []
		self._unicodes = []
		self.width = 0
		self.note = None
		self._name = "Unnamed Glyph"
		self.selected = False
		self._properties = None
		self._lib = RLib()
		self._lib.setParent(self)
		self.psHints = PostScriptGlyphHintValues()
		self.psHints.setParent(self)

	def __len__(self):
		return len(self.contours) 

	def __getitem__(self, index):
		if index < len(self.contours):
			return self.contours[index]
		raise IndexError
	
	def _hasNotChanged(self):
		for contour in self.contours:
			contour.setChanged(False)
			for segment in contour.segments:
				segment.setChanged(False)
				for point in segment.points:
					point.setChanged(False)
		for component in self.components:
			component.setChanged(False)
		for anchor in self.anchors:
			anchor.setChanged(False)
		self.setChanged(False)
	
	#
	# attributes
	#
	
	def _get_lib(self):
		return self._lib
	
	def _set_lib(self, obj):
		self._lib.clear()
		self._lib.update(obj)
	
	lib = property(_get_lib, _set_lib)
	
	def _get_name(self):
		return self._name
	
	def _set_name(self, value):
		prevName = self._name
		newName = value
		if newName == prevName:
			return
		self._name = newName
		self.setChanged(True)
		font = self.getParent()
		if font is not None:
			# but, this glyph could be linked to a
			# FontLab font, because objectsFL.RGlyph.copy()
			# creates an objectsRF.RGlyph with the parent
			# set to an objectsFL.RFont object. so, check to see
			# if this is a legitimate RFont before trying to 
			# do the objectsRF.RFont glyph name change
			if isinstance(font, RFont):
				font._object[newName] = self
				# is the user changing a glyph's name to the
				# name of a glyph that was deleted earlier?
				if newName in font._scheduledForDeletion:
					font._scheduledForDeletion.remove(newName)
				font.removeGlyph(prevName)
	
	name = property(_get_name, _set_name)
	
	def _get_unicodes(self):
		return self._unicodes
	
	def _set_unicodes(self, value):
		if not isinstance(value, list):
			raise RoboFabError, "unicodes must be a list"
		self._unicodes = value
		self._hasChanged()
			
	unicodes = property(_get_unicodes, _set_unicodes, doc="all unicode values for the glyph")
	
	def _get_unicode(self):
		if len(self._unicodes) == 0:
			return None
		return self._unicodes[0]
	
	def _set_unicode(self, value):
		uni = self._unicodes
		if value is not None:
			if value not in uni:
				self.unicodes.insert(0, value)
			elif uni.index(value) != 0:
				uni.insert(0, uni.pop(uni.index(value)))
				self.unicodes = uni
		
	unicode = property(_get_unicode, _set_unicode, doc="first unicode value for the glyph")
	
	def getPointPen(self):
		from robofab.pens.rfUFOPen import RFUFOPointPen
		return RFUFOPointPen(self)

	def appendComponent(self, baseGlyph, offset=(0, 0), scale=(1, 1)):
		"""append a component to the glyph"""
		new = RComponent(baseGlyph, offset, scale)
		new.setParent(self)
		self.components.append(new)
		self._hasChanged()
		
	def appendAnchor(self, name, position, mark=None):
		"""append an anchor to the glyph"""
		new = RAnchor(name, position, mark)
		new.setParent(self)
		self.anchors.append(new)
		self._hasChanged()
	
	def removeContour(self, index):
		"""remove  a specific contour from the glyph"""
		del self.contours[index]
		self._hasChanged()
		
	def removeAnchor(self, anchor):
		"""remove  a specific anchor from the glyph"""
		del self.anchors[anchor.index]
		self._hasChanged()
	
	def removeComponent(self, component):
		"""remove  a specific component from the glyph"""
		del self.components[component.index]
		self._hasChanged()
			
	def center(self, padding=None):
		"""Equalise sidebearings, set to padding if wanted."""
		left = self.leftMargin
		right = self.rightMargin
		if padding:
			e_left = e_right = padding
		else:
			e_left = (left + right)/2
			e_right = (left + right) - e_left
		self.leftMargin = e_left
		self.rightMargin = e_right
	
	def decompose(self):
		"""Decompose all components"""
		for i in range(len(self.components)):
			self.components[-1].decompose()
		self._hasChanged()
			
	def clear(self, contours=True, components=True, anchors=True, guides=True):
		"""Clear all items marked as True from the glyph"""
		if contours:
			self.clearContours()
		if components:
			self.clearComponents()
		if anchors:
			self.clearAnchors()
		if guides:
			self.clearHGuides()
			self.clearVGuides()
	
	def clearContours(self):
		"""clear all contours"""
		self.contours = []
		self._hasChanged()
	
	def clearComponents(self):
		"""clear all components"""
		self.components = []
		self._hasChanged()
		
	def clearAnchors(self):
		"""clear all anchors"""
		self.anchors = []
		self._hasChanged()
		
	def clearHGuides(self):
		"""clear all horizontal guides"""
		self.hGuides = []
		self._hasChanged()
	
	def clearVGuides(self):
		"""clear all vertical guides"""
		self.vGuides = []
		self._hasChanged()
		
	def getAnchors(self):
		return self.anchors
	
	def getComponents(self):
		return self.components
	
	#
	# stuff related to Glyph Properties
	#
	


class RContour(BaseContour):
	
	_title = "RoboFabContour"
	
	def __init__(self, object=None):
		#BaseContour.__init__(self)
		self.segments = []
		self.selected = False
		
	def __len__(self):
		return len(self.segments) 

	def __getitem__(self, index):
		if index < len(self.segments):
			return self.segments[index]
		raise IndexError
		
	def _get_index(self):
		return self.getParent().contours.index(self)
		
	def _set_index(self, index):
		ogIndex = self.index
		if index != ogIndex:
			contourList = self.getParent().contours
			contourList.insert(index, contourList.pop(ogIndex))
			
	
	index = property(_get_index, _set_index, doc="index of the contour")
	
	def _get_points(self):
		points = []
		for segment in self.segments:
			for point in segment.points:
				points.append(point)
		return points
	
	points = property(_get_points, doc="view the contour as a list of points")
	
	def _get_bPoints(self):
		bPoints = []
		for segment in self.segments:
			segType = segment.type
			if segType == MOVE:
				bType = CORNER
			elif segType == LINE:
				bType = CORNER
			elif segType == CURVE:
				if segment.smooth:
					bType = CURVE
				else:
					bType = CORNER
			else:
				raise RoboFabError, "encountered unknown segment type"
			b = RBPoint()
			b.setParent(segment)
			bPoints.append(b)
		return bPoints

	bPoints = property(_get_bPoints, doc="view the contour as a list of bPoints")
	
	def appendSegment(self, segmentType, points, smooth=False):
		"""append a segment to the contour"""
		segment = self.insertSegment(index=len(self.segments), segmentType=segmentType, points=points, smooth=smooth)
		return segment
		
	def insertSegment(self, index, segmentType, points, smooth=False):
		"""insert a segment into the contour"""
		segment = RSegment(segmentType, points, smooth)
		segment.setParent(self)
		self.segments.insert(index, segment)
		self._hasChanged()
		return segment
		
	def removeSegment(self, index):
		"""remove a segment from the contour"""
		del self.segments[index]
		self._hasChanged()
				
	def reverseContour(self):
		"""reverse the contour"""
		from robofab.pens.reverseContourPointPen import ReverseContourPointPen
		index = self.index
		glyph = self.getParent()
		pen = glyph.getPointPen()
		reversePen = ReverseContourPointPen(pen)
		self.drawPoints(reversePen)
		# we've drawn the reversed contour onto our parent glyph,
		# so it sits at the end of the contours list:
		newContour = glyph.contours.pop(-1)
		for segment in newContour.segments:
			segment.setParent(self)
		self.segments = newContour.segments
		self._hasChanged()
	
	def setStartSegment(self, segmentIndex):
		"""set the first segment on the contour"""
		# this obviously does not support open contours
		if len(self.segments) < 2:
			return
		if segmentIndex == 0:
			return
		if segmentIndex > len(self.segments)-1:
			raise IndexError, 'segment index not in segments list'
		oldStart = self.segments[0]
		oldLast = self.segments[-1]
		 #check to see if the contour ended with a curve on top of the move
		 #if we find one delete it,
		if oldLast.type == CURVE or oldLast.type == QCURVE:
			startOn = oldStart.onCurve
			lastOn = oldLast.onCurve
			if startOn.x == lastOn.x and startOn.y == lastOn.y:
				del self.segments[0]
				# since we deleted the first contour, the segmentIndex needs to shift
				segmentIndex = segmentIndex - 1
		# if we DO have a move left over, we need to convert it to a line
		if self.segments[0].type == MOVE:
			self.segments[0].type = LINE
		# slice up the segments and reassign them to the contour
		segments = self.segments[segmentIndex:]
		self.segments = segments + self.segments[:segmentIndex]
		# now, draw the contour onto the parent glyph
		glyph = self.getParent()
		pen = glyph.getPointPen()
		self.drawPoints(pen)
		# we've drawn the new contour onto our parent glyph,
		# so it sits at the end of the contours list:
		newContour = glyph.contours.pop(-1)
		for segment in newContour.segments:
			segment.setParent(self)
		self.segments = newContour.segments
		self._hasChanged()


class RSegment(BaseSegment):
	
	_title = "RoboFabSegment"
	
	def __init__(self, segmentType=None, points=[], smooth=False):
		BaseSegment.__init__(self)
		self.selected = False
		self.points = []
		self.smooth = smooth
		if points:
			#the points in the segment should be RPoints, so create those objects
			for point in points[:-1]:
				x, y = point
				p = RPoint(x, y, pointType=OFFCURVE)
				p.setParent(self)
				self.points.append(p)
			aX, aY = points[-1]
			p = RPoint(aX, aY, segmentType)
			p.setParent(self)
			self.points.append(p)
		
	def _get_type(self):
		return self.points[-1].type
	
	def _set_type(self, pointType):
		onCurve = self.points[-1]
		ocType = onCurve.type
		if ocType == pointType:
			return
		#we are converting a cubic line into a cubic curve
		if pointType == CURVE and  ocType == LINE:
			onCurve.type = pointType
			parent = self.getParent()
			prev = parent._prevSegment(self.index)
			p1 = RPoint(prev.onCurve.x, prev.onCurve.y, pointType=OFFCURVE)
			p1.setParent(self)
			p2 = RPoint(onCurve.x, onCurve.y, pointType=OFFCURVE)
			p2.setParent(self)
			self.points.insert(0, p2)
			self.points.insert(0, p1)
		#we are converting a cubic move to a curve
		elif pointType == CURVE and ocType == MOVE:
			onCurve.type = pointType
			parent = self.getParent()
			prev = parent._prevSegment(self.index)
			p1 = RPoint(prev.onCurve.x, prev.onCurve.y, pointType=OFFCURVE)
			p1.setParent(self)
			p2 = RPoint(onCurve.x, onCurve.y, pointType=OFFCURVE)
			p2.setParent(self)
			self.points.insert(0, p2)
			self.points.insert(0, p1)
		#we are converting a quad curve to a cubic curve
		elif pointType == CURVE and ocType == QCURVE:
			onCurve.type == CURVE
		#we are converting a cubic curve into a cubic line
		elif pointType == LINE and ocType == CURVE:
			p = self.points.pop(-1)
			self.points = [p]
			onCurve.type = pointType
			self.smooth = False
		#we are converting a cubic move to a line
		elif pointType == LINE and ocType == MOVE:
			onCurve.type = pointType
		#we are converting a quad curve to a line:
		elif pointType == LINE and ocType == QCURVE:
			p = self.points.pop(-1)
			self.points = [p]
			onCurve.type = pointType
			self.smooth = False	
		# we are converting to a quad curve where just about anything is legal
		elif pointType == QCURVE:
			onCurve.type = pointType
		else:
			raise RoboFabError, 'unknown segment type'
			
	type = property(_get_type, _set_type, doc="type of the segment")
	
	def _get_index(self):
		return self.getParent().segments.index(self)
		
	index = property(_get_index, doc="index of the segment")
	
	def insertPoint(self, index, pointType, point):
		x, y = point
		p = RPoint(x, y, pointType=pointType)
		p.setParent(self)
		self.points.insert(index, p)
		self._hasChanged()
	
	def removePoint(self, index):
		del self.points[index]
		self._hasChanged()
		

class RBPoint(BaseBPoint):
	
	_title = "RoboFabBPoint"
		
	def _setAnchorChanged(self, value):
		self._anchorPoint.setChanged(value)
	
	def _setNextChanged(self, value):
		self._nextOnCurve.setChanged(value)	
		
	def _get__parentSegment(self):
		return self.getParent()
		
	_parentSegment = property(_get__parentSegment, doc="")
	
	def _get__nextOnCurve(self):
		pSeg = self._parentSegment
		contour = pSeg.getParent()
		#could this potentially return an incorrect index? say, if two segments are exactly the same?
		return contour.segments[(contour.segments.index(pSeg) + 1) % len(contour.segments)]
	
	_nextOnCurve = property(_get__nextOnCurve, doc="")
	
	def _get_index(self):
		return self._parentSegment.index
	
	index = property(_get_index, doc="index of the bPoint on the contour")


class RPoint(BasePoint):
	
	_title = "RoboFabPoint"
	
	def __init__(self, x=0, y=0, pointType=None, name=None):
		self.selected = False
		self._type = pointType
		self._x = x
		self._y = y
		self._name = name
		
	def _get_x(self):
		return self._x
		
	def _set_x(self, value):
		self._x = value
		self._hasChanged()
	
	x = property(_get_x, _set_x, doc="")

	def _get_y(self):
		return self._y
	
	def _set_y(self, value):
		self._y = value
		self._hasChanged()

	y = property(_get_y, _set_y, doc="")
	
	def _get_type(self):
		return self._type
	
	def _set_type(self, value):
		self._type = value
		self._hasChanged()

	type = property(_get_type, _set_type, doc="")
	
	def _get_name(self):
		return self._name
	
	def _set_name(self, value):
		self._name = value
		self._hasChanged()

	name = property(_get_name, _set_name, doc="")

		
class RAnchor(BaseAnchor):
	
	_title = "RoboFabAnchor"
	
	def __init__(self, name=None, position=None, mark=None):
		BaseAnchor.__init__(self)
		self.selected = False
		self.name = name
		if position is None:
			self.x = self.y = None
		else:
			self.x, self.y = position
		self.mark = mark
		
	def _get_index(self):
		if self.getParent() is None: return None
		return self.getParent().anchors.index(self)
	
	index = property(_get_index, doc="index of the anchor")
	
	def _get_position(self):
		return (self.x, self.y)
	
	def _set_position(self, value):
		self.x = value[0]
		self.y = value[1]
		self._hasChanged()
	
	position = property(_get_position, _set_position, doc="position of the anchor")
	
	def move(self, pt):
		"""Move the anchor"""
		self.x = self.x + pt[0]
		self.y = self.y + pt[0]
		self._hasChanged()

		
class RComponent(BaseComponent):
	
	_title = "RoboFabComponent"
	
	def __init__(self, baseGlyphName=None, offset=(0,0), scale=(1,1), transform=None):
		BaseComponent.__init__(self)
		self.selected = False
		self._baseGlyph = baseGlyphName
		self._offset = offset
		self._scale = scale
		if transform is None:
			xx, yy = scale
			dx, dy = offset
			self.transformation = (xx, 0, 0, yy, dx, dy)
		else:
			self.transformation = transform
		
	def _get_index(self):
		if self.getParent() is None: return None
		return self.getParent().components.index(self)
		
	index = property(_get_index, doc="index of the component")
	
	def _get_baseGlyph(self):
		return self._baseGlyph
		
	def _set_baseGlyph(self, glyphName):
		# XXXX needs to be implemented in objectsFL for symmetricity's sake. Eventually.
		self._baseGlyph = glyphName
		self._hasChanged()
		
	baseGlyph = property(_get_baseGlyph, _set_baseGlyph, doc="")

	def _get_offset(self):
		""" Get the offset component of the transformation.="""
		(xx, xy, yx, yy, dx, dy) = self._transformation
		return dx, dy
	
	def _set_offset(self, value):
		""" Set the offset component of the transformation."""
		(xx, xy, yx, yy, dx, dy) = self._transformation
		self._transformation = (xx, xy, yx, yy, value[0], value[1])
		self._hasChanged()
		
	offset = property(_get_offset, _set_offset, doc="the offset of the component")

	def _get_scale(self):
		""" Return the scale components of the transformation."""
		(xx, xy, yx, yy, dx, dy) = self._transformation
		return xx, yy
	
	def _set_scale(self, scale):
		""" Set the scale component of the transformation.
			Note: setting this value effectively makes the xy and yx values meaningless.
			We're assuming that if you're setting the xy and yx values, you will use
			the transformation attribute rather than the scale and offset attributes.
		"""
		xScale, yScale = scale
		(xx, xy, yx, yy, dx, dy) = self._transformation
		self._transformation = (xScale, xy, yx, yScale, dx, dy)
		self._hasChanged()
		
	scale = property(_get_scale, _set_scale, doc="the scale of the component")
	
	def _get_transformation(self):
		return self._transformation
	
	def _set_transformation(self, transformation):
		assert len(transformation)==6, "Transformation matrix must have 6 values"
		self._transformation = transformation
	
	transformation = property(_get_transformation, _set_transformation, doc="the transformation matrix of the component")
		
	def move(self, pt):
		"""Move the component"""
		(xx, xy, yx, yy, dx, dy) = self._transformation
		self._transformation = (xx, xy, yx, yy, dx+pt[0], dy+pt[1])
		self._hasChanged()
	
	def decompose(self):
		"""Decompose the component"""
		baseGlyphName = self.baseGlyph
		parentGlyph = self.getParent()
		# if there is no parent glyph, there is nothing to decompose to
		if baseGlyphName is not None and parentGlyph is not None:
			parentFont = parentGlyph.getParent()
			# we must have a parent glyph with the baseGlyph
			# if not, we will simply remove the component from
			# the parent glyph thereby decomposing the component
			# to nothing.
			if parentFont is not None and parentFont.has_key(baseGlyphName):
				from robofab.pens.adapterPens import TransformPointPen
				baseGlyph = parentFont[baseGlyphName]
				for contour in baseGlyph.contours:
					pointPen = parentGlyph.getPointPen()
					transPen = TransformPointPen(pointPen, self._transformation)
					contour.drawPoints(transPen)
			parentGlyph.components.remove(self)
	
		
class RKerning(BaseKerning):
	
	_title = "RoboFabKerning"

		
class RGroups(BaseGroups):
	
	_title = "RoboFabGroups"
	
class RLib(BaseLib):
	
	_title = "RoboFabLib"

		
class RInfo(BaseInfo):
	
	_title = "RoboFabFontInfo"

class RFeatures(BaseFeatures):

	_title = "RoboFabFeatures"

