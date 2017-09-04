"""A simple set of tools for building accented glyphs.
# Hey look! A demonstration:
from robofab.accentBuilder import AccentTools, buildRelatedAccentList
font = CurrentFont
# a list of accented glyphs that you want to build
myList=['Aacute', 'aacute']
# search for glyphs related to glyphs in myList and add them to myList
myList=buildRelatedAccentList(font, myList)+myList
# start the class
at=AccentTools(font, myList)
# clear away any anchors that exist (this is optional)
at.clearAnchors()
# add necessary anchors if you want to
at.buildAnchors(ucXOffset=20, ucYOffset=40, lcXOffset=15, lcYOffset=30)
# print a report of any errors that occured
at.printAnchorErrors()
# build the accented glyphs if you want to
at.buildAccents()
# print a report of any errors that occured
at.printAccentErrors()
"""
#XXX! This is *very* experimental! I think it works, but you never know.

from robofab.gString import lowercase_plain, accents, uppercase_plain, splitAccent, findAccentBase
from robofab.tools.toolsAll import readGlyphConstructions
import robofab
from robofab.interface.all.dialogs import ProgressBar
from robofab.world import RFWorld
inFontLab = RFWorld().inFontLab

anchorColor=125
accentColor=75

def stripSuffix(glyphName):
	"""strip away unnecessary suffixes from a glyph name"""
	if glyphName.find('.') != -1:
		baseName = glyphName.split('.')[0]
		if glyphName.find('.sc') != -1:
			baseName = '.'.join([baseName, 'sc'])
		return baseName
	else:
		return glyphName
		
def buildRelatedAccentList(font, list):
	"""build a list of related glyphs suitable for use with AccentTools"""
	searchList = []
	baseGlyphs = {}
	foundList = []
	for glyphName in list:
		splitNames = splitAccent(glyphName)
		baseName = splitNames[0]
		accentNames = splitNames[1]
		if baseName not in searchList:
			searchList.append(baseName)
		if baseName not in baseGlyphs.keys():
			baseGlyphs[baseName] = [accentNames]
		else:
			baseGlyphs[baseName].append(accentNames)
	foundGlyphs = findRelatedGlyphs(font, searchList, doAccents=0)
	for baseGlyph in foundGlyphs.keys():
		for foundGlyph in foundGlyphs[baseGlyph]:
			for accentNames in baseGlyphs[baseGlyph]:
				foundList.append(makeAccentName(foundGlyph, accentNames))
	return foundList
	
def findRelatedGlyphs(font, searchItem, doAccents=True):
	"""Gather up a bunch of related glyph names. Send it either a
	single glyph name 'a', or a list of glyph names ['a', 'x'] and it
	returns a dict like: {'a': ['atilde', 'a.alt', 'a.swash']}. if doAccents
	is False it will skip accented glyph names.
	This is a relatively slow operation!"""
	relatedGlyphs = {}
	for name in font.keys():
		base = name.split('.')[0]
		if name not in relatedGlyphs.keys():
			relatedGlyphs[name] = []
		if base not in relatedGlyphs.keys():
			relatedGlyphs[base] = []
		if doAccents:
			accentBase = findAccentBase(name)
			if accentBase not in relatedGlyphs.keys():
				relatedGlyphs[accentBase] = []
			baseAccentBase = findAccentBase(base)
			if baseAccentBase not in relatedGlyphs.keys():
				relatedGlyphs[baseAccentBase] = []
		if base != name and name not in relatedGlyphs[base]:
			relatedGlyphs[base].append(name)
		if doAccents:
			if accentBase != name and name not in relatedGlyphs[accentBase]:
				relatedGlyphs[accentBase].append(name)
			if baseAccentBase != name and name not in relatedGlyphs[baseAccentBase]:
				relatedGlyphs[baseAccentBase].append(name)
	foundGlyphs = {}
	if isinstance(searchItem, str):
		searchList = [searchItem]
	else:
		searchList = searchItem
	for glyph in searchList:
		foundGlyphs[glyph] = relatedGlyphs[glyph]
	return foundGlyphs

def makeAccentName(baseName, accentNames):
	"""make an accented glyph name"""
	if isinstance(accentNames, str):
		accentNames = [accentNames]
	build = []
	if baseName.find('.') != -1:
		base = baseName.split('.')[0]
		suffix = baseName.split('.')[1]
	else:
		base = baseName
		suffix = ''
	build.append(base)
	for accent in accentNames:
		build.append(accent)
	buildJoin = ''.join(build)
	name = '.'.join([buildJoin, suffix])
	return name
	
