"""Remote control for MacOS FontLab.
initFontLabRemote() registers a callback for appleevents and
runFontLabRemote() sends the code from a different application,
such as a Mac Python IDE or Python interpreter.
"""

from robofab.world import world

if world.inFontLab and world.mac is not None:
	from Carbon import AE as _AE

else:
	import sys
	from aetools import TalkTo

	class FontLab(TalkTo):
		pass

__all__ = ['initFontLabRemote', 'runFontLabRemote']

def _executePython(theAppleEvent, theReply):
	import aetools
	import cStringIO
	import traceback
	import sys
	parms, attrs = aetools.unpackevent(theAppleEvent)
	source = parms.get("----")
	if source is None:
		return
	stdout = cStringIO.StringIO()
	#print "<executing remote command>"
	save = sys.stdout, sys.stderr
	sys.stdout = sys.stderr = stdout
	namespace = {}
	try:
		try:
			exec source in namespace
		except:
			traceback.print_exc()
	finally:
		sys.stdout, sys.stderr = save
	output = stdout.getvalue()
	aetools.packevent(theReply, {"----": output})

_imported = False

def initFontLabRemote():
	"""Call this in FontLab at startup of the application to switch on the remote."""
	print "FontLabRemote is on."
	_AE.AEInstallEventHandler("Rfab", "exec", _executePython)

if world.inFontLab and world.mac is not None:
	initFontLabRemote()

def runFontLabRemote(code):
	"""Call this in the MacOS Python IDE to make FontLab execute the code."""
	fl = FontLab("FLab", start=1)
	ae, parms, attrs = fl.send("Rfab", "exec", {"----": code})
	output = parms.get("----")
	return output



#	GlyphTransmit
#	Convert a glyph to  a string using digestPen, transmit string, unpack string with pointpen.
#


def Glyph2String(glyph):
	from robofab.pens.digestPen import DigestPointPen
	import pickle
	p = DigestPointPen(glyph)
	glyph.drawPoints(p)
	info = {}
	info['name'] = glyph.name
	info['width'] = glyph.width
	info['points'] = p.getDigest()
	return str(pickle.dumps(info))

def String2Glyph(gString, penClass, font):
	import pickle
	if gString is None:
		return None
	info = pickle.loads(gString)
	name = info['name']
	if not name in font.keys():
		glyph = font.newGlyph(name)
	else:
		glyph = font[name]
	pen = penClass(glyph)
	for p in info['points']:
		if p == "beginPath":
			pen.beginPath()
		elif p == "endPath":
			pen.endPath()
		else:
			pt, type = p
			pen.addPoint(pt, type)
	glyph.width = info['width']
	glyph.update()
	return glyph

_makeFLGlyph = """
from robofab.world import CurrentFont
from robofab.tools.remote import receiveGlyph
code = '''%s'''
receiveGlyph(code, CurrentFont())
"""

def transmitGlyph(glyph):
	from robofab.world import world
	if world.inFontLab and world.mac is not None:
		# we're in fontlab, on a mac
		print Glyph2String(glyph)
		pass
	else:
		remoteProgram = _makeFLGlyph%Glyph2String(glyph)
		print "remoteProgram", remoteProgram
		return runFontLabRemote(remoteProgram)

def receiveGlyph(glyphString,  font=None):
	from robofab.world import world
	if world.inFontLab and world.mac is not None:
		# we're in fontlab, on a mac
		from robofab.pens.flPen import FLPointPen
		print String2Glyph(glyphString, FLPointPen, font)
		pass
	else:
		from robofab.pens.rfUFOPen import RFUFOPointPen
		print String2Glyph(glyphString, RFUFOPointPen, font)
		

#
#	command to tell FontLab to open a UFO and save it as a vfb

def os9PathConvert(path):
	"""Attempt to convert a unix style path to a Mac OS9 style path.
	No support for relative paths!
	"""
	if path.find("/Volumes") == 0:
		# it's on the volumes list, some sort of external volume
		path = path[len("/Volumes")+1:]
	elif path[0] == "/":
		# a dir on the root volume
		path = path[1:]
	new = path.replace("/", ":")
	return new
		
	
_remoteUFOImportProgram = """
from robofab.objects.objectsFL import NewFont
import os.path
destinationPathVFB = "%(destinationPathVFB)s"
font = NewFont()
font.readUFO("%(sourcePathUFO)s", doProgress=True)
font.update()
font.save(destinationPathVFB)
print font, "done"
font.close()
"""				

def makeVFB(sourcePathUFO, destinationPathVFB=None):
	"""FontLab convenience function to import a UFO and save it as a VFB"""
	import os
	fl = FontLab("FLab", start=1)
	if destinationPathVFB is None:
		destinationPathVFB = os.path.splitext(sourcePathUFO)[0]+".vfb"
	src9 = os9PathConvert(sourcePathUFO)
	dst9 = os9PathConvert(destinationPathVFB)
	code = _remoteUFOImportProgram%{'sourcePathUFO': src9, 'destinationPathVFB':dst9}
	ae, parms, attrs = fl.send("Rfab", "exec", {"----": code})
	output = parms.get("----")
	return output

		