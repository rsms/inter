import sys, os, os.path, argparse, re
from fontTools.ttLib import TTFont

# Adoptation of fonttools/blob/master/Snippets/rename-fonts.py

WINDOWS_ENGLISH_IDS = 3, 1, 0x409
MAC_ROMAN_IDS = 1, 0, 0

LEGACY_FAMILY       = 1
SUBFAMILY_NAME      = 2
TRUETYPE_UNIQUE_ID  = 3
FULL_NAME           = 4
POSTSCRIPT_NAME     = 6
PREFERRED_FAMILY    = 16
TYPO_SUBFAMILY_NAME = 17
WWS_FAMILY          = 21
VAR_PS_NAME_PREFIX  = 25


FAMILY_RELATED_IDS = set([
  LEGACY_FAMILY,
  TRUETYPE_UNIQUE_ID,
  FULL_NAME,
  POSTSCRIPT_NAME,
  PREFERRED_FAMILY,
  WWS_FAMILY,
  VAR_PS_NAME_PREFIX,
])

whitespace_re = re.compile(r'\s+')


def remove_whitespace(s):
  return whitespace_re.sub('', s)


def normalize_whitespace(s):
  return whitespace_re.sub(' ', s)


def remove_substring(s, substr):
  # examples of remove_substring(s, "Display"):
  #   "Inter Display"   => "Inter"
  #   "Display Lol"     => "Lol"
  #   "Foo Display Lol" => "Foo Lol"
  #   " Foo   Bar Lol " => "Foo Bar Lol"
  return normalize_whitespace(s.strip().replace(substr, '')).strip()


def set_full_name(font, fullName, fullNamePs):
  nameTable = font["name"]
  nameTable.setName(fullName, FULL_NAME, 1, 0, 0)     # mac
  nameTable.setName(fullName, FULL_NAME, 3, 1, 0x409) # windows
  nameTable.setName(fullNamePs, POSTSCRIPT_NAME, 1, 0, 0)     # mac
  nameTable.setName(fullNamePs, POSTSCRIPT_NAME, 3, 1, 0x409) # windows


def getFamilyName(font):
  nameTable = font["name"]
  r = None
  for plat_id, enc_id, lang_id in (WINDOWS_ENGLISH_IDS, MAC_ROMAN_IDS):
    for name_id in (PREFERRED_FAMILY, LEGACY_FAMILY):
      r = nameTable.getName(nameID=name_id, platformID=plat_id, platEncID=enc_id, langID=lang_id)
      if r is not None:
        break
    if r is not None:
      break
  if not r:
    raise ValueError("family name not found")
  return r.toUnicode()


def getFamilyNames(font):
  nameTable = font["name"]
  r = None
  names = dict()  # dict in Py >=3.7 maintains insertion order
  for plat_id, enc_id, lang_id in (WINDOWS_ENGLISH_IDS, MAC_ROMAN_IDS):
    for name_id in (PREFERRED_FAMILY, LEGACY_FAMILY):
      r = nameTable.getName(
        nameID=name_id, platformID=plat_id, platEncID=enc_id, langID=lang_id)
      if r:
        names[r.toUnicode()] = True
  if len(names) == 0:
    raise ValueError("family name not found")
  names = list(names.keys())
  names.sort()
  names.reverse() # longest first
  return names


def getStyleName(font):
  nameTable = font["name"]
  for plat_id, enc_id, lang_id in (WINDOWS_ENGLISH_IDS, MAC_ROMAN_IDS):
    for name_id in (TYPO_SUBFAMILY_NAME, SUBFAMILY_NAME):
      r = nameTable.getName(
        nameID=name_id, platformID=plat_id, platEncID=enc_id, langID=lang_id)
      if r is not None:
        return r.toUnicode()
  raise ValueError("style name not found")


def renameStylesGoogleFonts(font):
  familyName = getFamilyName(font)

  # collect subfamily (style) name IDs for variable font's named instances
  vfInstanceSubfamilyNameIds = set()
  if "fvar" in font:
    for namedInstance in font["fvar"].instances:
      vfInstanceSubfamilyNameIds.add(namedInstance.subfamilyNameID)

  nameTable = font["name"]
  for rec in nameTable.names:
    rid = rec.nameID
    if rid in (FULL_NAME, LEGACY_FAMILY):
      # style part of family name
      s = rec.toUnicode()
      start = s.find(familyName)
      if start != -1:
        s = familyName + " " + remove_whitespace(s[start + len(familyName):])
      else:
        s = remove_whitespace(s)
      if s != "Italic" and s.endswith("Italic"):
        # fixup e.g. "ExtraBoldItalic" -> "ExtraBold Italic"
        s = s[:len(s) - len("Italic")] + " Italic"
      rec.string = s.strip()
    if rid in (SUBFAMILY_NAME, TYPO_SUBFAMILY_NAME) or rid in vfInstanceSubfamilyNameIds:
      s = remove_whitespace(rec.toUnicode())
      if s != "Italic" and s.endswith("Italic"):
        # fixup e.g. "ExtraBoldItalic" -> "ExtraBold Italic"
        s = s[:len(s) - len("Italic")] + " Italic"
      rec.string = s.strip()
    # else: ignore standard names unrelated to style


