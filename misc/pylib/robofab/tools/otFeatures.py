"""Simple module to write features to font"""


import string


from types import StringType, ListType, TupleType

from robofab.world import world
if world.inFontLab:
	from FL import *
	from fl_cmd import *
from robofab.tools.toolsFL import FontIndex

		#feat = []
		#feat.append('feature smcp {')
		#feat.append('\tlookup SMALLCAPS {')
		#feat.append('\t\tsub @LETTERS_LC by @LETTERS_LC;')
		#feat.append('\t} SMALLCAPS;')
		#feat.append('} smcp;')


class FeatureWriter:
	"""Make properly formatted feature code"""
	def __init__(self, type):
		self.type = type
		self.data = []
		
	def add(self, src, dst):
		"""Add a substitution: change src to dst."""
		self.data.append((src, dst))
	
	def write(self, group=0):
		"""Write the whole thing to string"""
		t = []
		if len(self.data) == 0:
			return None
		t.append('feature %s {' % self.type)
		for src, dst in self.data:
			if isinstance(src, (list, tuple)):
				if group:
					src = "[%s]" % string.join(src, ' ')
				else:
					src = string.join(src, ' ')
			if isinstance(dst, (list, tuple)):
				if group:
					dst = "[%s]" % string.join(dst, ' ')
				else:
					dst = string.join(dst, ' ')
			src = string.strip(src)
			dst = string.strip(dst)
			t.append("\tsub %s by %s;" % (src, dst))
		t.append('}%s;' % self.type)
		return string.join(t, '\n')


class GlyphName:
	"""Simple class that splits a glyphname in handy parts,
	access the parts as attributes of the name."""
	def __init__(self, name):
		self.suffix = []
		self.ligs = []
		self.name = self.base = name
		if '.' in name:
			self.bits = name.split('.')
			self.base = self.bits[0]
			self.suffix = self.bits[1:]
		if '_' in name:
			self.ligs = self.base.split('_')


def GetAlternates(font, flavor="alt", match=0):
	"""Sort the glyphs of this font by the parts of the name.
	flavor is the bit to look for, i.e. 'alt' in a.alt
	match = 1 if you want a exact match: alt1 != alt
	match = 0 if the flavor is a partial match: alt == alt1
	"""
	names = {}
	for c in font.glyphs:
		name = GlyphName(c.name)
		if not names.has_key(name.base):
			names[name.base] = []
		if match:
			# only include if there is an exact match
			if flavor in name.suffix:
				names[name.base].append(c.name)
		else:
			# include if there is a partial match
			for a in name.suffix:
				if a.find(flavor) != -1:
					names[name.base].append(c.name)
	return names
		

# XXX there should be a more generic glyph finder.

def MakeCapsFeature(font):
	"""Build a feature for smallcaps based on .sc glyphnames"""
	names = GetAlternates(font, 'sc', match=1)
	fw = FeatureWriter('smcp')
	k = names.keys()
	k.sort()
	for p in k:
		if names[p]:
			fw.add(p, names[p])
	feat = fw.write()
	if feat:
		font.features.append(Feature('smcp', feat))
	return feat
		

def MakeAlternatesFeature(font):
	"""Build a aalt feature based on glyphnames"""
	names = GetAlternates(font, 'alt', match=0)
	fw = FeatureWriter('aalt')
	k = names.keys()
	k.sort()
	for p in k:
		if names[p]:
			fw.add(p, names[p])
	feat = fw.write(group=1)
	if feat:
		font.features.append(Feature('aalt', feat))
	return feat
	

def MakeSwashFeature(font):
	"""Build a swash feature based on glyphnames"""
	names = GetAlternates(font, 'swash', match=0)
	fw = FeatureWriter('swsh')
	k=names.keys()
	k.sort()
	for p in k:
		if names[p]:
			l=names[p]
			l.sort()
			fw.add(p, l[0])
	feat=fw.write()
	if feat:
		font.features.append(Feature('swsh', feat))
	return feat
	

def MakeLigaturesFeature(font):
	"""Build a liga feature based on glyphnames"""
	from robofab.gString import ligatures
	ligCountDict = {}
	for glyph in font.glyphs:
		if glyph.name in ligatures:
			if len(glyph.name) not in ligCountDict.keys():
				ligCountDict[len(glyph.name)] = [glyph.name]
			else:
				ligCountDict[len(glyph.name)].append(glyph.name)
		elif glyph.name.find('_') != -1:
			usCounter=1
			for i in glyph.name:
				if i =='_':
					usCounter=usCounter+1
			if usCounter not in ligCountDict.keys():
				ligCountDict[usCounter] = [glyph.name]
			else:
				ligCountDict[usCounter].append(glyph.name)
	ligCount=ligCountDict.keys()
	ligCount.sort()
	foundLigs=[]
	for i in ligCount:
		l = ligCountDict[i]
		l.sort()
		foundLigs=foundLigs+l
	fw=FeatureWriter('liga')
	for i in foundLigs:
		if i.find('_') != -1:
			sub=i.split('_')
		else:
			sub=[]
			for c in i:
				sub.append(c)
		fw.add(sub, i)
	feat=fw.write()
	if feat:
		font.features.append(Feature('liga', feat))
	return feat
	

if __name__ == "__main__":
	fw = FeatureWriter('liga')
	fw.add(['f', 'f', 'i'], ['f_f_i'])
	fw.add('f f ', 'f_f')
	fw.add(['f', 'i'], 'f_i')
	print fw.write()
