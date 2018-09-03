
def parseFeaList(s):
  v = []
  for e in s.split(' '):
    if e.find('-') != -1:
      (a,b) = e.split('-')
      #print 'split: %s, %s' % (a,chr(ord(a)+1))
      i = ord(a)
      end = ord(b)+1
      while i < end:
        v.append(chr(i))
        i += 1
    else:
      v.append(e)
  return v

UC_ROMAN = parseFeaList('A-Z AE AEacute Aacute Abreve Acircumflex Adieresis Agrave Alpha Alphatonos Amacron Aogonek Aogonek.NAV Aring Aringacute Atilde Beta Cacute Ccaron Ccedilla Ccircumflex Chi Dcaron Dcroat Delta Eacute Ebreve Ecaron Ecircumflex Edieresis Edotaccent Egrave Emacron Eng Eogonek Eogonek.NAV Epsilon Epsilontonos Eta Etatonos Eth Gamma Gbreve Gcircumflex Gcommaaccent Germandbls Hbar Hcircumflex IJ Iacute Ibreve Icircumflex Idieresis Igrave Imacron Iogonek Iota Iotadieresis Iotatonos Itilde Jcircumflex Kappa Kcommaaccent Lacute Lambda Lcaron Lcommaaccent Ldot Lslash Nacute Ncaron Ncommaaccent Ntilde Nu OE Oacute Obreve Ocircumflex Odieresis Ograve Ohungarumlaut Omacron Omega Omegatonos Omicron Omicrontonos Oogonek Oogonek.NAV Oslash Oslashacute Otilde Phi Pi Psi Racute Rcaron Rcommaaccent Rho Sacute Scaron Scedilla Scircumflex Sigma Tau Tbar Tcaron Theta Thorn Uacute Ubreve Ucircumflex Udieresis Ugrave Uhungarumlaut Umacron Uogonek Upsilon Upsilondieresis Upsilontonos Uring Utilde Wacute Wcircumflex Wdieresis Wgrave Xi Yacute Ycircumflex Ydieresis Ygrave Zacute Zcaron Zdotaccent Zeta ampersand uni010A uni0120 uni0162 uni0218 uni021A uni037F')
LC_ROMAN = parseFeaList('a-z ae aeacute aacute abreve acircumflex adieresis agrave alpha alphatonos amacron aogonek aogonek.NAV aring aringacute atilde beta cacute ccaron ccedilla ccircumflex chi dcaron dcroat delta eacute ebreve ecaron ecircumflex edieresis edotaccent egrave emacron eng eogonek eogonek.NAV epsilon epsilontonos eta etatonos eth gamma gbreve gcircumflex gcommaaccent germandbls hbar hcircumflex ij iacute ibreve icircumflex idieresis igrave imacron iogonek iota iotadieresis iotatonos itilde jcircumflex kappa kcommaaccent lacute lambda lcaron lcommaaccent ldot lslash nacute ncaron ncommaaccent ntilde nu oe oacute obreve ocircumflex odieresis ograve ohungarumlaut omacron omega omegatonos omicron omicrontonos oogonek oogonek.NAV oslash oslashacute otilde phi pi psi racute rcaron rcommaaccent rho sacute scaron scedilla scircumflex sigma tau tbar tcaron theta thorn uacute ubreve ucircumflex udieresis ugrave uhungarumlaut umacron uogonek upsilon upsilondieresis upsilontonos uring utilde wacute wcircumflex wdieresis wgrave xi yacute ycircumflex ydieresis ygrave zacute zcaron zdotaccent zeta ampersand uni010B uni0121 uni0163 uni0219 uni021B uni03F3')

UC_AF = parseFeaList('A-F')
LC_AF = parseFeaList('a-f')

LNUM  = parseFeaList('zero one two three four five six seven eight nine')

HEXNUM = LNUM + UC_AF + LC_AF
ALL    = UC_ROMAN + LC_ROMAN + LNUM

glyphs = HEXNUM
for g in glyphs:
  print '  <key>%s</key><dict>' % g
  for g in glyphs:
    print '    <key>%s</key><integer>-256</integer>' % g
  print '  </dict>'

# print ', '.join(LC_ROMAN)


