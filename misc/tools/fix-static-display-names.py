import sys, os, os.path, argparse, re
from fontTools.ttLib import TTFont

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
WWS_SUBFAMILY       = 22

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


def getStyleName(font):
  nameTable = font["name"]
  for plat_id, enc_id, lang_id in (WINDOWS_ENGLISH_IDS, MAC_ROMAN_IDS):
    for name_id in (TYPO_SUBFAMILY_NAME, SUBFAMILY_NAME):
      r = nameTable.getName(
        nameID=name_id, platformID=plat_id, platEncID=enc_id, langID=lang_id)
      if r is not None:
        return r.toUnicode()
  raise ValueError("style name not found")


def print_relevant_names(nameTable):
  names = {
    LEGACY_FAMILY: "LEGACY_FAMILY",
    TRUETYPE_UNIQUE_ID: "TRUETYPE_UNIQUE_ID",
    FULL_NAME: "FULL_NAME",
    POSTSCRIPT_NAME: "POSTSCRIPT_NAME",
    PREFERRED_FAMILY: "PREFERRED_FAMILY",
    WWS_FAMILY: "WWS_FAMILY",
    WWS_SUBFAMILY: "WWS_SUBFAMILY",
    SUBFAMILY_NAME: "SUBFAMILY_NAME",
    TYPO_SUBFAMILY_NAME: "TYPO_SUBFAMILY_NAME",
  }
  for rec in nameTable.names:
    name_id = rec.nameID
    name = names.get(name_id)
    if name:
      print("%-19s  #%-2d  %s" % (name, name_id, rec.toUnicode()))


def main():
  argparser = argparse.ArgumentParser(
    description='Rename family and styles of static "Inter Display" fonts'
  )
  a = lambda *args, **kwargs: argparser.add_argument(*args, **kwargs)
  a('-o', '--output', metavar='<file>',
    help='Output font file. Defaults to input file (overwrite)')
  a('input', metavar='<file>', help='Input font file')
  args = argparser.parse_args()

  infile = args.input
  outfile = args.output or infile

  font = TTFont(infile, recalcBBoxes=False, recalcTimestamp=False)

  family = "Inter Display"
  style = remove_substring(getStyleName(font), "Display")
  isItalic = style.find('Italic') != -1
  if style == '':
    style = 'Regular'

  # See https://learn.microsoft.com/en-us/typography/opentype/spec/name
  nameTable = font["name"]

  fullName = family + " " + style
  fullNamePs = remove_whitespace(family) + "-" + remove_whitespace(style)

  try:
    # print_relevant_names(nameTable)

    # set full name
    nameTable.setName(fullName, FULL_NAME, 1, 0, 0)     # mac
    nameTable.setName(fullName, FULL_NAME, 3, 1, 0x409) # windows
    nameTable.setName(fullNamePs, POSTSCRIPT_NAME, 1, 0, 0)     # mac
    nameTable.setName(fullNamePs, POSTSCRIPT_NAME, 3, 1, 0x409) # windows

    for rec in nameTable.names:
      id = rec.nameID
      if id == TRUETYPE_UNIQUE_ID: # ID 3
        # Format:
        #   version ";" "git-" git-tag ";" foundry-tag ";" ps_family "-" ps_style
        # E.g.
        #   "4.001;git-4de559246;RSMS;Inter-DisplayThinItalic"
        id = rec.toUnicode().split(";")
        id[3] = fullNamePs
        rec.string = ";".join(id)
      elif id == LEGACY_FAMILY: # ID 1
        rec.string = family + ' ' + style
      elif id == SUBFAMILY_NAME: # ID 2
        rec.string = 'Italic' if isItalic else 'Regular'
      elif id == PREFERRED_FAMILY: # ID 16
        rec.string = family
      elif id == WWS_FAMILY: # ID 21
        rec.string = family
      elif id == WWS_SUBFAMILY: # ID 22
        rec.string = style
      elif id == TYPO_SUBFAMILY_NAME: # ID 17
        rec.string = style

    # print("————————————————————————————————————————————————————")
    # print_relevant_names(nameTable)

    font.save(outfile)
  finally:
    font.close()


if __name__ == '__main__':
  main()
