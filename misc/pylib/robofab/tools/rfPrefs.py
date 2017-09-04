"""A simple module for dealing with preferences that are used by scripts. Based almost entirely on MacPrefs.

To save some preferences:
myPrefs = RFPrefs(drive/directory/directory/myPrefs.plist)
myPrefs.myString = 'xyz'
myPrefs.myInteger = 1234
myPrefs.myList = ['a', 'b', 'c']
myPrefs.myDict = {'a':1, 'b':2}
myPrefs.save()

To retrieve some preferences:
myPrefs = RFPrefs(drive/directory/directory/myPrefs.plist)
myString = myPrefs.myString
myInteger = myPrefs.myInteger
myList = myPrefs.myList
myDict = myPrefs.myDict

When using this module within FontLab, it is not necessary to
provide the RFPrefs class with a path. If a path is not given,
it will look for a file in FontLab/RoboFab Data/RFPrefs.plist.
If that file does not exist, it will make it.
"""

from robofab import RoboFabError
from robofab.plistlib import Plist
from cStringIO import StringIO
import os

class _PrefObject:
	
	def __init__(self, dict=None):
		if not dict:
			self._prefs = {}
		else:
			self._prefs = dict
	
	def __len__(self):
		return len(self._prefs)
	
	def __delattr__(self, attr):
		if self._prefs.has_key(attr):
			del self._prefs[attr]
		else:
			raise AttributeError, 'delete non-existing instance attribute'
	
	def __getattr__(self, attr):
		if attr == '__members__':
			keys = self._prefs.keys()
			keys.sort()
			return keys
		try:
			return self._prefs[attr]
		except KeyError:
			raise AttributeError, attr

	def __setattr__(self, attr, value):
		if attr[0] != '_':
			self._prefs[attr] = value
		else:
			self.__dict__[attr] = value
			
	def asDict(self):
		return self._prefs

class RFPrefs(_PrefObject):
	
	"""The main preferences object to call"""
	
	def __init__(self, path=None):
		from robofab.world import world
		self.__path = path
		self._prefs = {}
		if world.inFontLab:
			#we don't have a path, but we know where we can put it
			if not path:
				from robofab.tools.toolsFL import makeDataFolder
				settingsPath = makeDataFolder()
				path = os.path.join(settingsPath, 'RFPrefs.plist')
				self.__path = path
				self._makePrefsFile()
			#we do have a path, make sure it exists and load it
			else:
				self._makePrefsFile()
		else:
			#no path, raise error
			if not path:
				raise RoboFabError, "no preferences path defined"
			#we do have a path, make sure it exists and load it
			else:
				self._makePrefsFile()
		self._prefs = Plist.fromFile(path)
			
	def _makePrefsFile(self):
		if not os.path.exists(self.__path):
			self.save()
	
	def __getattr__(self, attr):
		if attr[0] == '__members__':
			keys = self._prefs.keys()
			keys.sort()
			return keys
		try:
			return self._prefs[attr]
		except KeyError:
			raise AttributeError, attr
			#if attr[0] != '_':
			#	self._prefs[attr] = _PrefObject()
			#	return self._prefs[attr]
			#else:
			#	raise AttributeError, attr
			
	def save(self):
		"""save the plist file"""
		f = StringIO()
		pl = Plist()
		for i in self._prefs.keys():
			pl[i] = self._prefs[i]
		pl.write(f)
		data = f.getvalue()
		f = open(self.__path, 'wb')
		f.write(data)
		f.close()
