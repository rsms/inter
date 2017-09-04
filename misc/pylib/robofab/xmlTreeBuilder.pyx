import os
try:
	from xml.parsers.expat import ParserCreate
except ImportError:
	_haveExpat = 0
	from xml.parsers.xmlproc.xmlproc import XMLProcessor
else:
	_haveExpat = 1


class XMLParser:

	def __init__(self):
		self.root = []
		self.current = (self.root, None)

	def getRoot(self):
		assert len(self.root) == 1
		return self.root[0]

	def startElementHandler(self, name, attrs):
		children = []
		self.current = (children, name, attrs, self.current)

	def endElementHandler(self, name):
		children, name, attrs, previous = self.current
		previous[0].append((name, attrs, children))
		self.current = previous

	def characterDataHandler(self, data):
		nodes = self.current[0]
		if nodes and type(nodes[-1]) == type(data):
			nodes[-1] = nodes[-1] + data
		else:
			nodes.append(data)

	def _expatParseFile(self, pathOrFile):
		parser = ParserCreate()
		parser.returns_unicode = 0  # XXX, Don't remember why. It sucks, though.
		parser.StartElementHandler = self.startElementHandler
		parser.EndElementHandler = self.endElementHandler
		parser.CharacterDataHandler = self.characterDataHandler
		if isinstance(pathOrFile, (str, unicode)):
			f = open(pathOrFile)
			didOpen = 1
		else:
			didOpen = 0
			f = pathOrFile
		parser.ParseFile(f)
		if didOpen:
			f.close()
		return self.getRoot()

	def _xmlprocDataHandler(self, data, begin, end):
		self.characterDataHandler(data[begin:end])

	def _xmlprocParseFile(self, pathOrFile):
		proc = XMLProcessor()
		proc.app.handle_start_tag = self.startElementHandler
		proc.app.handle_end_tag = self.endElementHandler
		proc.app.handle_data = self._xmlprocDataHandler
		if isinstance(pathOrFile, (str, unicode)):
			f = open(pathOrFile)
			didOpen = 1
		else:
			didOpen = 0
			f = pathOrFile
		proc.parseStart()
		proc.read_from(f)
		proc.flush()
		proc.parseEnd()
		proc.deref()
		if didOpen:
			f.close()
		return self.getRoot()

	if _haveExpat:
		parseFile = _expatParseFile
	else:
		parseFile = _xmlprocParseFile


def stripCharacterData(nodes, recursive=True):
	i = 0
	while 1:
		try:
			node = nodes[i]
		except IndexError:
			break
		if isinstance(node, tuple):
			if recursive:
				stripCharacterData(node[2])
			i = i + 1
		else:
			node = node.strip()
			if node:
				nodes[i] = node
				i = i + 1
			else:
				del nodes[i]


def buildTree(pathOrFile, stripData=1):
	parser = XMLParser()
	tree = parser.parseFile(pathOrFile)
	if stripData:
		stripCharacterData(tree[2])
	return tree


if __name__ == "__main__":
	from pprint import pprint
	import sys
	strip = bool(sys.argv[2:])
	tree = buildTree(sys.argv[1], strip)
	pprint(tree)
