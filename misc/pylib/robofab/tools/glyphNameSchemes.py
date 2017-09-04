"""A separate module for glyphname to filename functions.

glyphNameToShortFileName() generates a non-clashing filename for systems with
filename-length limitations.
"""

MAXLEN = 31

def glyphNameToShortFileName(glyphName, glyphSet):
	"""Alternative glyphname to filename function.

	Features a garuanteed maximum filename for really long glyphnames, and clash testing.
	- all non-ascii characters are converted to "_" (underscore), including "."
	- all glyphnames which are too long are truncated and a hash is added at the end
	- the hash is generated from the whole glyphname
	- finally, the candidate glyphname is checked against the contents.plist
	and a incrementing number is added at the end if there is a clash.
	"""
	import binascii, struct, string
	ext = ".glif"
	ok = string.ascii_letters + string.digits + " _"
	h = binascii.hexlify(struct.pack(">l", binascii.crc32(glyphName)))
	n = ''
	for c in glyphName:
		if c in ok:
			if c != c.lower():
				n += c + "_"
			else:
				n += c
		else:
			n += "_"
	if len(n + ext) < MAXLEN:
		return n + ext
	count = 0
	candidate = n[:MAXLEN - len(h + ext)] + h + ext
	if glyphSet is not None:
		names = glyphSet.getReverseContents()
		while candidate.lower() in names:
			candidate = n[:MAXLEN - len(h + ext + str(count))] + h + str(count) + ext
			count += 1
	return candidate
