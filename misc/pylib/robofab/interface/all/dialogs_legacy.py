
"""

Dialogs.
Cross-platform and cross-application compatible. Some of them anyway.
(Not all dialogs work on PCs outside of FontLab. Some dialogs are for FontLab only. Sorry.)

Mac and FontLab implementation written by the RoboFab development team.
PC implementation by Eigi Eigendorf and is (C)2002 Eigi Eigendorf.

"""

import os
import sys
from robofab import RoboFabError
from warnings import warn

MAC = False
PC = False
haveMacfs = False

if sys.platform in ('mac', 'darwin'):
	MAC = True
elif os.name == 'nt':
	PC = True
else:
	warn("dialogs.py only supports Mac and PC platforms.")
pyVersion = sys.version_info[:3]

inFontLab = False
try:
	from FL import *
	inFontLab = True
except ImportError: pass


try:
	import W
	hasW = True
except ImportError:
	hasW = False

try:
	import dialogKit
	hasDialogKit = True
except ImportError:
	hasDialogKit = False
	
try:
	import EasyDialogs
	hasEasyDialogs = True
except:
	hasEasyDialogs = False
	
if MAC:
	if pyVersion < (2, 3, 0):
		import macfs
		haveMacfs = True
elif PC and not inFontLab:
	from win32com.shell import shell
	import win32ui
	import win32con


def _raisePlatformError(dialog):
	"""error raiser"""
	if MAC:
		p = 'Macintosh'
	elif PC:
		p = 'PC'
	else:
		p = sys.platform
	raise RoboFabError("%s is not currently available on the %s platform"%(dialog, p))


class _FontLabDialogOneList:
	"""A one list dialog for FontLab. This class should not be called directly. Use the OneList function."""
	
	def __init__(self, list, message, title='RoboFab'):
		self.message = message
		self.selected = None
		self.list = list
		self.d = Dialog(self)
		self.d.size = Point(250, 250)
		self.d.title = title
		self.d.Center()
		self.d.AddControl(LISTCONTROL, Rect(12, 30, 238, 190), "list", STYLE_LIST, self.message)
		self.list_index = 0
	
	def Run(self):
		return self.d.Run()
	
	def on_cancel(self, code):
		self.selected = None
	
	def on_ok(self, code):
		self.d.GetValue('list')
		# Since FLS v5.2, the GetValue() method of the Dialog() class returns
		# a 'wrong' index value from the specified LISTCONTROL.
		# If the selected index is n, it will return n-1. For example, when
		# the index is 1, it returns 0; when it's 2, it returns 1, and so on.
		# If the selection is empty, FLS v5.2 returns -2, while the old v5.0 
		# returned None.
		# See also:
		# - http://forum.fontlab.com/index.php?topic=8807.0
		# - http://forum.fontlab.com/index.php?topic=9003.0
		#
		# Edited based on feedback from Adam Twardoch
		if fl.buildnumber > 4600 and sys.platform == 'win32':
			if self.list_index == -2:
				self.selected = None
			else:
				self.selected = self.list_index + 1
		else:
			self.selected = self.list_index


class _FontLabDialogSearchList:
	"""A dialog for searching through a list. It contains a text field and a results list FontLab. This class should not be called directly. Use the SearchList function."""
	
	def __init__(self, aList, message, title="RoboFab"):
		self.d = Dialog(self)
		self.d.size = Point(250, 290)
		self.d.title = title
		self.d.Center()
		
		self.message = message
		self._fullContent = aList
		self.possibleHits = list(aList)
		self.possibleHits.sort()
		self.possibleHits_index = 0
		self.entryField = ""
		self.selected = None
		
		self.d.AddControl(STATICCONTROL, Rect(10, 10, 240, 30), "message", STYLE_LABEL, message)
		self.d.AddControl(EDITCONTROL, Rect(10, 30, 240, aAUTO), "entryField", STYLE_EDIT, "")
		self.d.AddControl(LISTCONTROL, Rect(12, 60, 238, 230), "possibleHits", STYLE_LIST, "")
		
		
	def run(self):
		self.d.Run()
	
	def on_entryField(self, code):
		self.d.GetValue("entryField")
		entry = self.entryField
		count = len(entry)
		possibleHits = [
				i for i in self._fullContent
				if len(i) >= count
				and i[:count] == entry
				]
		possibleHits.sort()
		self.possibleHits = possibleHits
		self.possibleHits_index = 0
		self.d.PutValue("possibleHits")
	
	def on_ok(self, code):
		self.d.GetValue("possibleHits")
		sel = self.possibleHits_index
		if sel == -1:
			self.selected = None
		else:
			self.selected = self.possibleHits[sel]
	
	def on_cancel(self, code):
		self.selected = None
		
		
