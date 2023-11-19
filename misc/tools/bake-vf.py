"""
This script "bakes" the final Inter variable fonts.

This script performs the following:
  1. Renames the family to "Inter Variable"
  2. Updates style names to scrub away "Display"
  3. Builds a STAT table

How to debug/develop this script:

1. build the initial fonts:

  make -j var

2. after making changes, run script and inspect with ttx:

  (. build/venv/bin/activate && mkdir -p build/bake &&
    for f in build/fonts/var/.Inter-*.var.ttf; do
      python misc/tools/bake-vf.py "$f" -o build/bake/"$(basename "${f/.Inter/Inter}")"
    done)
  (. build/venv/bin/activate && ttx -t STAT -i -f -s build/bake/Inter-*.var.ttf)

"""
import sys, os, os.path, re, argparse
from fontTools.ttLib import TTFont
from fontTools.otlLib.builder import buildStatTable

FLAG_DEFAULT = 0x2  # elidable value, effectively marks a location as default

OPSZ_MIN = 0 # set at runtime to fvar.axes['opsz'].minValue
OPSZ_MAX = 0 # set at runtime to fvar.axes['opsz'].maxValue


# stat_axes_format_2 is used for making a STAT table with format 1 & 2 records
def stat_axes_format_2(is_italic):
  OPSZ_MID = OPSZ_MIN + int(round((OPSZ_MAX - OPSZ_MIN) / 2))
  return [
    dict(name="Optical Size", tag="opsz", ordering=0, values=[
      dict(nominalValue=OPSZ_MIN, rangeMinValue=OPSZ_MIN, rangeMaxValue=OPSZ_MID,
        name="Text", flags=FLAG_DEFAULT, linkedValue=OPSZ_MAX),
      dict(nominalValue=OPSZ_MAX, rangeMinValue=OPSZ_MID, rangeMaxValue=OPSZ_MAX,
        name="Display"),
    ]),
    dict(name="Weight", tag="wght", ordering=1, values=[
      dict(nominalValue=100, rangeMinValue=100, rangeMaxValue=150, name="Thin"),
      dict(nominalValue=200, rangeMinValue=150, rangeMaxValue=250, name="ExtraLight"),
      dict(nominalValue=300, rangeMinValue=250, rangeMaxValue=350, name="Light"),
      dict(nominalValue=400, rangeMinValue=350, rangeMaxValue=450, name="Regular",
           flags=FLAG_DEFAULT, linkedValue=700),
      dict(nominalValue=500, rangeMinValue=450, rangeMaxValue=550, name="Medium"),
      dict(nominalValue=600, rangeMinValue=550, rangeMaxValue=650, name="SemiBold"),
      dict(nominalValue=700, rangeMinValue=650, rangeMaxValue=750, name="Bold"),
      dict(nominalValue=800, rangeMinValue=750, rangeMaxValue=850, name="ExtraBold"),
      dict(nominalValue=900, rangeMinValue=850, rangeMaxValue=900, name="Black"),
    ]),
    dict(name="Italic", tag="ital", ordering=2, values=[
      dict(value=1, name="Italic", linkedValue=0) if is_italic else \
      dict(value=0, name="Roman", flags=FLAG_DEFAULT),
    ]),
  ]


# stat_axes_format_3 is used for making a STAT table with format 1 & 3 records
def stat_axes_format_3(is_italic):
  # see https://learn.microsoft.com/en-us/typography/opentype/spec/
  #     stat#axis-value-table-format-3
  return [
    dict(name="Optical Size", tag="opsz", values=[
      dict(value=OPSZ_MIN, name="Text"),
      dict(value=OPSZ_MAX, name="Display"),
    ]),
    dict(name="Weight", tag="wght", values=[
      dict(name="Thin",       value=100 ),
      dict(name="ExtraLight", value=200 ),
      dict(name="Light",      value=300 ),
      dict(name="Regular",    value=400, linkedValue=700, flags=FLAG_DEFAULT ),
      dict(name="Medium",     value=500 ),
      dict(name="SemiBold",   value=600 ),
      dict(name="Bold",       value=700 ),
      dict(name="ExtraBold",  value=800 ),
      dict(name="Black",      value=900 ),
    ]),
    # Note: OK to have two 'linkedValue's here since we make two separate VFs
    dict(name="Italic", tag="ital", values=[
      dict(value=1, name="Italic", linkedValue=0) if is_italic else \
      dict(value=0, name="Roman", linkedValue=1, flags=FLAG_DEFAULT),
    ]),
  ]


# # STAT_AXES is used for making a STAT table with format 4 records
# STAT_AXES = [
#   { "name": "Optical Size", "tag": "opsz" },
#   { "name": "Weight",       "tag": "wght" },
#   { "name": "Italic",       "tag": "ital" }
# ]

