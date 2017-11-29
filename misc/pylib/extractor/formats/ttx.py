from extractor.formats.opentype import extractOpenTypeInfo, extractOpenTypeGlyphs, extractOpenTypeKerning

def isTTX(pathOrFile):
    from fontTools.ttLib import TTFont, TTLibError
    try:
        font = TTFont()
        font.importXML(pathOrFile)
        del font
    except TTLibError:
        return False
    return True

def extractFontFromTTX(pathOrFile, destination, doGlyphs=True, doInfo=True, doKerning=True, customFunctions=[]):
    from fontTools.ttLib import TTFont, TTLibError
    source = TTFont()
    source.importXML(pathOrFile)
    if doInfo:
        extractOpenTypeInfo(source, destination)
    if doGlyphs:
        extractOpenTypeGlyphs(source, destination)
    if doKerning:
        kerning, groups = extractOpenTypeKerning(source, destination)
        destination.groups.update(groups)
        destination.kerning.clear()
        destination.kerning.update(kerning)
    for function in customFunctions:
        function(source, destination)
    source.close()