class _FontLabDialogTwoFields:
	"""A two field dialog for FontLab. This class should not be called directly. Use the TwoFields function."""
	
	def __init__(self, title_1, value_1, title_2, value_2, title='RoboFab'):
		self.d = Dialog(self)
		self.d.size = Point(200, 125)
		self.d.title = title
		self.d.Center()
		self.d.AddControl(EDITCONTROL, Rect(120, 10, aIDENT2, aAUTO), "v1edit", STYLE_EDIT, title_1)		
		self.d.AddControl(EDITCONTROL, Rect(120, 40, aIDENT2, aAUTO), "v2edit", STYLE_EDIT, title_2)
		self.v1edit = value_1
		self.v2edit = value_2

	def Run(self):
		return self.d.Run()
	
	def on_cancel(self, code):
		self.v1edit = None
		self.v2edit = None
	
	def on_ok(self, code):
		self.d.GetValue("v1edit")
		self.d.GetValue("v2edit")
		self.v1 = self.v1edit
		self.v2 = self.v2edit
		
class _FontLabDialogTwoChecks:
	"""A two check box dialog for FontLab. This class should not be called directly. Use the TwoChecks function."""

	def __init__(self, title_1, title_2, value1=1, value2=1, title='RoboFab'):
		self.d = Dialog(self)
		self.d.size = Point(200, 105)
		self.d.title = title
		self.d.Center()
		self.d.AddControl(CHECKBOXCONTROL, Rect(10, 10, aIDENT2, aAUTO), "check1", STYLE_CHECKBOX, title_1) 
		self.d.AddControl(CHECKBOXCONTROL, Rect(10, 30, aIDENT2, aAUTO), "check2", STYLE_CHECKBOX, title_2) 
		self.check1 = value1
		self.check2 = value2
			
	def Run(self):
		return self.d.Run()
	
	def on_cancel(self, code):
		self.check1 = None
		self.check2 = None
		
	def on_ok(self, code):
		self.d.GetValue("check1")
		self.d.GetValue("check2")
		

class _FontLabDialogAskString:
	"""A one simple string prompt dialog for FontLab. This class should not be called directly. Use the GetString function."""

	def __init__(self, message, value, title='RoboFab'):
		self.d = Dialog(self)
		self.d.size = Point(350, 130)
		self.d.title = title
		self.d.Center()
		self.d.AddControl(STATICCONTROL, Rect(aIDENT, aIDENT, aIDENT, aAUTO), "label", STYLE_LABEL, message) 
		self.d.AddControl(EDITCONTROL, Rect(aIDENT, 40, aIDENT, aAUTO), "value", STYLE_EDIT, '')	
		self.value=value
		
	def Run(self):
		return self.d.Run()
		
	def on_cancel(self, code):
		self.value = None
	
	def on_ok(self, code):
		self.d.GetValue("value")
		
class _FontLabDialogMessage:
	"""A simple message dialog for FontLab. This class should not be called directly. Use the SimpleMessage function."""
	
	def __init__(self, message, title='RoboFab'):
		self.d = Dialog(self)
		self.d.size = Point(350, 130)
		self.d.title = title
		self.d.Center()
		self.d.AddControl(STATICCONTROL, Rect(aIDENT, aIDENT, aIDENT, 80), "label", STYLE_LABEL, message) 
		
	def Run(self):
		return self.d.Run()
		
class _FontLabDialogGetYesNoCancel:
	"""A yes no cancel message dialog for FontLab. This class should not be called directly. Use the YesNoCancel function."""
	
	def __init__(self, message, title='RoboFab'):
		self.d = Dialog(self)
		self.d.size = Point(350, 130)
		self.d.title = title
		self.d.Center()
		self.d.ok = 'Yes'
		self.d.AddControl(STATICCONTROL, Rect(aIDENT, aIDENT, aIDENT, 80), "label", STYLE_LABEL, message)
		self.d.AddControl(BUTTONCONTROL, Rect(100, 95, 172, 115), "button", STYLE_BUTTON, "No")
		self.value = 0
		
	def Run(self):
		return self.d.Run()
	
	def on_ok(self, code):
		self.value = 1
	
	def on_cancel(self, code):
		self.value = -1
		
	def on_button(self, code):
		self.value = 0
		self.d.End()

		
