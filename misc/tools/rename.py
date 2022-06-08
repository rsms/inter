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


FAMILY_RELATED_IDS = set([
  LEGACY_FAMILY,
  TRUETYPE_UNIQUE_ID,
  FULL_NAME,
  POSTSCRIPT_NAME,
  PREFERRED_FAMILY,
  WWS_FAMILY,
])

whitespace_re = re.compile(r'\s+')


def removeWhitespace(s):
  return whitespace_re.sub("", s)


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
        s = familyName + " " + removeWhitespace(s[start + len(familyName):])
      else:
        s = removeWhitespace(s)
      if s != "Italic" and s.endswith("Italic"):
        # fixup e.g. "ExtraBoldItalic" -> "ExtraBold Italic"
        s = s[:len(s) - len("Italic")] + " Italic"
      rec.string = s.strip()
    if rid in (SUBFAMILY_NAME, TYPO_SUBFAMILY_NAME) or rid in vfInstanceSubfamilyNameIds:
      s = removeWhitespace(rec.toUnicode())
      if s != "Italic" and s.endswith("Italic"):
        # fixup e.g. "ExtraBoldItalic" -> "ExtraBold Italic"
        s = s[:len(s) - len("Italic")] + " Italic"
      rec.string = s.strip()
    # else: ignore standard names unrelated to style


def setStyleName(font, newStyleName):
  newFullName = getFamilyName(font).strip() + " " + newStyleName
  newFullNamePs = removeWhitespace(newFullName)
  set_full_name(font, newFullName, newFullNamePs)

  nameTable = font["name"]
  for rec in nameTable.names:
    rid = rec.nameID
    if rid in (SUBFAMILY_NAME, TYPO_SUBFAMILY_NAME):
      rec.string = newStyleName


def setFamilyName(font, nextFamilyName):
  prevFamilyName = getFamilyName(font)
  if prevFamilyName == nextFamilyName:
    return
    # raise Exception("identical family name")

  def renameRecord(nameRecord, prevFamilyName, nextFamilyName):
    # replaces prevFamilyName with nextFamilyName in nameRecord
    s = nameRecord.toUnicode()
    start = s.find(prevFamilyName)
    if start != -1:
      end = start + len(prevFamilyName)
      nextFamilyName = s[:start] + nextFamilyName + s[end:]
    nameRecord.string = nextFamilyName
    return s, nextFamilyName

  # postcript name can't contain spaces
  psPrevFamilyName = prevFamilyName.replace(" ", "")
  psNextFamilyName = nextFamilyName.replace(" ", "")
  for rec in font["name"].names:
    name_id = rec.nameID
    if name_id not in FAMILY_RELATED_IDS:
      # leave uninteresting records unmodified
      continue
    if name_id == POSTSCRIPT_NAME:
      old, new = renameRecord(rec, psPrevFamilyName, psNextFamilyName)
    elif name_id == TRUETYPE_UNIQUE_ID:
      # The Truetype Unique ID rec may contain either the PostScript Name or the Full Name
      if psPrevFamilyName in rec.toUnicode():
        # Note: This is flawed -- a font called "Foo" renamed to "Bar Lol";
        # if this record is not a PS record, it will incorrectly be rename "BarLol".
        # However, in practice this is not abig deal since it's just an ID.
        old, new = renameRecord(rec, psPrevFamilyName, psNextFamilyName)
      else:
        old, new = renameRecord(rec, prevFamilyName, nextFamilyName)
    else:
      old, new = renameRecord(rec, prevFamilyName, nextFamilyName)
    # print("  %r: '%s' -> '%s'" % (rec, old, new))


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
  a('input', metavar='<file>',
    help='Input font file')
  args = argparser.parse_args()

  infile = args.input
  outfile = args.output or infile

  font = TTFont(infile, recalcBBoxes=False, recalcTimestamp=False)
  editCount = 0
  try:
    if args.family:
      editCount += 1
      setFamilyName(font, args.family)

    if args.style:
      editCount += 1
      setStyleName(font, args.style)

    if args.google_style:
      editCount += 1
      renameStylesGoogleFonts(font)

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
