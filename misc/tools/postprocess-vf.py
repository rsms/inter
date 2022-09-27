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


def remove_whitespace(s):
  return whitespace_re.sub("", s)


def set_full_name(font, fullName, fullNamePs):
  nameTable = font["name"]
  nameTable.setName(fullName, FULL_NAME, 1, 0, 0)     # mac
  nameTable.setName(fullName, FULL_NAME, 3, 1, 0x409) # windows
  nameTable.setName(fullNamePs, POSTSCRIPT_NAME, 1, 0, 0)     # mac
  nameTable.setName(fullNamePs, POSTSCRIPT_NAME, 3, 1, 0x409) # windows


def get_family_name(font):
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


def fix_fullname(font):
  fullName = get_family_name(font)
  fullNamePs = remove_whitespace(fullName)
  set_full_name(font, fullName, fullNamePs)
  return fullName


# def clear_subfamily_name(font):
#   nameTable = font["name"]
#   rmrecs = []
#   for rec in nameTable.names:
#     if rec.nameID == SUBFAMILY_NAME or rec.nameID == TYPO_SUBFAMILY_NAME:
#       rmrecs.append(rec)
#   for rec in rmrecs:
#     nameTable.removeNames(rec.nameID, rec.platformID, rec.platEncID, rec.langID)


def fix_unique_id(font, fullName):
  fontIdRecs = []
  newId = ''
  nameTable = font["name"]
  for rec in nameTable.names:
    if rec.nameID == TRUETYPE_UNIQUE_ID:
      if newId == '':
        oldId = rec.toUnicode()
        newId = remove_whitespace(fullName)
        p = oldId.find(':')
        if p > -1:
          newId += oldId[p:]
      fontIdRecs.append(rec)
  for rec in fontIdRecs:
    nameTable.setName(newId, rec.nameID, rec.platformID, rec.platEncID, rec.langID)


def main():
  argparser = argparse.ArgumentParser(description='Fix names in variable font')
  a = lambda *args, **kwargs: argparser.add_argument(*args, **kwargs)
  a('-o', '--output', metavar='<file>',
    help='Output font file. Defaults to input file (overwrite)')
  a('input', metavar='<file>',
    help='Input font file')
  args = argparser.parse_args()

  infile = args.input
  outfile = args.output or infile

  font = TTFont(infile, recalcBBoxes=False, recalcTimestamp=False)

  fullName = fix_fullname(font)
  fix_unique_id(font, fullName)
  #clear_subfamily_name(font)

  font.save(outfile)
  font.close()


if __name__ == '__main__':
  main()