class _MacOneListW:
	"""A one list dialog for Macintosh. This class should not be called directly. Use the OneList function."""
	
	def __init__(self, list, message='Make a selection'):
		import W
		self.list = list
		self.selected = None
		self.w = W.ModalDialog((200, 240))
		self.w.message = W.TextBox((10, 10, -10, 30), message)
		self.w.list = W.List((10, 35, -10, -50), list)
		self.w.l = W.HorizontalLine((10, -40, -10, 1), 1)
		self.w.cancel = W.Button((10, -30, 87, -10), 'Cancel', self.cancel)
		self.w.ok = W.Button((102, -30, 88, -10), 'OK', self.ok)		
		self.w.setdefaultbutton(self.w.ok)
		self.w.bind('cmd.', self.w.cancel.push)
		self.w.open()
		
	def ok(self):
		if len(self.w.list.getselection()) == 1:
			self.selected = self.w.list.getselection()[0]
			self.w.close()
		
	def cancel(self):
		self.selected = None
		self.w.close()
		
class _MacTwoChecksW:
	""" Version using W """
	
	def __init__(self, title_1, title_2, value1=1, value2=1, title='RoboFab'):
		import W
		self.check1 = value1
		self.check2 = value2
		self.w = W.ModalDialog((200, 100))
		self.w.check1 = W.CheckBox((10, 10, -10, 16), title_1, value=value1)
		self.w.check2 = W.CheckBox((10, 35, -10, 16), title_2, value=value2)
		self.w.l = W.HorizontalLine((10, 60, -10, 1), 1)
		self.w.cancel = W.Button((10, 70, 85, 20), 'Cancel', self.cancel)
		self.w.ok = W.Button((105, 70, 85, 20), 'OK', self.ok)
		self.w.setdefaultbutton(self.w.ok)
		self.w.bind('cmd.', self.w.cancel.push)
		self.w.open()
		
	def ok(self):
		self.check1 = self.w.check1.get()
		self.check2 = self.w.check2.get()
		self.w.close()
	
	def cancel(self):
		self.check1 = None
		self.check2 = None
		self.w.close()


class ProgressBar:
	def __init__(self, title='RoboFab...', ticks=0, label=''):
		"""
		A progress bar.
		Availability: FontLab, Mac
		"""
		self._tickValue = 1
		
		if inFontLab:
			fl.BeginProgress(title, ticks)
		elif MAC and hasEasyDialogs:
			import EasyDialogs
			self._bar = EasyDialogs.ProgressBar(title, maxval=ticks, label=label)
		else:
			_raisePlatformError('Progress')
			
	def getCurrentTick(self):
		return self._tickValue
			
			
	def tick(self, tickValue=None):
		"""
		Tick the progress bar.
		Availability: FontLab, Mac
		"""
		if not tickValue:
			tickValue = self._tickValue
		
		if inFontLab:
			fl.TickProgress(tickValue)
		elif MAC:
			self._bar.set(tickValue)
		else:
			pass
			
		self._tickValue = tickValue + 1
		
	def label(self, label):
		"""
		Set the label on the progress bar.
		Availability: Mac
		"""
		if inFontLab:
			pass
		elif MAC:
			self._bar.label(label)
		else:
			pass
		
	
	def close(self):
		"""
		Close the progressbar.
		Availability: FontLab, Mac
		"""
		if inFontLab:
			fl.EndProgress()
		elif MAC:
			del self._bar
		else:
			pass

					
def SelectFont(message="Select a font:", title='RoboFab'):
	"""
	Returns font instance if there is one, otherwise it returns None.
	Availability: FontLab
	"""
	from robofab.world import RFont
	if inFontLab:
		list = []
		for i in range(fl.count):
			list.append(fl[i].full_name)
		name = OneList(list, message, title)
		if name is None:
			return None
		else:
			return RFont(fl[list.index(name)])
	else:
		_raisePlatformError('SelectFont')
			
def SelectGlyph(font, message="Select a glyph:", title='RoboFab'):
	"""
	Returns glyph instance if there is one, otherwise it returns None.
	Availability: FontLab
	"""
	from fontTools.misc.textTools import caselessSort

	if inFontLab:
		tl = font.keys()
		list = caselessSort(tl)
		glyphname = OneList(list, message, title)
		if glyphname is None:
			return None
		else:
			return font[glyphname]
	else:
		_raisePlatformError('SelectGlyph')

