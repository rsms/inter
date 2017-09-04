"""This is the place for stuff that makes proofs and test text settings etc"""

import string




idHeader = """<ASCII-MAC>
<Version:2.000000><FeatureSet:InDesign-Roman><ColorTable:=<Black:COLOR:CMYK:Process:0.000000,0.000000,0.000000,1.000000>>"""

idColor = """<cColor:COLOR\:%(model)s\:Process\:%(c)f\,%(m)f\,%(y)f\,%(k)f>"""

idParaStyle = """<ParaStyle:><cTypeface:%(weight)s><cSize:%(size)f><cLeading:%(leading)f><cFont:%(family)s>"""
idGlyphStyle = """<cTypeface:%(weight)s><cSize:%(size)f><cLeading:%(leading)f><cFont:%(family)s>"""

seperator = ''

autoLinespaceFactor = 1.2


class IDTaggedText:

	"""Export a text as a XML tagged text file for InDesign (2.0?).
	The tags can contain information about
		- family: font family i.e. "Times"
		- weight: font weight "Bold"
		- size: typesize in points
		- leading: leading in points
		- color:  a CMYK color, as a 4 tuple of floats between 0 and 1
		- insert special glyphs based on glyphindex
			(which is why it only makes sense if you use this in FontLab,
			otherwise there is no other way to get the indices)
	"""

	def __init__(self, family, weight, size=36, leading=None):
		self.family = family
		self.weight = weight
		self.size = size
		if not leading:
			self.leading = autoLinespaceFactor*size
		self.text = []
		self.data = []
		self.addHeader()
	
	def add(self, text):
		"""Method to add text to the file."""
		t = self.charToGlyph(text)
		self.data.append(t)
	
	def charToGlyph(self, text):
		return text
	
	def addHeader(self):
		"""Add the standard header."""
		# set colors too?
		self.data.append(idHeader)
	
	def replace(self, old, new):
		"""Replace occurances of 'old' with 'new' in all content."""
		d = []
		for i in self.data:
			d.append(i.replace(old, new))
		self.data = d
		
	def save(self, path):
		"""Save the tagged text here."""
		f = open(path, 'w')
		f.write(string.join(self.data, seperator))
		f.close()
	
	def addGlyph(self, index):
		"""Add a special glyph, index is the glyphIndex in an OpenType font."""
		self.addStyle()
		self.data.append("<cSpecialGlyph:%d><0xFFFD>"%index)
		
	def addStyle(self, family=None, weight=None, size=None, leading=None, color=None):
		"""Set the paragraph style for the following text."""
		if not family:
			family = self.family
		if not weight:
			weight = self.weight
		if not size:
			size = self.size
		if not leading:
			leading = autoLinespaceFactor*self.size
		self.data.append(idGlyphStyle%({'weight': weight, 'size': size, 'family': family, 'leading':leading}))
		if color:
			self.data.append(idColor%({'model': 'CMYK', 'c': color[0], 'm': color[1], 'y': color[2], 'k': color[3]}))
		

		
if __name__ == "__main__":
	from random import randint
	id = IDTaggedText("Minion", "Regular", size=40, leading=50)
	
	id.addStyle(color=(0,0,0,1))
	id.add("Hello")

	id.addStyle(weight="Bold", color=(0,0.5,1,0))
	id.add(" Everybody")
	id.addStyle(weight="Regular", size=100, color=(0,1,1,0))
	id.addGlyph(102)
	id.addGlyph(202)
	
	from robofab.interface.all.dialogs import PutFile
	path = PutFile("Save the tagged file:", "TaggedText.txt")
	if path:
		id.save(path)
	
	# 	then: open a document in Adobe InDesign
	#	select "Place" (cmd-D on Mac)
	#	select the text file you just generated
	#	place the text
	




	# 