# # stat_locations is used for making a STAT table with format 4 records
# def stat_locations(is_italic):
#   # see https://learn.microsoft.com/en-us/typography/opentype/spec/
#   #     stat#axis-value-table-format-4
#   ital = 1 if is_italic else 0
#   suffix = " Italic" if is_italic else ""
#   return [
#     { "name": "Thin"+suffix,       "location":{"wght":100, "ital":ital} },
#     { "name": "ExtraLight"+suffix, "location":{"wght":200, "ital":ital} },
#     { "name": "Light"+suffix,      "location":{"wght":300, "ital":ital} },
#     { "name": "Regular"+suffix,    "location":{"wght":400, "ital":ital},
#       "flags":FLAG_DEFAULT },
#     { "name": "Medium"+suffix,     "location":{"wght":500, "ital":ital} },
#     { "name": "SemiBold"+suffix,   "location":{"wght":600, "ital":ital} },
#     { "name": "Bold"+suffix,       "location":{"wght":700, "ital":ital} },
#     { "name": "ExtraBold"+suffix,  "location":{"wght":800, "ital":ital} },
#     { "name": "Black"+suffix,      "location":{"wght":900, "ital":ital} },
#   ]


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

WHITESPACE_RE = re.compile(r'\s+')


def remove_whitespace(s):
  return WHITESPACE_RE.sub('', s)


def normalize_whitespace(s):
  return WHITESPACE_RE.sub(' ', s)


def remove_substring(s, substr):
  # examples of remove_substring(s, "Display"):
  #   "Inter Display"   => "Inter"
  #   "Display Lol"     => "Lol"
  #   "Foo Display Lol" => "Foo Lol"
  #   " Foo   Bar Lol " => "Foo Bar Lol"
  return normalize_whitespace(s.strip().replace(substr, '')).strip()


def font_is_italic(ttfont):
  """Check if the font has the word "Italic" in its stylename"""
  stylename = ttfont["name"].getName(2, 3, 1, 0x409).toUnicode()
  return True if "Italic" in stylename else False


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

  # add name ID 25 "Variations PostScript Name Prefix" if not found
  if not found_VAR_PS_NAME_PREFIX and nextFamilyName.find('Variable') != -1:
    varPSNamePrefix = remove_whitespace(nextFamilyName)
    if font_is_italic(font):
      varPSNamePrefix += 'Italic'
    nameTable.setName(varPSNamePrefix, VAR_PS_NAME_PREFIX, 1, 0, 0)     # mac
    nameTable.setName(varPSNamePrefix, VAR_PS_NAME_PREFIX, 3, 1, 0x409) # windows


def gen_stat(ttfont):
  # builds a STAT table
  # https://learn.microsoft.com/en-us/typography/opentype/spec/stat
  #
  # We are limited to format 2 or 3 records, else Adobe products like InDesign
  # bugs out. See https://github.com/rsms/inter/issues/577
  #
  # build a version 1.1 STAT table with format 2 records:
  #buildStatTable(ttfont, stat_axes_format_2(font_is_italic(ttfont)))
  #
  # build a version 1.1 STAT table with format 1 and 3 records:
  buildStatTable(ttfont, stat_axes_format_3(font_is_italic(ttfont)))
  #
  # build a version 1.2 STAT table with format 4 records:
  #locations = stat_locations(font_is_italic(ttfont))
  #buildStatTable(ttfont, STAT_AXES, locations=locations)


def check_fvar(ttfont):
  fvar = ttfont['fvar']
  error = False
  for i in fvar.instances:
    actual_wght = i.coordinates['wght']
    expected_wght = round(actual_wght / 100) * 100
    if expected_wght != actual_wght:
      print(f"unexpected wght {actual_wght} (expected {expected_wght})",
        ttfont, i.coordinates)
      error = True


# def fixup_fvar(ttfont):
#   fvar = ttfont['fvar']
#   for i in fvar.instances:
#     wght = round(i.coordinates['wght'] / 100) * 100
#     print(f"wght {i.coordinates['wght']} -> {wght}")
#     #i.coordinates['wght'] = wght
#   # for a in fvar.axes:
#   #   if a.axisTag == "wght":
#   #     a.defaultValue = 400
#   #     break


# def fixup_os2(ttfont):
#   os2 = ttfont['OS/2']
#   os2.usWeightClass = 400


def main():
  argparser = argparse.ArgumentParser(
    description='Generate STAT table for variable font family')
  a = lambda *args, **kwargs: argparser.add_argument(*args, **kwargs)
  a('--family', metavar='<name>',
    help='Rename family to <name> instead of "Inter Variable"')
  a('-o', '--output', metavar='<file>',
    help='Output font file. Defaults to input file (overwrite)')
  a('input', metavar='<file>', help='Input font file')

  args = argparser.parse_args()

  # load font
  ttfont = TTFont(args.input, recalcBBoxes=False, recalcTimestamp=False)

  # infer axis extremes
  global OPSZ_MIN
  global OPSZ_MAX
  for a in ttfont["fvar"].axes:
    if a.axisTag == "opsz":
      OPSZ_MIN = int(a.minValue)
      OPSZ_MAX = int(a.maxValue)
      break

  # set family name
  if not args.family:
    args.family = "Inter Variable"
  setFamilyName(ttfont, args.family)

  # set style name
  stylename = remove_substring(getStyleName(ttfont), "Display")
  if stylename == '':
    stylename = 'Regular'
  setStyleName(ttfont, stylename)

  # build STAT table
  gen_stat(ttfont)

  # check fvar table
  check_fvar(ttfont)

  # # fixup OS/2 table (set usWeightClass)
  # fixup_os2(ttfont)

  # save font
  outfile = args.output or args.input
  ttfont.save(outfile)


if __name__ == '__main__':
  main()
