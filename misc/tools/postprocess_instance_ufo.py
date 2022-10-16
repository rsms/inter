import sys
import defcon

def ufo_set_wws(ufo):
  # Fix missing WWS entries for Display fonts:
  # See https://github.com/googlefonts/glyphsLib/issues/820
  subfamily = ufo.info.styleName
  if subfamily.find("Display") == -1:
    return
  subfamily = subfamily[len("Display"):].strip()
  if subfamily == "":
    # "Display" -> "Regular"
    subfamily = "Regular"
  ufo.info.openTypeNameWWSFamilyName = "Inter Display"
  ufo.info.openTypeNameWWSSubfamilyName = subfamily


# See https://github.com/rsms/inter/issues/508
# TODO: Remove when https://github.com/googlefonts/glyphsLib/issues/821 is fixed
def fix_fractional_advance_width(ufo):
  for g in ufo:
    w = int(round(g.width))
    if str(g.width) != str(w):
      # set twice to work around bug or weird behavior in defcon.
      # If we don't do this, then fractional widths with .0 fraction are
      # not updated to integer values.
      g.width = w + 1
      g.width = w


def main(argv):
  ufo_file = argv[1]

  # TODO: Uncomment when https://github.com/googlefonts/glyphsLib/issues/821 is fixed
  # if ufo_file.find("Display") == -1:
  #   return  # skip fonts of "default" family

  ufo = defcon.Font(ufo_file)

  if ufo_file.find("Display") != -1:
    ufo_set_wws(ufo)

  fix_fractional_advance_width(ufo)

  ufo.save(ufo_file)


if __name__ == '__main__':
  main(sys.argv)
