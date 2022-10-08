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


def main(argv):
  ufo_file = argv[1]
  if ufo_file.find("Display") == -1:
    return  # skip fonts of "default" family
  ufo = defcon.Font(ufo_file)
  ufo_set_wws(ufo)
  ufo.save(ufo_file)


if __name__ == '__main__':
  main(sys.argv)
