"""A bunch of stuff useful for glyph name comparisons and such.

1. A group of sorted glyph name lists that can be called directly:
2. Some tools to work with glyph names to do things like build control strings."""

import string

######################################################
# THE LISTS
######################################################

uppercase_plain = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AE', 'OE', 'Oslash', 'Thorn', 'Eth',]

uppercase_accents = ['Aacute', 'Abreve', 'Acaron', 'Acircumflex', 'Adblgrave', 'Adieresis', 'Agrave', 'Amacron', 'Aogonek', 'Aring', 'Aringacute', 'Atilde', 'Bdotaccent', 'Cacute', 'Ccaron', 'Ccircumflex', 'Cdotaccent', 'Dcaron', 'Dcedilla', 'Ddotaccent', 'Eacute', 'Ebreve', 'Ecaron', 'Ecircumflex', 'Edblgrave', 'Edieresis', 'Edotaccent', 'Egrave', 'Emacron', 'Eogonek', 'Etilde', 'Fdotaccent', 'Gacute', 'Gbreve', 'Gcaron', 'Gcedilla', 'Gcircumflex', 'Gcommaaccent', 'Gdotaccent', 'Gmacron', 'Hcedilla', 'Hcircumflex', 'Hdieresis', 'Hdotaccent', 'Iacute', 'Ibreve', 'Icaron', 'Icircumflex', 'Idblgrave', 'Idieresis', 'Idieresisacute', 'Idieresisacute', 'Idotaccent', 'Igrave', 'Imacron', 'Iogonek', 'Itilde', 'Jcircumflex', 'Kacute', 'Kcaron', 'Kcedilla', 'Kcommaaccent', 'Lacute', 'Lcaron', 'Lcedilla', 'Lcommaaccent', 'Ldotaccent', 'Macute', 'Mdotaccent', 'Nacute', 'Ncaron', 'Ncedilla', 'Ncommaaccent', 'Ndotaccent', 'Ntilde', 'Oacute', 'Obreve', 'Ocaron', 'Ocircumflex', 'Odblgrave', 'Odieresis', 'Ograve', 'Ohorn', 'Ohungarumlaut', 'Omacron', 'Oogonek', 'Otilde', 'Pacute', 'Pdotaccent', 'Racute', 'Rcaron', 'Rcedilla', 'Rcommaaccent', 'Rdblgrave', 'Rdotaccent', 'Sacute', 'Scaron', 'Scedilla', 'Scircumflex', 'Scommaaccent', 'Sdotaccent', 'Tcaron', 'Tcedilla', 'Tcommaaccent', 'Tdotaccent', 'Uacute', 'Ubreve', 'Ucaron', 'Ucircumflex', 'Udblgrave', 'Udieresis', 'Udieresisacute', 'Udieresisacute', 'Udieresisgrave', 'Udieresisgrave', 'Ugrave', 'Uhorn', 'Uhungarumlaut', 'Umacron', 'Uogonek', 'Uring', 'Utilde', 'Vtilde', 'Wacute', 'Wcircumflex', 'Wdieresis', 'Wdotaccent', 'Wgrave', 'Xdieresis', 'Xdotaccent', 'Yacute', 'Ycircumflex', 'Ydieresis', 'Ydotaccent', 'Ygrave', 'Ytilde', 'Zacute', 'Zcaron', 'Zcircumflex', 'Zdotaccent', 'AEacute', 'Ccedilla', 'Oslashacute', 'Ldot']

uppercase_special_accents = ['Dcroat', 'Lslash', 'Hbar', 'Tbar', 'LL', 'Eng']

uppercase_ligatures = ['IJ']

uppercase = uppercase_plain+uppercase_accents+uppercase_special_accents+uppercase_ligatures

lowercase_plain = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'dotlessi', 'dotlessj', 'ae', 'oe', 'oslash', 'thorn', 'eth', 'germandbls',  'longs',]