def setStyleName(font, newStyleName):
  newFullName = getFamilyName(font).strip()
  if newStyleName != 'Regular':
    newFullName += " " + newStyleName
  newFullNamePs = remove_whitespace(newFullName)
  set_full_name(font, newFullName, newFullNamePs)

  nameTable = font["name"]
  for rec in nameTable.names:
    rid = rec.nameID
    if rid in (SUBFAMILY_NAME, TYPO_SUBFAMILY_NAME):
      rec.string = newStyleName


def setFamilyName(font, nextFamilyName):
  prevFamilyNames = getFamilyNames(font)
  # if prevFamilyNames[0] == nextFamilyName:
  #   return
  #   # raise Exception("identical family name")

  def renameRecord(nameRecord, prevFamilyNames, nextFamilyName):
    # replaces prevFamilyNames with nextFamilyName in nameRecord
    s = nameRecord.toUnicode()
    for prevFamilyName in prevFamilyNames:
      start = s.find(prevFamilyName)
      if start == -1:
        continue
      end = start + len(prevFamilyName)
      nextFamilyName = s[:start] + nextFamilyName + s[end:]
      nameRecord.string = nextFamilyName
      break
    return s, nextFamilyName

  # postcript name can't contain spaces
  psPrevFamilyNames = []
  for s in prevFamilyNames:
    s = s.strip()
    if s.find(' ') == -1:
      psPrevFamilyNames.append(s)
    else:
      # Foo Bar Baz -> FooBarBaz
      psPrevFamilyNames.append(s.replace(" ", ""))
      # # Foo Bar Baz -> FooBar-Baz
      p = s.rfind(' ')
      s = s[:p] + '-' + s[p+1:]
      psPrevFamilyNames.append(s)

  psNextFamilyName = nextFamilyName.replace(" ", "")
  found_VAR_PS_NAME_PREFIX = False
  nameTable = font["name"]

  for rec in nameTable.names:
    name_id = rec.nameID
    if name_id not in FAMILY_RELATED_IDS:
      # leave uninteresting records unmodified
      continue
    if name_id == POSTSCRIPT_NAME:
      old, new = renameRecord(rec, psPrevFamilyNames, psNextFamilyName)
    elif name_id == TRUETYPE_UNIQUE_ID:
      # The Truetype Unique ID rec may contain either the PostScript Name
      # or the Full Name
      prev_psname = None
      for s in psPrevFamilyNames:
        if s in rec.toUnicode():
          prev_psname = s
          break
      if prev_psname is not None:
        # Note: This is flawed -- a font called "Foo" renamed to "Bar Lol";
        # if this record is not a PS record, it will incorrectly be rename "BarLol".
        # However, in practice this is not a big deal since it's just an ID.
        old, new = renameRecord(rec, [prev_psname], psNextFamilyName)
      else:
        old, new = renameRecord(rec, prevFamilyNames, nextFamilyName)
    elif name_id == VAR_PS_NAME_PREFIX:
      # Variations PostScript Name Prefix.
      # If present in a variable font, it may be used as the family prefix in the
      # PostScript Name Generation for Variation Fonts algorithm.
      # The character set is restricted to ASCII-range uppercase Latin letters,
      # lowercase Latin letters, and digits.
      found_VAR_PS_NAME_PREFIX = True
      old, new = renameRecord(rec, prevFamilyNames, nextFamilyName)
    else:
      old, new = renameRecord(rec, prevFamilyNames, nextFamilyName)
    # print("  %r: '%s' -> '%s'" % (rec, old, new))

  # HACK! FIXME!
  # add name ID 25 "Variations PostScript Name Prefix" if not found
  if not found_VAR_PS_NAME_PREFIX and nextFamilyName.find('Variable') != -1:
    varPSNamePrefix = remove_whitespace(nextFamilyName)
    nameTable.setName(varPSNamePrefix, VAR_PS_NAME_PREFIX, 1, 0, 0)     # mac
    nameTable.setName(varPSNamePrefix, VAR_PS_NAME_PREFIX, 3, 1, 0x409) # windows


def main():
  argparser = argparse.ArgumentParser(
    description='Rename family and/or styles of font'
  )
  a = lambda *args, **kwargs: argparser.add_argument(*args, **kwargs)
  a('-o', '--output', metavar='<file>',
    help='Output font file. Defaults to input file (overwrite)')
  a('--family', metavar='<name>',
    help='Rename family to <name>')
  a('--style', metavar='<name>',
    help='Rename style to <name>')
  a('--google-style', action='store_true',
    help='Rename style names to Google Fonts standards')
  a('--scrub-display', action='store_true',
    help='Remove "Display" from various family & style records')
  a('input', metavar='<file>',
    help='Input font file')
  args = argparser.parse_args()

  infile = args.input
  outfile = args.output or infile

  font = TTFont(infile, recalcBBoxes=False, recalcTimestamp=False)

  if args.scrub_display:
    if not args.family: # for setFamilyName()
      args.family = remove_substring(getFamilyName(font), "Display")
    if not args.style:
      args.style = remove_substring(getStyleName(font), "Display")
      if args.style == '':
        args.style = 'Regular'

  editCount = 0
  try:
    if args.family:
      setFamilyName(font, args.family)
      editCount += 1

    if args.style:
      setStyleName(font, args.style)
      editCount += 1

    if args.google_style:
      renameStylesGoogleFonts(font)
      editCount += 1

    if editCount == 0:
      print("no rename options provided", file=sys.stderr)
      argparser.print_help(sys.stderr)
      sys.exit(1)
      return

    font.save(outfile)
  finally:
    font.close()


if __name__ == '__main__':
  main()
