from extractor.exceptions import ExtractorError
from extractor.formats.opentype import isOpenType, extractFontFromOpenType
from extractor.formats.woff import isWOFF, extractFontFromWOFF
from extractor.formats.type1 import isType1, extractFontFromType1
from extractor.formats.ttx import isTTX, extractFontFromTTX


__version__ = "0.2.1.dev0"

_extractFunctions = dict(
    OTF=extractFontFromOpenType,
    Type1=extractFontFromType1,
    WOFF=extractFontFromWOFF,
    ttx=extractFontFromTTX,
)

def extractFormat(pathOrFile):
    if isType1(pathOrFile):
        return "Type1"
    elif isWOFF(pathOrFile):
        return "WOFF"
    elif isOpenType(pathOrFile):
        return "OTF"
    elif isTTX(pathOrFile):
        return "ttx"
    return None

def extractUFO(pathOrFile, destination, doGlyphs=True, doInfo=True, doKerning=True, format=None, customFunctions={}):
    if format is None:
        format = extractFormat(pathOrFile)
    if format not in _extractFunctions:
        raise ExtractorError("Unknown file format.")
    func = _extractFunctions[format]
    # wrap the extraction in a try: except: so that
    # callers don't need to worry about lower level
    # (fontTools, etc.) errors. if an error
    # occurs, print the traceback for debugging and
    # raise an ExtractorError.
    try:
        func(pathOrFile, destination, doGlyphs=doGlyphs, doInfo=doInfo, doKerning=doKerning, customFunctions=customFunctions.get(format, []))
    except:
        import sys
        import traceback
        traceback.print_exc(file=sys.stdout)
        raise ExtractorError("There was an error reading the %s file." % format)