lowercase_accents = ['aacute', 'abreve', 'acaron', 'acircumflex', 'adblgrave', 'adieresis', 'agrave', 'amacron', 'aogonek', 'aring', 'aringacute', 'atilde', 'bdotaccent', 'cacute', 'ccaron', 'ccircumflex', 'cdotaccent', 'dcaron', 'dcedilla', 'ddotaccent', 'dmacron', 'eacute', 'ebreve', 'ecaron', 'ecircumflex', 'edblgrave', 'edieresis', 'edotaccent', 'egrave', 'emacron', 'eogonek', 'etilde', 'fdotaccent', 'gacute', 'gbreve', 'gcaron', 'gcedilla', 'gcircumflex', 'gcommaaccent', 'gdotaccent', 'gmacron', 'hcedilla', 'hcircumflex', 'hdieresis', 'hdotaccent', 'iacute', 'ibreve', 'icaron', 'icircumflex', 'idblgrave', 'idieresis', 'idieresisacute', 'idieresisacute', 'igrave', 'imacron', 'iogonek', 'itilde', 'jcaron', 'jcircumflex', 'kacute', 'kcaron', 'kcedilla', 'kcommaaccent', 'lacute', 'lcaron', 'lcedilla', 'lcommaaccent', 'ldotaccent', 'macute', 'mdotaccent', 'nacute', 'ncaron', 'ncedilla', 'ncommaaccent', 'ndotaccent', 'ntilde', 'oacute', 'obreve', 'ocaron', 'ocircumflex', 'odblgrave', 'odieresis', 'ograve', 'ohorn', 'ohungarumlaut', 'omacron', 'oogonek', 'otilde', 'pacute', 'pdotaccent', 'racute', 'rcaron', 'rcedilla', 'rcommaaccent', 'rdblgrave', 'rdotaccent', 'sacute', 'scaron', 'scedilla', 'scircumflex', 'scommaaccent', 'sdotaccent', 'tcaron', 'tcedilla', 'tcommaaccent', 'tdieresis', 'tdotaccent', 'uacute', 'ubreve', 'ucaron', 'ucircumflex', 'udblgrave', 'udieresis', 'udieresisacute', 'udieresisacute', 'udieresisgrave', 'udieresisgrave', 'ugrave', 'uhorn', 'uhungarumlaut', 'umacron', 'uogonek', 'uring', 'utilde', 'vtilde', 'wacute', 'wcircumflex', 'wdieresis', 'wdotaccent', 'wgrave', 'wring', 'xdieresis', 'xdotaccent', 'yacute', 'ycircumflex', 'ydieresis', 'ydotaccent', 'ygrave', 'yring', 'ytilde', 'zacute', 'zcaron', 'zcircumflex', 'zdotaccent', 'aeacute', 'ccedilla', 'oslashacute', 'ldot', ]

lowercase_special_accents = ['dcroat', 'lslash', 'hbar', 'tbar', 'kgreenlandic', 'longs', 'll', 'eng']

lowercase_ligatures = ['fi', 'fl', 'ff', 'ffi', 'ffl', 'ij']

lowercase = lowercase_plain+lowercase_accents+lowercase_special_accents+lowercase_ligatures

smallcaps_plain = ['A.sc', 'B.sc', 'C.sc', 'D.sc', 'E.sc', 'F.sc', 'G.sc', 'H.sc', 'I.sc', 'J.sc', 'K.sc', 'L.sc', 'M.sc', 'N.sc', 'O.sc', 'P.sc', 'Q.sc', 'R.sc', 'S.sc', 'T.sc', 'U.sc', 'V.sc', 'W.sc', 'X.sc', 'Y.sc', 'Z.sc', 'AE.sc', 'OE.sc', 'Oslash.sc', 'Thorn.sc', 'Eth.sc', ]

smallcaps_accents = ['Aacute.sc', 'Acircumflex.sc', 'Adieresis.sc', 'Agrave.sc', 'Aring.sc', 'Atilde.sc', 'Ccedilla.sc', 'Eacute.sc', 'Ecircumflex.sc', 'Edieresis.sc', 'Egrave.sc', 'Iacute.sc', 'Icircumflex.sc', 'Idieresis.sc', 'Igrave.sc', 'Ntilde.sc', 'Oacute.sc', 'Ocircumflex.sc', 'Odieresis.sc', 'Ograve.sc', 'Otilde.sc', 'Scaron.sc', 'Uacute.sc', 'Ucircumflex.sc', 'Udieresis.sc', 'Ugrave.sc', 'Yacute.sc', 'Ydieresis.sc', 'Zcaron.sc',  'Ccedilla.sc', 'Lslash.sc', ]

smallcaps_special_accents = ['Dcroat.sc', 'Lslash.sc', 'Hbar.sc', 'Tbar.sc', 'LL.sc', 'Eng.sc']

smallcaps_ligatures = ['IJ.sc']

smallcaps = smallcaps_plain + smallcaps_accents + smallcaps_special_accents + smallcaps_ligatures

all_accents = uppercase_accents + uppercase_special_accents + lowercase_accents +lowercase_special_accents + smallcaps_accents + smallcaps_special_accents

