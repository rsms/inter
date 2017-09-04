"""Simple and ugly way to print some attributes and properties of an object to stdout.
FontLab doesn't have an object browser and sometimes we do need to look inside"""

from pprint import pprint

def classname(object, modname):
    """Get a class name and qualify it with a module name if necessary."""
    name = object.__name__
    if object.__module__ != modname:
        name = object.__module__ + '.' + name
    return name

def _objectDumper(object, indent=0, private=False):
	"""Collect a dict with the contents of the __dict__ as a quick means of peeking inside
	an instance. Some RoboFab locations do not support PyBrowser and still need debugging."""
	data = {}
	data['__class__'] = "%s at %d"%(classname(object.__class__, object.__module__), id(object))
	for k in object.__class__.__dict__.keys():
		if private and k[0] == "_":
			continue
		x = object.__class__.__dict__[k]
		if hasattr(x, "fget"):	#other means of recognising a property?
			try:
				try:
					value = _objectDumper(x.fget(self), 1)
				except:
					value = x.fget(self)
				data[k] = "[property, %s] %s"%(type(x.fget(self)).__name__, value)
			except:
				data[k] = "[property] (Error getting property value)"
	for k in object.__dict__.keys():
		if private and k[0] == "_":
			continue
		try:	
			data[k] = "[attribute, %s] %s"%(type(object.__dict__[k]).__name__, `object.__dict__[k]`)
		except:
			data[k] = "[attribute] (Error getting attribute value)"
	return data

def flattenDict(dict, indent=0):
	t = []
	k = dict.keys()
	k.sort()
	print
	print '---RoboFab Object Dump---'
	for key in k:
		value = dict[key]
		t.append(indent*"\t"+"%s: %s"%(key, value))
	t.append('')
	return "\r".join(t)

def dumpObject(object, private=False):
	print pprint(_objectDumper(object, private=private))


