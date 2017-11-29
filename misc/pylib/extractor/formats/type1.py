from fontTools.t1Lib import T1Font, T1Error
from fontTools.agl import AGL2UV
from fontTools.misc.psLib import PSInterpreter
from fontTools.misc.transform import Transform
from extractor.tools import RelaxedInfo

# specification: http://partners.adobe.com/public/developer/en/font/T1_SPEC.PDF

# ----------------
# Public Functions
# ----------------

def isType1(pathOrFile):
    try:
        font = T1Font(pathOrFile)
        del font
    except T1Error:
        return False
    return True

def extractFontFromType1(pathOrFile, destination, doGlyphs=True, doInfo=True, doKerning=True, customFunctions=[]):
    source = T1Font(pathOrFile)
    destination.lib["public.glyphOrder"] = _extractType1GlyphOrder(source)
    if doInfo:
        extractType1Info(source, destination)
    if doGlyphs:
        extractType1Glyphs(source, destination)
    if doKerning:
        # kerning extraction is not supported yet.
        # in theory, it could be retried from an AFM.
        # we need to find the AFM naming rules so that we can sniff for the file.
        pass
    for function in customFunctions:
        function(source, destination)

def extractType1Info(source, destination):
    info = RelaxedInfo(destination.info)
    _extractType1FontInfo(source, info)
    _extractType1Private(source, info)
    _extractType1FontMatrix(source, info)

# ----
# Info
# ----

def _extractType1FontInfo(source, info):
    sourceInfo = source["FontInfo"]
    # FontName
    info.postscriptFontName = source["FontName"]
    # version
    version = sourceInfo.get("version")
    if version is not None:
        # the spec says that version will be a string and no formatting info is given.
        # so, only move forward if the string can actually be parsed.
        try:
            # 1. convert to a float
            version = float(version)
            # 2. convert it back to a string
            version = "%.3f" % version
            # 3. split.
            versionMajor, versionMinor = version.split(".")
            # 4. convert.
            versionMajor = int(versionMajor)
            versionMinor = int(versionMinor)
            # 5. set.
            info.versionMajor = int(versionMajor)
            info.versionMinor = int(versionMinor)
        except ValueError:
            # couldn't parse. leve the object with the default values.
            pass
    # Notice
    notice = sourceInfo.get("Notice")
    if notice:
        info.copyright = notice
    # FullName
    fullName = sourceInfo.get("FullName")
    if fullName:
        info.postscriptFullName = fullName
    # FamilyName
    familyName = sourceInfo.get("FamilyName")
    if familyName:
        info.familyName = familyName
    # Weight
    postscriptWeightName = sourceInfo.get("Weight")
    if postscriptWeightName:
        info.postscriptWeightName = postscriptWeightName
    # ItalicAngle
    info.italicAngle = sourceInfo.get("ItalicAngle")
    # IsFixedPitch
    info.postscriptIsFixedPitch = sourceInfo.get("isFixedPitch")
    # UnderlinePosition/Thickness
    info.postscriptUnderlinePosition = sourceInfo.get("UnderlinePosition")
    info.postscriptUnderlineThickness = sourceInfo.get("UnderlineThickness")

def _extractType1FontMatrix(source, info):
    # units per em
    matrix = source["FontMatrix"]
    matrix = Transform(*matrix).inverse()
    info.unitsPerEm = int(round(matrix[3]))

def _extractType1Private(source, info):
    private = source["Private"]
    # UniqueID
    info.openTypeNameUniqueID = private.get("UniqueID", None)
    # BlueValues and OtherBlues
    info.postscriptBlueValues = private.get("BlueValues", [])
    info.postscriptOtherBlues = private.get("OtherBlues", [])
    # FamilyBlues and FamilyOtherBlues
    info.postscriptFamilyBlues = private.get("FamilyBlues", [])
    info.postscriptFamilyOtherBlues = private.get("FamilyOtherBlues", [])
    # BlueScale/Shift/Fuzz
    info.postscriptBlueScale = private.get("BlueScale", None)
    info.postscriptBlueShift = private.get("BlueShift", None)
    info.postscriptBlueFuzz = private.get("BlueFuzz", None)
    # StemSnapH/V
    info.postscriptStemSnapH = private.get("StemSnapH", [])
    info.postscriptStemSnapV = private.get("StemSnapV", [])
    # ForceBold
    info.postscriptForceBold = bool(private.get("ForceBold", None))

# --------
# Outlines
# --------

def extractType1Glyphs(source, destination):
    glyphSet = source.getGlyphSet()
    for glyphName in sorted(glyphSet.keys()):
        sourceGlyph = glyphSet[glyphName]
        # make the new glyph
        destination.newGlyph(glyphName)
        destinationGlyph = destination[glyphName]
        # outlines
        pen = destinationGlyph.getPen()
        sourceGlyph.draw(pen)
        # width
        destinationGlyph.width = sourceGlyph.width
        # synthesize the unicode value
        destinationGlyph.unicode = AGL2UV.get(glyphName)

# -----------
# Glyph order
# -----------

class GlyphOrderPSInterpreter(PSInterpreter):

    def __init__(self):
        PSInterpreter.__init__(self)
        self.glyphOrder = []
        self.collectTokenForGlyphOrder = False

    def do_literal(self, token):
        result = PSInterpreter.do_literal(self, token)
        if token == "/FontName":
            self.collectTokenForGlyphOrder = False
        if self.collectTokenForGlyphOrder:
            self.glyphOrder.append(result.value)
        if token == "/CharStrings":
            self.collectTokenForGlyphOrder = True
        return result

def _extractType1GlyphOrder(t1Font):
    interpreter = GlyphOrderPSInterpreter()
    interpreter.interpret(t1Font.data)
    return interpreter.glyphOrder
