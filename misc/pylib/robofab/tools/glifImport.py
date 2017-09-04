"""Tools for importing GLIFs into FontLab"""

import os
from FL import fl
from robofab.tools.toolsFL import NewGlyph, FontIndex
from robofab.pens.flPen import FLPointPen
from robofab.glifLib import GlyphSet
from robofab.interface.all.dialogs import ProgressBar, GetFolder


class GlyphPlaceholder:
	pass


def importAllGlifFiles(font, dirName=None, doProgress=True, bar=None):
	"""import all GLIFs into a FontLab font"""
	if dirName is None:
		if font.file_name:
			dir, base = os.path.split(font.file_name)
			base = base.split(".")[0] + ".glyphs"
			dirName = os.path.join(dir, base)
		else:
			dirName = GetFolder("Please select a folder with .glif files")
	glyphSet = GlyphSet(dirName)
	glyphNames = glyphSet.keys()
	glyphNames.sort()
	barStart = 0
	closeBar = False
	if doProgress:
		if not bar:
			bar = ProgressBar("Importing Glyphs", len(glyphNames))
			closeBar = True
		else:
			barStart = bar.getCurrentTick()
	else:
		bar = None
	try:
		for i in range(len(glyphNames)):
			#if not (i % 10) and not bar.tick(barStart + i):
			#	raise KeyboardInterrupt
			glyphName = glyphNames[i]
			flGlyph = NewGlyph(font, glyphName, clear=True)
			pen = FLPointPen(flGlyph)
			glyph = GlyphPlaceholder()
			glyphSet.readGlyph(glyphName, glyph, pen)
			if hasattr(glyph, "width"):
				flGlyph.width = int(round(glyph.width))
			if hasattr(glyph, "unicodes"):
				flGlyph.unicodes = glyph.unicodes
			if hasattr(glyph, "note"):
				flGlyph.note = glyph.note  # XXX must encode
			if hasattr(glyph, "lib"):
				from cStringIO import StringIO
				from robofab.plistlib import writePlist
				lib = glyph.lib
				if lib:
					if len(lib) == 1 and "org.robofab.fontlab.customdata" in lib:
						data = lib["org.robofab.fontlab.customdata"].data
					else:
						f = StringIO()
						writePlist(glyph.lib, f)
						data = f.getvalue()
					flGlyph.customdata = data
			# XXX the next bit is only correct when font is the current font :-(
			fl.UpdateGlyph(font.FindGlyph(glyphName))
			if bar and not i % 10:
				bar.tick(barStart + i)
	except KeyboardInterrupt:
		if bar:
			bar.close()
			bar = None
	fl.UpdateFont(FontIndex(font))
	if bar and closeBar:
		bar.close()
