"""
T.O.O.L.S.: Things Other Objects Lack (Sometimes)
-assorted raw tools.

This is an assorted colection of raw tools that do
things inside of FontLab. Many of these functions
form the bedrock of objectsFL. In short, use these
tools only if you need the raw functions and they are
not supported by the objects.

Object model:
Most of these tools were written before
objectsFL. Some of these tools are used by
objectsFL. That means that if you want to
use functions from robofab.tools you can always
feed them FontLab objects (like Font, Glyps,
etc.). If the functions also accept Robjects from
robofab.objects it is usually mentioned in the
doc string.

This is a simple way to convert a robofab Font
object back to a FL Font object. Even if you don't
know which particular faith an object belongs to
you can use this:

font = unwrapFont(font)
"""


from FL import *
from warnings import warn

try:
	from fl_cmd import *
except ImportError:
	print "The fl_cmd module is not available here. toolsFL.py"
	
import os

from robofab import RoboFabError

# local encoding
if os.name == "mac":
	LOCAL_ENCODING = "macroman"
else:
	LOCAL_ENCODING = "latin-1"
	
	
#
#
#
#	stuff for fontlab app
#
#
#

def AppFolderRenamer():
	"""This function will rename the folder that contains the
	FontLab application to a more specific name that includes
	the version of the application
	Warning: it messes with the paths of your app, if you have
	items that hardwired to this path you'd be in trouble.
	"""
	if fl.count > 0:
		warn("Close all fonts before running AppFolderRenamer")
		return
	old = fl.path[:-1]
	root = os.path.dirname(old)
	new = "FontLab " + fl.version.replace('/', '_')
	path = os.path.join(root, new)
	if path != old:
		try:
			os.rename(old, path)
		except OSError:
			pass
		warn("Please quit and restart FontLab")
			
#
#
#
#	stuff for fonts
#
#
#

def GetFont(full_name):
	"""Return fontobjects which match full_name.
	Note: result is a list.
	Returns: a list of FL Font objects
	"""
	found = []
	for f in AllFonts():
		if f.full_name == full_name:
			found.append(f)
	return found

def AllFonts():
	"""Collect a list of all open fonts.
	Returns: a list of FL Font objects.
	"""
	fontcount = len(fl)
	af = []
	for i in range(fontcount):
		af.append(fl[i])
	return af

def FontIndex(font):
	"""return the index of a specified FL Font"""
	font = unwrapFont(font)
	a = AllFonts()
	p = []
	for f in a:
		p.append(f.file_name)
	if font.file_name in p:
		return p.index(font.file_name)
	else:
		return None
		
def unwrapFont(font):
	"""Unwrap the font if it happens to be a RoboFab Font"""
	if hasattr(font, 'isRobofab'):
		return font.naked()
	return font

def MakeTempFont(font, dupemark=None, removeOverlap=True, decompose=True):
	"""Save the current FL Font,
	- close the file,
	- duplicate the file in the finder (icon looks weird, but it works)
	- open the duplicate
	- decompose the glyphs
	- remove overlaps
	- return the fontobject

	font  is either a FL Font or RF RFont object.
	
	Problems: doesn't check if the filename is getting too long.
	Note: it will overwrite older files with the same name.
	"""	
	import string
	f = unwrapFont(font)
	if not dupemark or dupemark == "":
		dupemark = "_tmp_"
	path = f.file_name
	a = f.file_name.split('.')
	a.insert(len(a)-1, dupemark)
	newpath = string.join(a, '.')
	f.Save(path)
	fl.Close(FontIndex(f))
	file = open(path, 'rb')
	data = file.read()
	file.close()
	file = open(newpath, 'wb')
	file.write(data)
	file.close()
	fl.Open(newpath, 1)
	nf = fl.font
	if nf is None:
		print 'uh oh, sup?'
		return None
	else:
		for g in nf.glyphs:
			if decompose:
				g.Decompose()
			if removeOverlap:
				g.RemoveOverlap()
		return nf

def makePSFontName(name):
	"""Create a postscript filename out of a regular postscript fontname,
	using the old fashioned macintosh 5:3:3 convention.
	"""
	import string
	parts = []
	current = []
	final = []
	notAllowed = '-_+=,-'
	index = 0
	for c in name:
		if c in notAllowed:
			continue
		if c in string.uppercase or index == 0:
			c = string.upper(c)
			if current:
				parts.append("".join(current))
			current = [c]
		else:
			current.append(c)
		index = index + 1
	if current:
		parts.append("".join(current))
	final.append(parts[0][:5])
	for p in parts[1:]:
		final.append(p[:3])
	return "".join(final)

