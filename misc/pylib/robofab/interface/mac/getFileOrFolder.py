"""This module provides two functions, very similar to
EasyDialogs.AskFileForOpen() and EasyDialogs.AskFolder(): GetFile() and
GetFileOrFolder(). The main difference is that the functions here fully
support "packages" or "bundles", ie. folders that appear to be files in
the finder and open/save dialogs. The second difference is that
GetFileOrFolder() allows the user to select a file _or_ a folder.
"""


__all__ = ["GetFile", "GetFileOrFolder"]


from EasyDialogs import _process_Nav_args, _interact
import Nav
import Carbon.File


# Lots of copy/paste from EasyDialogs.py, for one because althought the
# EasyDialogs counterparts take a million options, they don't take the
# one option I need: the flag to support packages...

kNavSupportPackages = 0x00001000


def GetFile(message=None, title=None, directory=None, fileName=None, allowsMultipleSelection=False, fileTypes=None):
	"""Ask the user to select a file.
	
	Some of these arguments are not supported:
	    title, directory, fileName, allowsMultipleSelection and fileTypes are here for compatibility reasons.
	"""
	default_flags = 0x56 | kNavSupportPackages
	args, tpwanted = _process_Nav_args(default_flags, message=message)
	_interact()
	try:
		rr = Nav.NavChooseFile(args)
		good = 1
	except Nav.error, arg:
		if arg[0] != -128: # userCancelledErr
			raise Nav.error, arg
		return None
	if not rr.validRecord or not rr.selection:
		return None
	if issubclass(tpwanted, Carbon.File.FSRef):
		return tpwanted(rr.selection_fsr[0])
	if issubclass(tpwanted, Carbon.File.FSSpec):
		return tpwanted(rr.selection[0])
	if issubclass(tpwanted, str):
		return tpwanted(rr.selection_fsr[0].as_pathname())
	if issubclass(tpwanted, unicode):
		return tpwanted(rr.selection_fsr[0].as_pathname(), 'utf8')
	raise TypeError, "Unknown value for argument 'wanted': %s" % repr(tpwanted)


def GetFileOrFolder(message=None, title=None, directory=None, fileName=None, allowsMultipleSelection=False, fileTypes=None):
	"""Ask the user to select a file or a folder.

	Some of these arguments are not supported:
	    title, directory, fileName, allowsMultipleSelection and fileTypes are here for compatibility reasons.
	"""
	default_flags = 0x17 | kNavSupportPackages
	args, tpwanted = _process_Nav_args(default_flags, message=message)
	_interact()
	try:
		rr = Nav.NavChooseObject(args)
		good = 1
	except Nav.error, arg:
		if arg[0] != -128: # userCancelledErr
			raise Nav.error, arg
		return None
	if not rr.validRecord or not rr.selection:
		return None
	if issubclass(tpwanted, Carbon.File.FSRef):
		return tpwanted(rr.selection_fsr[0])
	if issubclass(tpwanted, Carbon.File.FSSpec):
		return tpwanted(rr.selection[0])
	if issubclass(tpwanted, str):
		return tpwanted(rr.selection_fsr[0].as_pathname())
	if issubclass(tpwanted, unicode):
		return tpwanted(rr.selection_fsr[0].as_pathname(), 'utf8')
	raise TypeError, "Unknown value for argument 'wanted': %s" % repr(tpwanted)
