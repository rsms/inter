"""Tool for exporting GLIFs from FontLab"""

import FL
import os
from robofab.interface.all.dialogs import ProgressBar
from robofab.glifLib import GlyphSet
from robofab.tools.glifImport import GlyphPlaceholder
from robofab.pens.flPen import drawFLGlyphOntoPointPen


def exportGlyph(glyphName, flGlyph, glyphSet):
	"""Export a FontLab glyph."""

	glyph = GlyphPlaceholder()
	glyph.width = flGlyph.width
	glyph.unicodes = flGlyph.unicodes
	if flGlyph.note:
		glyph.note = flGlyph.note
	customdata = flGlyph.customdata
	if customdata:
		from cStringIO import StringIO
		from robofab.plistlib import readPlist, Data
		f = StringIO(customdata)
		try:
			glyph.lib = readPlist(f)
		except: # XXX ugh, plistlib can raise lots of things
			# Anyway, customdata does not contain valid plist data,
			# but we don't need to toss it!
			glyph.lib = {"org.robofab.fontlab.customdata": Data(customdata)}

	def drawPoints(pen):
		# whoohoo, nested scopes are cool.
		drawFLGlyphOntoPointPen(flGlyph, pen)

	glyphSet.writeGlyph(glyphName, glyph, drawPoints)


def exportGlyphs(font, glyphs=None, dest=None, doProgress=True, bar=None):
	"""Export all glyphs in a FontLab font"""
	if dest is None:
		dir, base = os.path.split(font.file_name)
		base = base.split(".")[0] + ".glyphs"
		dest = os.path.join(dir, base)
	
	if not os.path.exists(dest):
		os.makedirs(dest)

	glyphSet = GlyphSet(dest)
	
	if glyphs is None:
		indices = range(len(font))
	else:
		indices = []
		for glyphName in glyphs:
			indices.append(font.FindGlyph(glyphName))
	barStart = 0
	closeBar = False
	if doProgress:
		if not bar:
			bar = ProgressBar("Exporting Glyphs", len(indices))
			closeBar = True
		else:
			barStart = bar.getCurrentTick()
	else:
		bar = None
	try:
		done = {}
		for i in range(len(indices)):
			#if not (i % 10) and not bar.tick(i + barStart):
			#	raise KeyboardInterrupt
			index = indices[i]
			flGlyph = font[index]
			if flGlyph is None:
				continue
			glyphName = flGlyph.name
			if not glyphName:
				print "can't dump glyph #%s, it has no glyph name" % i
			else:
				if glyphName in done:
					n = 1
					while ("%s#%s" % (glyphName, n)) in done:
						n += 1
					glyphName = "%s#%s" % (glyphName, n)
				done[glyphName] = None
				exportGlyph(glyphName, flGlyph, glyphSet)
			if bar and not i % 10:
				bar.tick(barStart + i)
		# Write out contents.plist
		glyphSet.writeContents()
	except KeyboardInterrupt:
		if bar:
			bar.close()
			bar = None
	if bar and closeBar:
		bar.close()