#
#
#
#	stuff for glyphs
#
#
#

def NewGlyph(font, glyphName, clear=False, updateFont=True):
	"""Make a new glyph if it doesn't already exist, return the glyph.
	font is either a FL Font or RF RFont object. If updateFont is True
	the (very slow) fl.UpdateFont function will be called.
	"""
	font = unwrapFont(font)
	if isinstance(glyphName, unicode):
		glyphName = glyphName.encode(LOCAL_ENCODING)
	glyph = font[glyphName]
	if glyph is None:
		new = Glyph()
		new.name = glyphName
		font.glyphs.append(new)
		if updateFont:
			fl.UpdateFont(FontIndex(font))
		glyph = font[glyphName]
	elif clear:
		glyph.Clear()
		glyph.anchors.clean()
		glyph.components.clean()
		glyph.note = ""
	return glyph


def AddToAlias(additions, sep='+'):
	"""additions is a dict with glyphnames as keys
	and glyphConstruction as values. In order to make
	a bunch of additions in one go rather than open
	and close the file for each name.	Add a glyph
	to the alias.dat file if it doesn't already exist.
	additions = {'Gcircumflex': ['G','circumflex'], }
	Returns a list of only the added glyphnames."""
	import string
	glyphs = {}
	data = []
	new = []
	path = os.path.join(fl.path, 'Mapping', 'alias.dat')
	if os.path.exists(path):
		file = open(path, 'r')
		data = file.read().split('\n')
		file.close()
	for i in data:
		if len(i) == 0: continue
		if i[0] != '%':
			glyphs[i.split(' ')[0]] = i.split(' ')[1]
	for glyphName, glyphConstruction in additions.items():
		if glyphName not in glyphs.keys():
			new.append(glyphName)
			glyphs[glyphName] = string.join(glyphConstruction, sep)
	newNames = ['%%FONTLAB ALIASES']
	l = glyphs.keys()
	l.sort()
	for i in l:
		newNames.append(string.join([i, glyphs[i]], ' '))
		file = open(path, 'w')
		file.write(string.join(newNames, '\n'))
		file.close()
	return new


def GlyphIndexTable(font):
	"""Make a glyph index table for font"""
	font = unwrapFont(font)
	idx = {}
	for i in range(len(font)):
		g = font.glyphs[i]
		idx[g.name] = i
	return idx

def MakeReverseCompoMapping(font):
	"""Return a dict that maps glyph names to lists containing tuples
	of the form:
	   (clientGlyphName, componentIndex)
	"""
	font = unwrapFont(font)
	reverseCompoMapping = {}
	for g in font.glyphs:
		for i, c in zip(range(len(g.components)), g.components):
			base = font[c.index].name
			if not base in reverseCompoMapping:
				reverseCompoMapping[base] = []
			reverseCompoMapping[base].append((g.name, i))
	return reverseCompoMapping


#
#
#
#	stuff for text files
#
#
#

def textPrinter(text, name=None, path=None):
	"""Write a string to a text file. If no name is given it becomes
	Untitled_hour_minute_second.txt . If no path is given it goes
	into the FontLab/RoboFab Data directory."""
	if not name:
		import time
		tm_year,tm_mon,tm_day,tm_hour,tm_min,tm_sec,tm_wday,tm_yday,tm_isdst = time.localtime()
		now = '_'.join((`tm_hour`, `tm_min`, `tm_sec`))
		name = 'Untitled_%s.txt'%now
	if not path:
		path = os.path.join(makeDataFolder(), name)
	f = open(path, 'wb')
	f.write(text)
	f.close()

def makeDataFolder():
	"""Make the RoboFab data folder"""
	folderPath = os.path.join(fl.path, "RoboFab Data")
	if not os.path.exists(folderPath):
		try:
			os.makedirs(folderPath)
		except:
			pass
	return folderPath
	

def Log(text=None):
	"""Make an entry in the default log file."""
	now = str(time.asctime(time.localtime(time.time())))
	if not text:
		text = "-"
	entry = "%s: %s\r"%(now, text)
	path = os.path.join(os.getcwd(), "Logs")
	new = 0
	if not os.path.exists(path):
		os.makedirs(path)
		new = 1
	log = os.path.join(path, "log.txt")
	f = open(log, 'a')
	if new:
		f.write("# log file for FL\r")
	f.write(entry)
	f.close()
