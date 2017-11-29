from xml.sax.saxutils import quoteattr
from fontTools.ttLib import TTFont, TTLibError
from extractor.tools import RelaxedInfo
from extractor.formats.opentype import extractOpenTypeInfo, extractOpenTypeGlyphs, extractOpenTypeKerning

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

# ----------------
# Public Functions
# ----------------

def isWOFF(pathOrFile):
    flavor = None
    try:
        font = TTFont(pathOrFile)
        flavor = font.flavor
        del font
    except TTLibError:
        return False
    return flavor in ("woff", "woff2")

def extractFontFromWOFF(pathOrFile, destination, doGlyphs=True, doInfo=True, doKerning=True, customFunctions=[]):
    source = TTFont(pathOrFile)
    if doInfo:
        extractWOFFInfo(source, destination)
    if doGlyphs:
        extractWOFFGlyphs(source, destination)
    if doKerning:
        kerning, groups = extractWOFFKerning(source, destination)
        destination.groups.update(groups)
        destination.kerning.clear()
        destination.kerning.update(kerning)
    for function in customFunctions:
        function(source, destination)
    source.close()

# ----------------
# Specific Imports
# ----------------

def extractWOFFInfo(source, destination):
    info = RelaxedInfo(destination.info)
    info.woffMajorVersion = source.flavorData.majorVersion
    info.woffMinorVersion = source.flavorData.minorVersion
    _extractWOFFMetadata(source.flavorData, info)
    return extractOpenTypeInfo(source, destination)

def extractWOFFGlyphs(source, destination):
    return extractOpenTypeGlyphs(source, destination)

def extractWOFFKerning(source, destination):
    return extractOpenTypeKerning(source, destination)

# --------
# Metadata
# --------

def _extractWOFFMetadata(source, destination):
    if source.metaData is None:
        return
    metadata = ElementTree.fromstring(source.metaData)
    for element in metadata:
        if element.tag == "uniqueid":
            _extractWOFFMetadataUniqueID(element, destination)
        elif element.tag == "vendor":
            _extractWOFFMetadataVendor(element, destination)
        elif element.tag == "credits":
            _extractWOFFMetadataCredits(element, destination)
        elif element.tag == "description":
            _extractWOFFMetadataDescription(element, destination)
        elif element.tag == "license":
            _extractWOFFMetadataLicense(element, destination)
        elif element.tag == "copyright":
            _extractWOFFMetadataCopyright(element, destination)
        elif element.tag == "trademark":
            _extractWOFFMetadataTrademark(element, destination)
        elif element.tag == "licensee":
            _extractWOFFMetadataLicensee(element, destination)
        elif element.tag == "extension":
            _extractWOFFMetadataExtension(element, destination)

def _extractWOFFMetadataUniqueID(element, destination):
    destination.woffMetadataUniqueID = _extractWOFFMetadataDict(element, ("id",))

def _extractWOFFMetadataVendor(element, destination):
    attributes = ("name", "url", "dir", "class")
    record = _extractWOFFMetadataDict(element, attributes)
    destination.woffMetadataVendor = record

def _extractWOFFMetadataCredits(element, destination):
    attributes = ("name", "url", "role", "dir", "class")
    credits = []
    for subElement in element:
        if subElement.tag == "credit":
            record = _extractWOFFMetadataDict(subElement, attributes)
            credits.append(record)
    destination.woffMetadataCredits = dict(credits=credits)

def _extractWOFFMetadataDescription(element, destination):
    description = _extractWOFFMetadataDict(element, ("url",))
    textRecords = _extractWOFFMetadataText(element)
    if textRecords:
        description["text"] = textRecords
    destination.woffMetadataDescription = description

def _extractWOFFMetadataLicense(element, destination):
    license = _extractWOFFMetadataDict(element, ("url", "id"))
    textRecords = _extractWOFFMetadataText(element)
    if textRecords:
        license["text"] = textRecords
    destination.woffMetadataLicense = license

def _extractWOFFMetadataCopyright(element, destination):
    copyright = {}
    textRecords = _extractWOFFMetadataText(element)
    if textRecords:
        copyright["text"] = textRecords
    destination.woffMetadataCopyright = copyright

def _extractWOFFMetadataTrademark(element, destination):
    trademark = {}
    textRecords = _extractWOFFMetadataText(element)
    if textRecords:
        trademark["text"] = textRecords
    destination.woffMetadataTrademark = trademark

def _extractWOFFMetadataLicensee(element, destination):
    destination.woffMetadataLicensee = _extractWOFFMetadataDict(element, ("name", "dir", "class"))

def _extractWOFFMetadataExtension(element, destination):
    extension = _extractWOFFMetadataDict(element, ("id",))
    for subElement in element:
        if subElement.tag == "name":
            if "names" not in extension:
                extension["names"] = []
            name = _extractWOFFMetadataExtensionName(subElement)
            extension["names"].append(name)
        elif subElement.tag == "item":
            if "items" not in extension:
                extension["items"] = []
            item = _extractWOFFMetadataExtensionItem(subElement)
            extension["items"].append(item)
    extensions = []
    if destination.woffMetadataExtensions:
        extensions.extend(destination.woffMetadataExtensions)
    destination.woffMetadataExtensions = extensions + [extension]

def _extractWOFFMetadataExtensionItem(element):
    item = _extractWOFFMetadataDict(element, ("id",))
    for subElement in element:
        if subElement.tag == "name":
            if "names" not in item:
                item["names"] = []
            name = _extractWOFFMetadataExtensionName(subElement)
            item["names"].append(name)
        elif subElement.tag == "value":
            if "values" not in item:
                item["values"] = []
            name = _extractWOFFMetadataExtensionValue(subElement)
            item["values"].append(name)
    return item

def _extractWOFFMetadataExtensionName(element):
    name = _extractWOFFMetadataDict(element, ("dir", "class"))
    language = _extractWOFFMetadataLanguage(element)
    if language is not None:
        name["language"] = language
    name["text"] = _flattenWOFFMetadataString(element)
    return name

def _extractWOFFMetadataExtensionValue(element):
    return _extractWOFFMetadataExtensionName(element)

# support

def _extractWOFFMetadataDict(element, attributes):
    record = {}
    for attribute in attributes:
        value = element.attrib.get(attribute)
        if value is not None:
            record[attribute] = value
    return record

def _extractWOFFMetadataText(element):
    records = []
    attributes = ("dir", "class")
    for subElement in element:
        record = _extractWOFFMetadataDict(subElement, attributes)
        # text
        record["text"] = _flattenWOFFMetadataString(subElement)
        # language
        language = _extractWOFFMetadataLanguage(subElement)
        if language is not None:
            record["language"] = language
        records.append(record)
    return records

def _extractWOFFMetadataLanguage(element):
    language = element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    if language is None:
        language = element.attrib.get("lang")
    return language

def _flattenWOFFMetadataString(element, sub=False):
    text = element.text.strip()
    for subElement in element:
        text += _flattenWOFFMetadataString(subElement, sub=True)
    if element.tail:
        text += element.tail.strip()
    if sub:
        attrib = ["%s=%s" % (key, quoteattr(value)) for key, value in element.attrib.items()]
        attrib = " ".join(attrib)
        if attrib:
            start = "<%s %s>" % (element.tag, attrib)
        else:
            start = "<%s>" % (element.tag)
        end = "</%s>" % (element.tag)
        text = start + text + end
    return text
