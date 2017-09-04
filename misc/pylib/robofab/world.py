import os, sys
from robofab import RoboFabError, version, numberVersion


class RFWorld:

	"""All parameters about platforms, versions and environments included in one object."""

	def __init__(self):
		self.mac = None
		self.pc = None
		self.platform = sys.platform
		self.applicationName = None # name of the application we're running in
		self.name = os.name
		self.version = version	# the robofab version
		self.numberVersion = numberVersion
		self.run = True

		# get some platform information
		if self.name == 'mac' or self.name == 'posix':
			if self.platform == "darwin":
				self.mac = "X"
			else:
				self.mac = "pre-X"
		elif self.name == 'nt':
			# if you know more about PC & win stuff, add it here!
			self.pc = True
		else:
			raise RoboFabError, "We're running on an unknown platform."

		# collect versions
		self.pyVersion = sys.version[:3]
		self.inPython = False 
		self.inFontLab = False
		self.flVersion = None
		self.inGlyphs = False
		self.glyphsVersion = None
		self.inRoboFont = False
		self.roboFontVersion = None

		# are we in Glyphs?
		try:
			import objectsGS
			from AppKit import NSBundle
			bundle = NSBundle.mainBundle()
			self.applicationName = bundle.infoDictionary()["CFBundleName"]
			self.inGlyphs = True
			self.glyphsVersion = bundle.infoDictionary()["CFBundleVersion"]
		except ImportError:
			# are we in RoboFont
			try:
				import mojo
				from AppKit import NSBundle
				bundle = NSBundle.mainBundle()
				self.applicationName = bundle.infoDictionary()["CFBundleName"]
				self.inRoboFont = True
				self.roboFontVersion = bundle.infoDictionary()["CFBundleVersion"]
			except ImportError:
				# are we in FontLab?
				try:
					from FL import fl
					self.applicationName = fl.filename
					self.inFontLab = True
					self.flVersion = fl.version
				except ImportError: pass
		# we are in NoneLab
		if not self.inFontLab:
			self.inPython = True

		# see if we have DialogKit
		self.supportsDialogKit = False

	def __repr__(self):
		s = [
			"Robofab is running on %s" % self.platform,
			"Python version: %s" % self.pyVersion,
			"Mac stuff: %s" % self.mac,
			"PC stuff: %s" % self.pc,
			"FontLab stuff: %s" % self.inFontLab,
			"FLversion: %s" % self.flVersion,
			"Glyphs stuff: %s" % self.inGlyphs,
			"Glyphs version: %s" % self.glyphsVersion,
			"RoboFont stuff: %s" %self.inRoboFont,
			"RoboFont version: %s" %self.roboFontVersion,
		]
		return ", ".join(s)


world = RFWorld()

lineBreak = os.linesep

if world.inFontLab:
	from robofab.interface.all.dialogs import SelectFont, SelectGlyph
	from robofab.objects.objectsFL import CurrentFont, CurrentGlyph, RFont, RGlyph, OpenFont, NewFont, AllFonts
	lineBreak = "\n"
elif world.inRoboFont:
	from mojo.roboFont import CurrentFont, CurrentGlyph, RFont, RGlyph, OpenFont, NewFont, AllFonts
elif world.inGlyphs:
	from objectsGS import CurrentFont, CurrentGlyph, RFont, RGlyph, OpenFont, NewFont, AllFonts
elif world.inPython:
	from robofab.objects.objectsRF import CurrentFont, CurrentGlyph, RFont, RGlyph, OpenFont, NewFont, AllFonts

    

if __name__ == "__main__":
	f = RFWorld()
	print f