def FindGlyph(font, message="Search for a glyph:", title='RoboFab'):
	"""
	Returns glyph instance if there is one, otherwise it returns None.
	Availability: FontLab
	"""

	if inFontLab:
		glyphname = SearchList(font.keys(), message, title)
		if glyphname is None:
			return None
		else:
			return font[glyphname]
	else:
		_raisePlatformError('SelectGlyph')
		
def OneList(list, message="Select an item:", title='RoboFab'):
	"""
	Returns selected item, otherwise it returns None.
	Availability: FontLab, Macintosh
	"""
	if inFontLab:
		ol = _FontLabDialogOneList(list, message)
		ol.Run()
		selected = ol.selected	
		if selected is None:
			return None
		else:
			try:
				return list[selected]
			except:
				return None
	elif MAC:
		if hasW:
			d = _MacOneListW(list, message)
			sel = d.selected
			if sel is None:
				return None
			else:
				return list[sel]
		else:
			_raisePlatformError('OneList')
	elif PC:
		_raisePlatformError('OneList')

def SearchList(list, message="Select an item:", title='RoboFab'):
	"""
	Returns selected item, otherwise it returns None.
	Availability: FontLab
	"""
	if inFontLab:
		sl = _FontLabDialogSearchList(list, message, title)
		sl.run()
		selected = sl.selected	
		if selected is None:
			return None
		else:
			return selected
	else:
		_raisePlatformError('SearchList')

def TwoFields(title_1="One:", value_1="0", title_2="Two:", value_2="0", title='RoboFab'):
	"""
	Returns (value 1, value 2).
	Availability: FontLab
	"""
	if inFontLab:
		tf = _FontLabDialogTwoFields(title_1, value_1, title_2, value_2, title)
		tf.Run()
		try:
			v1 = tf.v1
			v2 = tf.v2
			return (v1, v2)
		except:
			return None
	else:
		_raisePlatformError('TwoFields')
		
def TwoChecks(title_1="One",  title_2="Two", value1=1, value2=1, title='RoboFab'):
	"""
	Returns check value:
	1 if check box 1 is checked
	2 if check box 2 is checked
	3 if both are checked
	0 if neither are checked
	None if cancel is clicked.
	
	Availability: FontLab, Macintosh
	"""
	tc = None
	if inFontLab:
		tc = _FontLabDialogTwoChecks(title_1, title_2, value1, value2, title)
		tc.Run()
	elif MAC:
		if hasW:
			tc = _MacTwoChecksW(title_1, title_2, value1, value2, title)
		else:
			_raisePlatformError('TwoChecks')
	else:
		_raisePlatformError('TwoChecks')
	c1 = tc.check1
	c2 = tc.check2
	if c1 == 1 and c2 == 0:
		return 1
	elif c1 == 0 and c2 == 1:
		return 2
	elif c1 == 1 and c2 == 1:
		return 3
	elif c1 == 0 and c2 == 0:
		return 0
	else:
		return None
		
def Message(message, title='RoboFab'):
	"""
	A simple message dialog.
	Availability: FontLab, Macintosh
	"""
	if inFontLab:
		_FontLabDialogMessage(message, title).Run()
	elif MAC:
		import EasyDialogs
		EasyDialogs.Message(message)
	else:
		_raisePlatformError('Message')
		
def AskString(message, value='', title='RoboFab'):
	"""
	Returns entered string.
	Availability: FontLab, Macintosh
	"""
	if inFontLab:
		askString = _FontLabDialogAskString(message, value, title)
		askString.Run()
		v = askString.value
		if v is None:
			return None
		else:
			return v
	elif MAC:
		import EasyDialogs
		askString = EasyDialogs.AskString(message)
		if askString is None:
			return None
		if len(askString) == 0:
			return None
		else:
			return askString
	else:
		_raisePlatformError('GetString')
		
def AskYesNoCancel(message, title='RoboFab', default=0):
	"""
	Returns 1 for 'Yes', 0 for 'No' and -1 for 'Cancel'.
	Availability: FontLab, Macintosh
	("default" argument only available on Macintosh)
	"""
	if inFontLab:
		gync = _FontLabDialogGetYesNoCancel(message, title)
		gync.Run()
		v = gync.value
		return v
	elif MAC:
		import EasyDialogs
		gync = EasyDialogs.AskYesNoCancel(message, default=default)
		return gync
	else:
		_raisePlatformError('GetYesNoCancel')
		
