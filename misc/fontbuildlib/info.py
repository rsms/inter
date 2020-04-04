import subprocess
import re
import sys
from datetime import datetime
from common import getGitHash, getVersion
from .util import readTextFile, BASEDIR, pjoin


def updateFontVersion(font, dummy, isVF):
  if dummy:
    version = "1.0"
    buildtag = "src"
    now = datetime(2016, 1, 1, 0, 0, 0, 0)
  else:
    version = getVersion()
    buildtag, buildtagErrs = getGitHash()
    now = datetime.utcnow()
    if buildtag == "" or len(buildtagErrs) > 0:
      buildtag = "src"
      print("warning: getGitHash() failed: %r" % buildtagErrs, file=sys.stderr)
  versionMajor, versionMinor = [int(num) for num in version.split(".")]
  font.info.version = version
  font.info.versionMajor = versionMajor
  font.info.versionMinor = versionMinor
  font.info.woffMajorVersion = versionMajor
  font.info.woffMinorVersion = versionMinor
  font.info.year = now.year
  font.info.openTypeNameVersion = "Version %d.%03d;git-%s" % (versionMajor, versionMinor, buildtag)
  psFamily = re.sub(r'\s', '', font.info.familyName)
  if isVF:
    font.info.openTypeNameUniqueID = "%s:VF:%d:%s" % (psFamily, now.year, buildtag)
  else:
    psStyle = re.sub(r'\s', '', font.info.styleName)
    font.info.openTypeNameUniqueID = "%s-%s:%d:%s" % (psFamily, psStyle, now.year, buildtag)
  font.info.openTypeHeadCreated = now.strftime("%Y/%m/%d %H:%M:%S")



# setFontInfo patches font.info
def setFontInfo(font, weight=None):
  #
  # For UFO3 names, see
  # https://github.com/unified-font-object/ufo-spec/blob/gh-pages/versions/
  #   ufo3/fontinfo.plist.md
  # For OpenType NAME table IDs, see
  # https://docs.microsoft.com/en-us/typography/opentype/spec/name#name-ids

  if weight is None:
    weight = font.info.openTypeOS2WeightClass

  family = font.info.familyName  # i.e. "Inter"
  style = font.info.styleName    # e.g. "Medium Italic"

  # Update italicAngle
  isitalic = style.find("Italic") != -1
  if isitalic:
    font.info.italicAngle = float('%.8g' % font.info.italicAngle)
  else:
    font.info.italicAngle = 0  # avoid "-0.0" value in UFO

  # weight
  font.info.openTypeOS2WeightClass = weight

  # version (dummy)
  updateFontVersion(font, dummy=True, isVF=False)

  # Names
  family_nosp = re.sub(r'\s', '', family)
  style_nosp = re.sub(r'\s', '', style)
  font.info.macintoshFONDName = "%s %s" % (family_nosp, style_nosp)
  font.info.postscriptFontName = "%s-%s" % (family_nosp, style_nosp)

  # name ID 16 "Typographic Family name"
  font.info.openTypeNamePreferredFamilyName = family

  # name ID 17 "Typographic Subfamily name"
  font.info.openTypeNamePreferredSubfamilyName = style

  # name ID 1 "Family name" (legacy, but required)
  # Restriction:
  #   "shared among at most four fonts that differ only in weight or style"
  # So we map as follows:
  # - Regular => "Family", ("regular" | "italic" | "bold" | "bold italic")
  # - Medium  => "Family Medium", ("regular" | "italic")
  # - Black   => "Family Black", ("regular" | "italic")
  # and so on.
  subfamily = stripItalic(style).strip() # "A Italic" => "A", "A" => "A"
  if len(subfamily) == 0:
    subfamily = "Regular"
  subfamily_lc = subfamily.lower()
  if subfamily_lc == "regular" or subfamily_lc == "bold":
    font.info.styleMapFamilyName = family
    # name ID 2 "Subfamily name" (legacy, but required)
    # Value must be one of: "regular", "italic", "bold", "bold italic"
    if subfamily_lc == "regular":
      if isitalic:
        font.info.styleMapStyleName = "italic"
      else:
        font.info.styleMapStyleName = "regular"
    else: # bold
      if isitalic:
        font.info.styleMapStyleName = "bold italic"
      else:
        font.info.styleMapStyleName = "bold"
  else:
    font.info.styleMapFamilyName = (family + ' ' + subfamily).strip()
    # name ID 2 "Subfamily name" (legacy, but required)
    if isitalic:
      font.info.styleMapStyleName = "italic"
    else:
      font.info.styleMapStyleName = "regular"



stripItalic_re = re.compile(r'(?:^|\b)italic\b|italic$', re.I | re.U)


def stripItalic(name):
  return stripItalic_re.sub('', name.strip())