digits = ['one', 'onefitted', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero']

digits_oldstyle = ['eight.oldstyle', 'five.oldstyle', 'four.oldstyle', 'nine.oldstyle', 'one.oldstyle', 'seven.oldstyle', 'six.oldstyle', 'three.oldstyle', 'two.oldstyle', 'zero.oldstyle']

digits_superior = ['eight.superior', 'five.superior', 'four.superior', 'nine.superior', 'one.superior', 'seven.superior', 'six.superior', 'three.superior', 'two.superior', 'zero.superior']

digits_inferior = ['eight.inferior', 'five.inferior', 'four.inferior', 'nine.inferior', 'one.inferior', 'seven.inferior', 'three.inferior', 'two.inferior', 'zero.inferior']

fractions = ['oneeighth', 'threeeighths', 'fiveeighths', 'seveneighths', 'onequarter', 'threequarters', 'onethird', 'twothirds', 'onehalf']

currency = ['dollar', 'cent', 'currency', 'Euro', 'sterling', 'yen', 'florin', 'franc', 'lira']

currency_oldstyle = ['cent.oldstyle', 'dollar.oldstyle']

currency_superior = ['cent.superior', 'dollar.superior']

currency_inferior = ['cent.inferior', 'dollar.inferior']

inferior = ['eight.inferior', 'five.inferior', 'four.inferior', 'nine.inferior', 'one.inferior', 'seven.inferior', 'three.inferior', 'two.inferior', 'zero.inferior', 'cent.inferior', 'dollar.inferior', 'comma.inferior', 'hyphen.inferior', 'parenleft.inferior', 'parenright.inferior', 'period.inferior']

superior = ['eight.superior', 'five.superior', 'four.superior', 'nine.superior', 'one.superior', 'seven.superior', 'six.superior', 'three.superior', 'two.superior', 'zero.superior', 'cent.superior', 'dollar.superior', 'Rsmallinverted.superior', 'a.superior', 'b.superior', 'comma.superior', 'd.superior', 'equal.superior', 'e.superior', 'glottalstopreversed.superior', 'hhook.superior', 'h.superior', 'hyphen.superior', 'i.superior', 'j.superior', 'l.superior', 'm.superior', 'n.superior', 'o.superior', 'parenleft.superior', 'parenright.superior', 'period.superior', 'plus.superior', 'r.superior', 'rturned.superior', 's.superior', 't.superior', 'w.superior', 'x.superior', 'y.superior']

accents = ['acute', 'acutecomb', 'breve', 'caron', 'cedilla', 'circumflex', 'commaaccent', 'dblgrave', 'dieresis', 'dieresisacute', 'dieresisacute', 'dieresisgrave', 'dieresisgrave', 'dotaccent', 'grave', 'dblgrave', 'gravecomb', 'hungarumlaut', 'macron', 'ogonek', 'ring', 'ringacute', 'tilde', 'tildecomb', 'horn', 'Acute.sc', 'Breve.sc', 'Caron.sc', 'Cedilla.sc', 'Circumflex.sc', 'Dieresis.sc', 'Dotaccent.sc', 'Grave.sc', 'Hungarumlaut.sc', 'Macron.sc', 'Ogonek.sc', 'Ring.sc', 'Tilde.sc']

dashes = ['hyphen', 'endash', 'emdash', 'threequartersemdash', 'underscore', 'underscoredbl', 'figuredash']

legal = ['trademark', 'trademarksans', 'trademarkserif', 'copyright', 'copyrightsans', 'copyrightserif', 'registered', 'registersans', 'registerserif']

ligatures = ['fi', 'fl', 'ff', 'ffi', 'ffl', 'ij', 'IJ']

punctuation = ['period', 'periodcentered', 'comma', 'colon', 'semicolon', 'ellipsis', 'exclam', 'exclamdown', 'exclamdbl', 'question', 'questiondown']

numerical = ['percent', 'perthousand', 'infinity', 'numbersign', 'degree', 'colonmonetary', 'dotmath']

slashes = ['slash', 'backslash', 'bar', 'brokenbar', 'fraction']

special = ['ampersand', 'paragraph', 'section', 'bullet', 'dagger', 'daggerdbl', 'asterisk', 'at', 'asciicircum', 'asciitilde']


dependencies = 	{
	'A': ['Aacute', 'Abreve', 'Acaron', 'Acircumflex', 'Adblgrave', 'Adieresis', 'Agrave', 'Amacron', 'Aogonek', 'Aring', 'Aringacute', 'Atilde'], 
	'B': ['Bdotaccent'], 
	'C': ['Cacute', 'Ccaron', 'Ccircumflex', 'Cdotaccent', 'Ccedilla'],
	'D': ['Dcaron', 'Dcedilla', 'Ddotaccent'], 
	'E': ['Eacute', 'Ebreve', 'Ecaron', 'Ecircumflex', 'Edblgrave', 'Edieresis', 'Edotaccent', 'Egrave', 'Emacron', 'Eogonek', 'Etilde'], 
	'F': ['Fdotaccent'], 
	'G': ['Gacute', 'Gbreve', 'Gcaron', 'Gcedilla', 'Gcircumflex', 'Gcommaaccent', 'Gdotaccent', 'Gmacron'], 
	'H': ['Hcedilla', 'Hcircumflex', 'Hdieresis', 'Hdotaccent'], 
	'I': ['Iacute', 'Ibreve', 'Icaron', 'Icircumflex', 'Idblgrave', 'Idieresis', 'Idieresisacute', 'Idieresisacute', 'Idotaccent', 'Igrave', 'Imacron', 'Iogonek', 'Itilde'], 
	'J': ['Jcircumflex'], 
	'K': ['Kacute', 'Kcaron', 'Kcedilla', 'Kcommaaccent'], 
	'L': ['Lacute', 'Lcaron', 'Lcedilla', 'Lcommaaccent', 'Ldotaccent', 'Ldot'],
	'M': ['Macute', 'Mdotaccent'], 
	'N': ['Nacute', 'Ncaron', 'Ncedilla', 'Ncommaaccent', 'Ndotaccent', 'Ntilde'], 
	'O': ['Oacute', 'Obreve', 'Ocaron', 'Ocircumflex', 'Odblgrave', 'Odieresis', 'Ograve', 'Ohorn', 'Ohungarumlaut', 'Omacron', 'Oogonek', 'Otilde'], 
	'P': ['Pacute', 'Pdotaccent'], 
	'R': ['Racute', 'Rcaron', 'Rcedilla', 'Rcommaaccent', 'Rdblgrave', 'Rdotaccent'], 
	'S': ['Sacute', 'Scaron', 'Scedilla', 'Scircumflex', 'Scommaaccent', 'Sdotaccent'], 
	'T': ['Tcaron', 'Tcedilla', 'Tcommaaccent', 'Tdotaccent'], 
	'U': ['Uacute', 'Ubreve', 'Ucaron', 'Ucircumflex', 'Udblgrave', 'Udieresis', 'Udieresisacute', 'Udieresisacute', 'Udieresisgrave', 'Udieresisgrave', 'Ugrave', 'Uhorn', 'Uhungarumlaut', 'Umacron', 'Uogonek', 'Uring', 'Utilde'], 
	'V': ['Vtilde'], 
	'W': ['Wacute', 'Wcircumflex', 'Wdieresis', 'Wdotaccent', 'Wgrave'], 
	'X': ['Xdieresis', 'Xdotaccent'], 
	'Y': ['Yacute', 'Ycircumflex', 'Ydieresis', 'Ydotaccent', 'Ygrave', 'Ytilde'], 
	'Z': ['Zacute', 'Zcaron', 'Zcircumflex', 'Zdotaccent'], 
	'AE': ['AEacute'],  
	'Oslash': ['Oslashacute'], 
	
	'a': ['aacute', 'abreve', 'acaron', 'acircumflex', 'adblgrave', 'adieresis', 'agrave', 'amacron', 'aogonek', 'aring', 'aringacute', 'atilde'],
	'b': ['bdotaccent'], 
	'c': ['cacute', 'ccaron', 'ccircumflex', 'cdotaccent', 'ccedilla'], 
	'd': ['dcaron', 'dcedilla', 'ddotaccent', 'dmacron'], 
	'e': ['eacute', 'ebreve', 'ecaron', 'ecircumflex', 'edblgrave', 'edieresis', 'edotaccent', 'egrave', 'emacron', 'eogonek', 'etilde'], 
	'f': ['fdotaccent'], 
	'g': ['gacute', 'gbreve', 'gcaron', 'gcedilla', 'gcircumflex', 'gcommaaccent', 'gdotaccent', 'gmacron'], 
	'h': ['hcedilla', 'hcircumflex', 'hdieresis', 'hdotaccent'], 
	'i': ['iacute', 'ibreve', 'icaron', 'icircumflex', 'idblgrave', 'idieresis', 'idieresisacute', 'idieresisacute', 'igrave', 'imacron', 'iogonek', 'itilde'], 
	'j': ['jcaron', 'jcircumflex'], 
	'k': ['kacute', 'kcaron', 'kcedilla', 'kcommaaccent'], 
	'l': ['lacute', 'lcaron', 'lcedilla', 'lcommaaccent', 'ldotaccent', 'ldot'], 
	'm': ['macute', 'mdotaccent'], 
	'n': ['nacute', 'ncaron', 'ncedilla', 'ncommaaccent', 'ndotaccent', 'ntilde'], 
	'o': ['oacute', 'obreve', 'ocaron', 'ocircumflex', 'odblgrave', 'odieresis', 'ograve', 'ohorn', 'ohungarumlaut', 'omacron', 'oogonek', 'otilde'], 
	'p': ['pacute', 'pdotaccent'], 
	'r': ['racute', 'rcaron', 'rcedilla', 'rcommaaccent', 'rdblgrave', 'rdotaccent'], 
	's': ['sacute', 'scaron', 'scedilla', 'scircumflex', 'scommaaccent', 'sdotaccent'], 
	't': ['tcaron', 'tcedilla', 'tcommaaccent', 'tdieresis', 'tdotaccent'], 
	'u': ['uacute', 'ubreve', 'ucaron', 'ucircumflex', 'udblgrave', 'udieresis', 'udieresisacute', 'udieresisacute', 'udieresisgrave', 'udieresisgrave', 'ugrave', 'uhorn', 'uhungarumlaut', 'umacron', 'uogonek', 'uring', 'utilde'], 
	'v': ['vtilde'], 
	'w': ['wacute', 'wcircumflex', 'wdieresis', 'wdotaccent', 'wgrave', 'wring'], 
	'x': ['xdieresis', 'xdotaccent'], 
	'y': ['yacute', 'ycircumflex', 'ydieresis', 'ydotaccent', 'ygrave', 'yring', 'ytilde'], 
	'z': ['zacute', 'zcaron', 'zcircumflex', 'zdotaccent'], 
	'ae': ['aeacute'], 
	'oslash': ['oslashacute'], 
	}
######################################################
# MISC TOOLS
######################################################

def breakSuffix(glyphname):
	"""
	Breaks the glyphname into a two item list
	0: glyphname
	1: suffix
	
	if a suffix is not found it returns None
	"""
	if glyphname.find('.') != -1:
		split = glyphname.split('.')
		return split
	else:
		return None

def findAccentBase(accentglyph):
	"""Return the base glyph of an accented glyph
	for example: Ugrave.sc returns U.sc"""
	base = splitAccent(accentglyph)[0]		
	return base

def splitAccent(accentglyph):
	"""
	Split an accented glyph into a two items
	0: base glyph
	1: accent list
	
	for example: Yacute.scalt45 returns: (Y.scalt45, [acute])
	and: aacutetilde.alt45 returns (a.alt45, [acute, tilde])
	"""
	base = None
	suffix = ''
	accentList=[]
	broken = breakSuffix(accentglyph)
	if broken is not None:
		suffix = broken[1]
		base = broken[0]
	else:
		base=accentglyph
	ogbase=base
	temp_special = lowercase_special_accents + uppercase_special_accents
	if base in lowercase_plain + uppercase_plain + smallcaps_plain:
		pass
	elif base not in temp_special:
		for accent in accents:
			if base.find(accent) != -1:
				base = base.replace(accent, '')
				accentList.append(accent)
		counter={}
		for accent in accentList:
			counter[ogbase.find(accent)] = accent
		counterList = counter.keys()
		counterList.sort()
		finalAccents = []
		for i in counterList:
			finalAccents.append(counter[i])
		accentList = finalAccents
	if len(suffix) != 0:
		base = '.'.join([base, suffix])
	return base, accentList
	
	
######################################################
# UPPER, LOWER, SMALL
######################################################

casedict = 	{
					'germandbls'	:	'S/S', 
					'dotlessi'			:	'I',
					'dotlessj'			:	'J',
					'ae'					:	'AE',
					'aeacute'			:	'AEacute',
					'oe'					:	'OE',
					'll'					:	'LL'
					}
					
casedictflip = 			{}
			
smallcapscasedict =	{
					'germandbls'		:	'S.sc/S.sc',
					'question'			:	'question.sc', 
					'questiondown'	:	'questiondown.sc', 
					'exclam'				:	'exclam.sc', 
					'exclamdown'		:	'exclamdown.sc', 
					'ampersand'		:	'ampersand.sc'
					}

class _InternalCaseFunctions:
	"""internal functions for doing gymnastics with the casedicts"""
	
	def expandsmallcapscasedict(self):
		for i in casedict.values():
			if i not in smallcapscasedict.keys():
				if len(i) > 1:
					if i[:1].upper() == i[:1]:
						smallcapscasedict[i] = i[:1] + i[1:] + '.sc'	
							
		for i in uppercase:
			if i + '.sc' in smallcaps:
				if i not in smallcapscasedict.keys():
					smallcapscasedict[i] = i + '.sc'
					
	def flipcasedict(self):
		for i in casedict.keys():
			if i.find('dotless') != -1:
				i = i.replace('dotless', '')
			casedictflip[casedict[i]] = i
	
	def expandcasedict(self):
		for i in lowercase_ligatures:
			casedict[i] = i.upper()
		for i in lowercase:
			if i not in casedict.keys():
				if string.capitalize(i) in uppercase:
					casedict[i] = string.capitalize(i)


def upper(glyphstring):
	"""Convert all possible characters to uppercase in a glyph string."""
	
	_InternalCaseFunctions().expandcasedict()
	uc = []
	for i in glyphstring.split('/'):	
		if i.find('.sc') != -1:
			if i[-3] != '.sc':
				x = i.replace('.sc', '.')
			else:	
				x = i.replace('.sc', '')
			i = x		
		suffix = ''
		bS = breakSuffix(i)
		if bS is not None:
			suffix = bS[1]
			i = bS[0]
		if i in casedict.keys():
			i = casedict[i]
		if len(suffix) != 0:
			i = '.'.join([i, suffix])
		uc.append(i)
	return '/'.join(uc)
	
def lower(glyphstring):
	"""Convert all possible characters to lowercase in a glyph string."""
	
	_InternalCaseFunctions().expandcasedict()
	_InternalCaseFunctions().flipcasedict()
	lc = []
	for i in glyphstring.split('/'):
		if i.find('.sc') != -1:
			if i[-3] != '.sc':
				x = i.replace('.sc', '.')
			else:	
				x = i.replace('.sc', '')
			i = x
		suffix = ''
		bS = breakSuffix(i)
		if breakSuffix(i) is not None:
			suffix = bS[1]
			i = bS[0]
		if i in casedictflip.keys():
			i = casedictflip[i]
		if len(suffix) != 0:
			i = '.'.join([i, suffix])	
		lc.append(i)
	return '/'.join(lc)
	
def small(glyphstring):
	"""Convert all possible characters to smallcaps in a glyph string."""
	
	_InternalCaseFunctions().expandcasedict()
	_InternalCaseFunctions().expandsmallcapscasedict()
	sc = []
	for i in glyphstring.split('/'):
		suffix = ''
		bS = breakSuffix(i)
		if bS is not None:
			suffix = bS[1]
			if suffix == 'sc':
				suffix = ''
			i = bS[0]
		if i in lowercase:
			if i not in smallcapscasedict.keys():
				i = casedict[i]
		if i in smallcapscasedict.keys():
			i = smallcapscasedict[i]
		if i != 'S.sc/S.sc':
			if len(suffix) != 0:
				if i[-3:] == '.sc':
					i = ''.join([i, suffix])
				else:	
					i = '.'.join([i, suffix])
		sc.append(i)
	return '/'.join(sc)


######################################################
# CONTROL STRING TOOLS
######################################################


controldict = 	{
			'UC'		:	['/H/H', '/H/O/H/O', '/O/O'],
			'LC'		:	['/n/n', '/n/o/n/o', '/o/o'],
			'SC'		:	['/H.sc/H.sc', '/H.sc/O.sc/H.sc/O.sc', '/O.sc/O.sc'],
			'DIGITS'	:	['/one/one', '/one/zero/one/zero', '/zero/zero'],
			}


def controls(glyphname):
	"""Send this a glyph name and get a control string
	with all glyphs separated by slashes."""
	controlslist =	[]
	for value in controldict.values():
		for v in value:
			for i in v.split('/'):
				if len(i) > 0:
					if i not in controlslist:
						controlslist.append(i)	
	cs = ''
	if glyphname in controlslist:
		for key in controldict.keys():
			for v in controldict[key]:
				if glyphname in v.split('/'):
					con = controldict[key]
		striptriple = []
		hold1 = ''
		hold2 = ''
		for i in ''.join(con).split('/'):
			if len(i) != 0:
				if i == hold1 and i == hold2:
					pass
				else:
					striptriple.append(i)
			hold1 = hold2
			hold2 = i
		constr = '/' + '/'.join(striptriple)
		# this is a bit of a hack since FL seems to have trouble 
		# when it encounters the same string more than once.
		# so, let's stick the glyph at the end to differentiate it.
		# for example: HHOHOOH and HHOHOOO
		cs = constr + '/' + glyphname
	else:
		suffix = ''
		bS = breakSuffix(glyphname)
		if bS is not None:
			suffix = bS[1]
			glyphname = bS[0]
		if suffix[:2] == 'sc':
			controls = controldict['SC']
		elif glyphname in uppercase:
			controls = controldict['UC']
		elif glyphname in lowercase:
			controls = controldict['LC']
		elif glyphname in digits:
			controls = controldict['DIGITS']
		else:
			controls = controldict['UC']
		if len(suffix) != 0:
			glyphname = '.'.join([glyphname, suffix])
		cs = controls[0] + '/' + glyphname + controls[1] + '/' + glyphname + controls[2]
	return cs


def sortControlList(list):
	"""Roughly sort a list of control strings."""
		
	controls = []
	for v in controldict.values():
		for w in v:
			for x in w.split('/'):
				if len(x) is not None:
					if x not in controls:
						controls.append(x)
	temp_digits = digits + digits_oldstyle + fractions
	temp_currency = currency + currency_oldstyle
	ss_uppercase = []
	ss_lowercase = [] 
	ss_smallcaps = [] 
	ss_digits = [] 
	ss_currency = [] 
	ss_other = []
	for i in list:
		glyphs = i.split('/')
		c = glyphs[2]
		for glyph in glyphs:
			if len(glyph) is not None:
				if glyph not in controls:
					c = glyph
		if c in uppercase:
			ss_uppercase.append(i)
		elif c in lowercase:
			ss_lowercase.append(i)
		elif c in smallcaps:
			ss_smallcaps.append(i)
		elif c in temp_digits:
			ss_digits.append(i)
		elif c in temp_currency:
			ss_currency.append(i)
		else:
			ss_other.append(i)
	ss_uppercase.sort()
	ss_lowercase.sort()
	ss_smallcaps.sort()
	ss_digits.sort()
	ss_currency.sort()
	ss_other.sort()
	return ss_uppercase + ss_lowercase + ss_smallcaps + ss_digits + ss_currency + ss_other


# under contruction!
kerncontroldict = 	{
				'UC/UC'				:	['/H/H', '/H/O/H/O/O'],
				'UC/LC'				:	['', '/n/n/o/n/e/r/s'],
				'UC/SORTS'			:	['/H/H', '/H/O/H/O/O'],
				'UC/DIGITS'			:	['/H/H', '/H/O/H/O/O'],
				'LC/LC'				:	['/n/n', '/n/o/n/o/o'],
				'LC/SORTS'			:	['/n/n', '/n/o/n/o/o'],
				'LC/DIGITS'			:	['', '/n/n/o/n/e/r/s'],
				'SC/SC'				:	['/H.sc/H.sc', '/H.sc/O.sc/H.sc/O.sc/O.sc'],
				'UC/SC'				:	['', '/H.sc/H.sc/O.sc/H.sc/O.sc/O.sc'],
				'SC/SORTS'			:	['/H.sc/H.sc', '/H.sc/O.sc/H.sc/O.sc/O.sc'],
				'SC/DIGITS'			:	['', '/H.sc/H.sc/O.sc/H.sc/O.sc/O.sc'],
				'DIGITS/DIGITS'	:	['/H/H', '/H/O/H/O/O'],
				'DIGITS/SORTS'	:	['/H/H', '/H/O/H/O/O'],
				'SORTS/SORTS'	:	['/H/H', '/H/O/H/O/O'],
				}

def kernControls(leftglyphname, rightglyphname):
	"""build a control string based on the left glyph and right glyph"""
	
	sorts = currency + accents + dashes + legal + numerical + slashes + special
	
	l = leftglyphname
	r = rightglyphname
	lSuffix = ''
	rSuffix = ''
	bSL = breakSuffix(l)
	if bSL is not None:
		lSuffix = bSL[1]
		l = bSL[0]
	bSR = breakSuffix(r)
	if bSR is not None:
		rSuffix = bSR[1]
		r = bSR[0]
	if lSuffix[:2] == 'sc' or rSuffix[:2] == 'sc':
		if l in uppercase or r in uppercase:
			controls = kerncontroldict['UC/SC']
		elif l in digits or r in digits:
			controls = kerncontroldict['SC/DIGITS']
		elif l in sorts or r in sorts:
			controls = kerncontroldict['SC/SORTS']
		else:
			controls = kerncontroldict['SC/SC']
	elif l in uppercase or r in uppercase:
		if l in lowercase or r in lowercase:
			controls = kerncontroldict['UC/LC']
		elif l in digits or r in digits:
			controls = kerncontroldict['UC/DIGITS']
		elif l in sorts or r in sorts:
			controls = kerncontroldict['UC/SORTS']
		else:
			controls = kerncontroldict['UC/UC']
	elif l in lowercase or r in lowercase:
		if l in uppercase or r in uppercase:
			controls = kerncontroldict['UC/LC']
		elif l in digits or r in digits:
			controls = kerncontroldict['LC/DIGITS']
		elif l in sorts or r in sorts:
			controls = kerncontroldict['LC/SORTS']
		else:
			controls = kerncontroldict['LC/LC']
	elif l in digits or r in digits:
		if l in uppercase or r in uppercase:
			controls = kerncontroldict['UC/DIGITS']
		elif l in lowercase or r in lowercase:
			controls = kerncontroldict['LC/DIGITS']
		elif l in sorts or r in sorts:
			controls = kerncontroldict['DIGITS/SORTS']
		else:
			controls = kerncontroldict['DIGITS/DIGITS']
	elif l in sorts and r in sorts:
		controls = kerncontroldict['SORTS/SORTS']
	else:
		controls = kerncontroldict['UC/UC']
				
	if len(lSuffix) != 0:
		l = '.'.join([l, lSuffix])
	if len(rSuffix) != 0:
		r = '.'.join([r, rSuffix])
	
	cs = controls[0] + '/' + l + '/' + r + controls[1]
	
	return cs
			

######################################################

class _testing:
	def __init__(self):
		print
		print '##### testing!'
	#	self.listtest()
	#	self.accentbasetest()
	#	self.controlstest()
		self.upperlowersmalltest()
	#	self.stringsorttest()
	
	def listtest(self):
		testlist = [
				uppercase, 
				uppercase_accents, 
				lowercase, 
				lowercase_accents, 
				smallcaps, 
				smallcaps_accents, 
				digits, 
				digits_oldstyle, 
				digits_superior, 
				digits_inferior, 
				fractions, 
				currency, 
				currency_oldstyle, 
				currency_superior, 
				currency_inferior, 
				inferior, 
				superior, 
				accents, 
				dashes, 
				legal, 
				ligatures, 
				punctuation,
				numerical, 
				slashes, 
				special
				]
		for i in testlist:
			print i
	
	
	def accentbasetest(self):
		print findAccentBase('Adieresis')
		print findAccentBase('Adieresis.sc')
		print findAccentBase('Thorn.sc')
		print findAccentBase('notaralglyphname')
		
			
	def controlstest(self):
		print kernControls('A', 'a.swash')
		print kernControls('A.sc', '1')
		print kernControls('bracket.sc', 'germandbls')
		print kernControls('2', 'X')
		print kernControls('Y', 'X')
		print kernControls('Y.alt', 'X')
		print kernControls('Y.scalt', 'X')
		#print controls('x')
		#print controls('germandbls')
		#print controls('L')
		#print controls('L.sc')
		#print controls('Z.sc')
		#print controls('seven')
		#print controls('question')
		#print controls('unknown')
		
	def upperlowersmalltest(self):
		u = upper('/H/i/Z.sc/ampersand.sc/dotlessi/germandbls/four.superior/LL')
		l = lower('/H/I/Z.sc/ampersand.sc/dotlessi/germandbls/four.superior/LL')
		s = small('/H/i/Z.sc/ampersand.alt/dotlessi/germandbls/four.superior/LL')
		print u
		print l
		print s
		print lower(u)
		print upper(l)
		print upper(s)
		print lower(s)
		
	def stringsorttest(self):
		sample = "/H/H/Euro/H/O/H/O/Euro/O/O /H/H/R/H/O/H/O/R/O/O /H/H/question/H/O/H/O/question/O/O /H/H/sterling/H/O/H/O/sterling/O/O /n/n/r/n/o/n/o/r/o/o"
		list = string.split(sample, ' ')
		x = sortControlList(list)	
		print x

if __name__ == '__main__':
	_testing()