def nameBuster(glyphName, glyphConstruct):
		stripedSuffixName = stripSuffix(glyphName)
		suffix = None
		errors = []
		accentNames = []
		baseName = glyphName
		if glyphName.find('.') != -1:
			suffix = glyphName.split('.')[1]
		if glyphName.find('.sc') != -1:
			suffix = glyphName.split('.sc')[1]
		if stripedSuffixName not in glyphConstruct.keys():
			errors.append('%s: %s not in glyph construction database'%(glyphName, stripedSuffixName))
		else:
			if suffix is None:
				baseName = glyphConstruct[stripedSuffixName][0]
			else:
				if glyphName.find('.sc') != -1:
					baseName = ''.join([glyphConstruct[stripedSuffixName][0], suffix])
				else:
					baseName = '.'.join([glyphConstruct[stripedSuffixName][0], suffix])
			accentNames = glyphConstruct[stripedSuffixName][1:]
		return (baseName, stripedSuffixName, accentNames, errors)
	
class AccentTools:
	def __init__(self, font, accentList):
		"""several tools for working with anchors and building accents"""
		self.glyphConstructions = readGlyphConstructions()
		self.accentList = accentList
		self.anchorErrors = ['ANCHOR ERRORS:']
		self.accentErrors = ['ACCENT ERRORS:']
		self.font = font
		
	def clearAnchors(self, doProgress=True):
		"""clear all anchors in the font"""
		tickCount = len(self.font)
		if doProgress:
			bar = ProgressBar("Cleaning all anchors...", tickCount)
		tick = 0	
		for glyphName in self.accentList:
			if doProgress:
				bar.label(glyphName)
			baseName, stripedSuffixName, accentNames, errors = nameBuster(glyphName, self.glyphConstructions)
			existError = False
			if len(errors) > 0:
				existError = True
			if not existError:
				toClear = [baseName]
				for accent, position in accentNames:
					toClear.append(accent)
				for glyphName in toClear:
					try:
						self.font[glyphName].clearAnchors()
					except IndexError: pass
			if doProgress:
				bar.tick(tick)
			tick = tick+1
		if doProgress:
			bar.close()

	def buildAnchors(self, ucXOffset=0, ucYOffset=0, lcXOffset=0, lcYOffset=0, markGlyph=True, doProgress=True):
		"""add the necessary anchors to the glyphs if they don't exist
		some flag definitions:
		uc/lc/X/YOffset=20 offset values for the anchors
		markGlyph=1 mark the glyph that is created
		doProgress=1 show a progress bar"""
		accentOffset = 10
		tickCount = len(self.accentList)
		if doProgress:
			bar = ProgressBar('Adding anchors...', tickCount)
		tick = 0
		for glyphName in self.accentList:
			if doProgress:
				bar.label(glyphName)
			previousPositions = {}
			baseName, stripedSuffixName, accentNames, errors = nameBuster(glyphName, self.glyphConstructions)
			existError = False
			if len(errors) > 0:
				existError = True
				for anchorError in errors:
					self.anchorErrors.append(anchorError)
			if not existError:
				existError = False
				try:
					self.font[baseName]
				except IndexError:
					self.anchorErrors.append(' '.join([glyphName, ':', baseName, 'does not exist.']))
					existError = True
				for accentName, accentPosition in accentNames:
						try:
							self.font[accentName]
						except IndexError:
							self.anchorErrors.append(' '.join([glyphName, ':', accentName, 'does not exist.']))
							existError = True
				if not existError:
					#glyph = self.font.newGlyph(glyphName, clear=True)
					for accentName, accentPosition in accentNames:
						if baseName.split('.')[0] in lowercase_plain:
							xOffset = lcXOffset-accentOffset
							yOffset = lcYOffset-accentOffset
						else:
							xOffset = ucXOffset-accentOffset
							yOffset = ucYOffset-accentOffset
						# should I add a cedilla and ogonek yoffset override here?
						if accentPosition not in previousPositions.keys():
							self._dropAnchor(self.font[baseName], accentPosition, xOffset, yOffset)
							if markGlyph:
								self.font[baseName].mark = anchorColor
								if inFontLab:
									self.font[baseName].update()
						else:
							self._dropAnchor(self.font[previousPositions[accentPosition]], accentPosition, xOffset, yOffset)
						self._dropAnchor(self.font[accentName], accentPosition, accentOffset, accentOffset, doAccentPosition=1)
						previousPositions[accentPosition] = accentName
						if markGlyph:
							self.font[accentName].mark = anchorColor
							if inFontLab:
								self.font[accentName].update()
			if inFontLab:
				self.font.update()
			if doProgress:
				bar.tick(tick)
			tick = tick+1
		if doProgress:
			bar.close()	
						
	def printAnchorErrors(self):
		"""print errors encounted during buildAnchors"""
		if len(self.anchorErrors) == 1:
			print 'No anchor errors encountered'
		else:
			for i in self.anchorErrors:
				print i
												
	def _dropAnchor(self, glyph, positionName, xOffset=0, yOffset=0, doAccentPosition=False):
		"""anchor adding method. for internal use only."""
		existingAnchorNames = []
		for anchor in glyph.getAnchors():
			existingAnchorNames.append(anchor.name)
		if doAccentPosition:
			positionName = ''.join(['_', positionName])
		if positionName not in existingAnchorNames:	
			glyphLeft, glyphBottom, glyphRight, glyphTop = glyph.box
			glyphXCenter = glyph.width/2
			if positionName == 'top':
				glyph.appendAnchor(positionName, (glyphXCenter, glyphTop+yOffset))
			elif positionName == 'bottom':
				glyph.appendAnchor(positionName, (glyphXCenter, glyphBottom-yOffset))
			elif positionName == 'left':
				glyph.appendAnchor(positionName, (glyphLeft-xOffset, glyphTop))
			elif positionName == 'right':
				glyph.appendAnchor(positionName, (glyphRight+xOffset, glyphTop))
			elif positionName == '_top':
				glyph.appendAnchor(positionName, (glyphXCenter, glyphBottom-yOffset))
			elif positionName == '_bottom':
				glyph.appendAnchor(positionName, (glyphXCenter, glyphTop+yOffset))
			elif positionName == '_left':
				glyph.appendAnchor(positionName, (glyphRight+xOffset, glyphTop))
			elif positionName == '_right':
				glyph.appendAnchor(positionName, (glyphLeft-xOffset, glyphTop))
			if inFontLab:
				glyph.update()

	def buildAccents(self, clear=True, adjustWidths=True, markGlyph=True, doProgress=True):
		"""build accented glyphs. some flag definitions:
		clear=1 clear the glyphs if they already exist
		markGlyph=1 mark the glyph that is created
		doProgress=1 show a progress bar
		adjustWidths=1 will fix right and left margins when left or right accents are added"""
		tickCount = len(self.accentList)
		if doProgress:
			bar = ProgressBar('Building accented glyphs...', tickCount)
		tick = 0
		for glyphName in self.accentList:
			if doProgress:
				bar.label(glyphName)
			existError = False
			anchorError = False
	
			baseName, stripedSuffixName, accentNames, errors = nameBuster(glyphName, self.glyphConstructions)
			if len(errors) > 0:
				existError = True
				for accentError in errors:
					self.accentErrors.append(accentError)
			
			if not existError:
				baseAnchors = []
				try:
					self.font[baseName]
				except IndexError:
					self.accentErrors.append('%s: %s does not exist.'%(glyphName, baseName))
					existError = True
				else:
					for anchor in self.font[baseName].anchors:
						baseAnchors.append(anchor.name)
				for accentName, accentPosition in accentNames:
					accentAnchors = []
					try:
						self.font[accentName]
					except IndexError:
						self.accentErrors.append('%s: %s does not exist.'%(glyphName, accentName))
						existError = True
					else:
						for anchor in self.font[accentName].getAnchors():
							accentAnchors.append(anchor.name)
						if accentPosition not in baseAnchors:
							self.accentErrors.append('%s: %s not in %s anchors.'%(glyphName, accentPosition, baseName))
							anchorError = True
						if ''.join(['_', accentPosition]) not in accentAnchors:
							self.accentErrors.append('%s: %s not in %s anchors.'%(glyphName, ''.join(['_', accentPosition]), accentName))
							anchorError = True
				if not existError and not anchorError:
					destination = self.font.compileGlyph(glyphName, baseName, self.glyphConstructions[stripedSuffixName][1:], adjustWidths)
					if markGlyph:
						destination.mark = accentColor
			if doProgress:
				bar.tick(tick)
			tick = tick+1
		if doProgress:
			bar.close()
			
	def printAccentErrors(self):
		"""print errors encounted during buildAccents"""
		if len(self.accentErrors) == 1:
			print 'No accent errors encountered'
		else:
			for i in self.accentErrors:
				print i
	

