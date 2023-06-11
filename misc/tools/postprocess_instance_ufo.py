import sys, re
import defcon


WHITESPACE_RE = re.compile(r'\s+')


def rmspace(s):
  return WHITESPACE_RE.sub('', s)


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
  ufo = defcon.Font(ufo_file)
  fix_fractional_advance_width(ufo)

  # fix legacy names to make style linking work in MS Windows
  familyName = ufo.info.familyName  # e.g. "Inter Display"
  styleName = ufo.info.styleName    # e.g. "ExtraBold"
  ufo.info.openTypeNamePreferredFamilyName = familyName
  ufo.info.openTypeNamePreferredSubfamilyName = styleName

  ufo.info.familyName = (familyName + ' ' + styleName).replace(' Italic', '').strip()
  ufo.info.styleName = 'Regular' if styleName.find('Italic') == -1 else 'Italic'

  # must also set these explicitly to avoid PostScript names like "Inter-ThinRegular":
  # "postscriptFontName" maps to name ID 6 "postscriptName"
  ufo.info.postscriptFontName = rmspace(familyName) + '-' + rmspace(styleName)

  # round OS/2 weight class values to even 100ths
  ufo.info.openTypeOS2WeightClass = round(ufo.info.openTypeOS2WeightClass / 100) * 100

  ufo.save(ufo_file)


if __name__ == '__main__':
  main(sys.argv)
