#!/usr/bin/env python
from fontTools.ttLib import TTFont
import os, sys, re

# Adoptation of fonttools/blob/master/Snippets/rename-fonts.py

WINDOWS_ENGLISH_IDS = 3, 1, 0x409
MAC_ROMAN_IDS = 1, 0, 0

LEGACY_FAMILY      = 1
TRUETYPE_UNIQUE_ID = 3
FULL_NAME          = 4
POSTSCRIPT_NAME    = 6
PREFERRED_FAMILY   = 16
SUBFAMILY_NAME     = 17
WWS_FAMILY         = 21


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


def setFullName(font, fullName):
  nameTable = font["name"]
  nameTable.setName(fullName, FULL_NAME, 1, 0, 0)     # mac
  nameTable.setName(fullName, FULL_NAME, 3, 1, 0x409) # windows


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


def removeWhitespaceFromStyles(font):
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
      rec.string = s
    if rid in (SUBFAMILY_NAME,) or rid in vfInstanceSubfamilyNameIds:
      rec.string = removeWhitespace(rec.toUnicode())
    # else: ignore standard names unrelated to style


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



def loadFont(file):
  return TTFont(file, recalcBBoxes=False, recalcTimestamp=False)


def renameFontFamily(infile, outfile, newFamilyName):
  font = loadFont(infile)
  setFamilyName(font, newFamilyName)
  # print('write "%s"' % outfile)
  font.save(outfile)
  font.close()



def main():
  infile = "./build/fonts/var/Inter.var.ttf"
  outfile = "./build/tmp/var2.otf"
  renameFontFamily(infile, outfile, "Inter V")
  print("%s familyName: %r" % (infile, getFamilyName(loadFont(infile)) ))
  print("%s familyName: %r" % (outfile, getFamilyName(loadFont(outfile)) ))

if __name__ == "__main__":
  sys.exit(main())

# Similar to:
# ttx -i -e -o ./build/tmp/var.ttx ./build/fonts/var/Inter.var.ttf
# ttx -b --no-recalc-timestamp -o ./build/tmp/var.otf ./build/tmp/var.ttx