def GetFile(message=None):
	"""
	Select file dialog. Returns path if one is selected. Otherwise it returns None.
	Availability: FontLab, Macintosh, PC
	"""
	path = None
	if MAC:
		if haveMacfs:
			fss, ok = macfs.PromptGetFile(message)
			if ok:
				path = fss.as_pathname()
		else:
			from robofab.interface.mac.getFileOrFolder import GetFile
			path = GetFile(message)
	elif PC:
		if inFontLab:
			if not message:
				message = ''
			path = fl.GetFileName(1, message, '', '')
		else:
			openFlags = win32con.OFN_FILEMUSTEXIST|win32con.OFN_EXPLORER
			mode_open = 1
			myDialog = win32ui.CreateFileDialog(mode_open,None,None,openFlags)
			myDialog.SetOFNTitle(message)
			is_OK = myDialog.DoModal()
			if is_OK == 1:
				path = myDialog.GetPathName()
	else:
		_raisePlatformError('GetFile')
	return path
	
def GetFolder(message=None):
	"""
	Select folder dialog. Returns path if one is selected. Otherwise it returns None.
	Availability: FontLab, Macintosh, PC
	"""
	path = None
	if MAC:
		if haveMacfs:
			fss, ok = macfs.GetDirectory(message)
			if ok:
				path = fss.as_pathname()
		else:
			from robofab.interface.mac.getFileOrFolder import GetFileOrFolder
			# This _also_ allows the user to select _files_, but given the
			# package/folder dichotomy, I think we have no other choice.
			path = GetFileOrFolder(message)
	elif PC:
		if inFontLab:
			if not message:
				message = ''
			path = fl.GetPathName('', message)
		else:
			myTuple = shell.SHBrowseForFolder(0, None, message, 64)
			try:
				path = shell.SHGetPathFromIDList(myTuple[0])
			except:
				pass
	else:
		_raisePlatformError('GetFile')
	return path
	
GetDirectory = GetFolder

def PutFile(message=None, fileName=None):
	"""
	Save file dialog. Returns path if one is entered. Otherwise it returns None.
	Availability: FontLab, Macintosh, PC
	"""
	path = None
	if MAC:
		if haveMacfs:
			fss, ok = macfs.StandardPutFile(message, fileName)
			if ok:
				path = fss.as_pathname()
		else:
			import EasyDialogs
			path = EasyDialogs.AskFileForSave(message, savedFileName=fileName)
	elif PC:
		if inFontLab:
			if not message:
				message = ''
			if not fileName:
				fileName = ''
			path = fl.GetFileName(0, message, fileName, '')
		else:
			openFlags = win32con.OFN_OVERWRITEPROMPT|win32con.OFN_EXPLORER
			mode_save = 0
			myDialog = win32ui.CreateFileDialog(mode_save, None, fileName, openFlags)
			myDialog.SetOFNTitle(message)
			is_OK = myDialog.DoModal()
			if is_OK == 1:
				path = myDialog.GetPathName()
	else:
		_raisePlatformError('GetFile')
	return path


if __name__=='__main__':
	import traceback
	
	print "dialogs hasW", hasW
	print "dialogs hasDialogKit", hasDialogKit
	print "dialogs MAC", MAC
	print "dialogs PC", PC
	print "dialogs inFontLab", inFontLab
	print "dialogs hasEasyDialogs", hasEasyDialogs
	
	def tryDialog(dialogClass, args=None):
		print
		print "tryDialog:", dialogClass, "with args:", args
		try:
			if args is not None:
				apply(dialogClass, args)
			else:
				apply(dialogClass)
		except:
			traceback.print_exc(limit=0)

	tryDialog(TwoChecks, ('hello', 'world', 1, 0, 'ugh'))
	tryDialog(TwoFields)
	tryDialog(TwoChecks, ('hello', 'world', 1, 0, 'ugh'))
	tryDialog(OneList, (['a', 'b', 'c'], 'hello world'))
	tryDialog(Message, ('hello world',))
	tryDialog(AskString, ('hello world',))
	tryDialog(AskYesNoCancel, ('hello world',))

	try:
		b = ProgressBar('hello', 50, 'world')
		for i in range(50):
			if i == 25:
				b.label('ugh.')
			b.tick(i)
		b.close()
	except:
		traceback.print_exc(limit=0)
