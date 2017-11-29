import time
from fontTools.ttLib import TTFont, TTLibError
from fontTools.ttLib.tables._h_e_a_d import mac_epoch_diff
from fontTools.misc.textTools import num2binary
from fontTools.pens.boundsPen import ControlBoundsPen
from extractor.exceptions import ExtractorError
from extractor.tools import RelaxedInfo, copyAttr

# ----------------
# Public Functions
# ----------------

def isOpenType(pathOrFile):
    try:
        font = TTFont(pathOrFile)
        del font
    except TTLibError:
        return False
    return True

def extractFontFromOpenType(pathOrFile, destination, doGlyphOrder=True, doGlyphs=True, doInfo=True, doKerning=True, customFunctions=[]):
    source = TTFont(pathOrFile)
    if doInfo:
        extractOpenTypeInfo(source, destination)
    if doGlyphs:
        extractOpenTypeGlyphs(source, destination)
    if doGlyphOrder:
        extractGlyphOrder(source, destination)
    if doKerning:
        kerning, groups = extractOpenTypeKerning(source, destination)
        destination.groups.update(groups)
        destination.kerning.clear()
        destination.kerning.update(kerning)
    for function in customFunctions:
        function(source, destination)
    source.close()

def extractGlyphOrder(source, destination):
    glyphOrder = source.getGlyphOrder()
    if len(glyphOrder):
        destination.lib["public.glyphOrder"] = glyphOrder

# ----
# Info
# ----

def extractOpenTypeInfo(source, destination):
    info = RelaxedInfo(destination.info)
    _extractInfoHead(source, info)
    _extractInfoName(source, info)
    _extracInfoOS2(source, info)
    _extractInfoHhea(source, info)
    _extractInfoVhea(source, info)
    _extractInfoPost(source, info)
    _extractInfoCFF(source, info)
    _extractInfoGasp(source, info)

def _extractInfoHead(source, info):
    head = source["head"]
    # version
    version = str(round(head.fontRevision, 3))
    versionMajor, versionMinor = version.split(".")
    info.versionMajor = int(versionMajor)
    info.versionMinor = int(versionMinor)
    # upm
    info.unitsPerEm = head.unitsPerEm
    # created
    format = "%Y/%m/%d %H:%M:%S"
    created = head.created
    created = time.gmtime(max(0, created + mac_epoch_diff))
    info.openTypeHeadCreated = time.strftime(format, created)
    # lowestRecPPEM
    info.openTypeHeadLowestRecPPEM = head.lowestRecPPEM
    # flags
    info.openTypeHeadFlags = binaryToIntList(head.flags)
    # styleMapStyleName
    macStyle = binaryToIntList(head.macStyle)
    styleMapStyleName = "regular"
    if 0 in macStyle and 1 in macStyle:
        styleMapStyleName = "bold italic"
    elif 0 in macStyle:
        styleMapStyleName = "bold"
    elif 1 in macStyle:
        styleMapStyleName = "italic"
    info.styleMapStyleName = styleMapStyleName

def _extractInfoName(source, info):
    records = []
    nameIDs = {}
    for record in source["name"].names:
        nameID = record.nameID
        platformID = record.platformID
        encodingID = record.platEncID
        languageID = record.langID
        string = record.toUnicode()
        nameIDs[nameID, platformID, encodingID, languageID] = string
        records.append((nameID, platformID, encodingID, languageID,
            dict(
                nameID=nameID,
                platformID=platformID,
                encodingID=encodingID,
                languageID=languageID,
                string=string
            )
        ))
    attributes = dict(
        familyName=_priorityOrder(16) + _priorityOrder(1),
        styleName=_priorityOrder(17) + _priorityOrder(2),
        styleMapFamilyName=_priorityOrder(1),
        # styleMapStyleName will be handled in head extraction
        copyright=_priorityOrder(0),
        trademark=_priorityOrder(7),
        openTypeNameDesigner=_priorityOrder(9),
        openTypeNameDesignerURL=_priorityOrder(12),
        openTypeNameManufacturer=_priorityOrder(8),
        openTypeNameManufacturerURL=_priorityOrder(11),
        openTypeNameLicense=_priorityOrder(13),
        openTypeNameLicenseURL=_priorityOrder(14),
        openTypeNameVersion=_priorityOrder(5),
        openTypeNameUniqueID=_priorityOrder(3),
        openTypeNameDescription=_priorityOrder(10),
        openTypeNamePreferredFamilyName=_priorityOrder(16),
        openTypeNamePreferredSubfamilyName=_priorityOrder(17),
        openTypeNameCompatibleFullName=_priorityOrder(18),
        openTypeNameSampleText=_priorityOrder(20),
        openTypeNameWWSFamilyName=_priorityOrder(21),
        openTypeNameWWSSubfamilyName=_priorityOrder(22)
    )
    for attr, priority in attributes.items():
        value = _skimNameIDs(nameIDs, priority)
        if value is not None:
            setattr(info, attr, value)
    info.openTypeNameRecords = [record[-1] for record in sorted(records)]

def _priorityOrder(nameID):
    priority = [
        (nameID, 1, 0, 0),
        (nameID, 1, None, None),
        (nameID, None, None, None)
    ]
    return priority

def _skimNameIDs(nameIDs, priority):
    for (nameID, platformID, platEncID, langID) in priority:
        for (nID, pID, pEID, lID), text in nameIDs.items():
            if nID != nameID:
                continue
            if pID != platformID and platformID is not None:
                continue
            if pEID != platEncID and platEncID is not None:
                continue
            if lID != langID and langID is not None:
                continue
            return text

def _extracInfoOS2(source, info):
    os2 = source["OS/2"]
    # openTypeOS2WidthClass
    copyAttr(os2, "usWidthClass", info, "openTypeOS2WidthClass")
    # openTypeOS2WeightClass
    copyAttr(os2, "usWeightClass", info, "openTypeOS2WeightClass")
    # openTypeOS2Selection
    if hasattr(os2, "fsSelection"):
        fsSelection = binaryToIntList(os2.fsSelection)
        fsSelection = [i for i in fsSelection if i in (1, 2, 3, 4)]
        info.openTypeOS2Selection = fsSelection
    # openTypeOS2VendorID
    copyAttr(os2, "achVendID", info, "openTypeOS2VendorID")
    ## the string could be padded with null bytes. strip those.
    if info.openTypeOS2VendorID.endswith("\x00"):
        r = []
        for c in reversed(info.openTypeOS2VendorID):
            if r or c != "\x00":
                r.insert(0, c)
        info.openTypeOS2VendorID = "".join(r)
    # openTypeOS2Panose
    if hasattr(os2, "panose"):
        panose = os2.panose
        info.openTypeOS2Panose = [
            os2.panose.bFamilyType,
            os2.panose.bSerifStyle,
            os2.panose.bWeight,
            os2.panose.bProportion,
            os2.panose.bContrast,
            os2.panose.bStrokeVariation,
            os2.panose.bArmStyle,
            os2.panose.bLetterForm,
            os2.panose.bMidline,
            os2.panose.bXHeight
        ]
    # openTypeOS2FamilyClass
    # XXX info.openTypeOS2FamilyClass
    if hasattr(os2, "ulUnicodeRange1"):
        info.openTypeOS2UnicodeRanges = binaryToIntList(os2.ulUnicodeRange1) + binaryToIntList(os2.ulUnicodeRange2, 32) + binaryToIntList(os2.ulUnicodeRange3, 64) + binaryToIntList(os2.ulUnicodeRange4, 96)
    if hasattr(os2, "ulCodePageRange1"):
        info.openTypeOS2CodePageRanges = binaryToIntList(os2.ulCodePageRange1) + binaryToIntList(os2.ulCodePageRange2, 32)
    copyAttr(os2, "sxHeight", info, "xHeight")
    copyAttr(os2, "sCapHeight", info, "capHeight")
    copyAttr(os2, "sTypoAscender", info, "ascender")
    copyAttr(os2, "sTypoDescender", info, "descender")
    copyAttr(os2, "sTypoAscender", info, "openTypeOS2TypoAscender")
    copyAttr(os2, "sTypoDescender", info, "openTypeOS2TypoDescender")
    copyAttr(os2, "sTypoLineGap", info, "openTypeOS2TypoLineGap")
    copyAttr(os2, "usWinAscent", info, "openTypeOS2WinAscent")
    copyAttr(os2, "usWinDescent", info, "openTypeOS2WinDescent")
    if hasattr(os2, "fsType"):
        info.openTypeOS2Type = binaryToIntList(os2.fsType)
    copyAttr(os2, "ySubscriptXSize", info, "openTypeOS2SubscriptXSize")
    copyAttr(os2, "ySubscriptYSize", info, "openTypeOS2SubscriptYSize")
    copyAttr(os2, "ySubscriptXOffset", info, "openTypeOS2SubscriptXOffset")
    copyAttr(os2, "ySubscriptYOffset", info, "openTypeOS2SubscriptYOffset")
    copyAttr(os2, "ySuperscriptXSize", info, "openTypeOS2SuperscriptXSize")
    copyAttr(os2, "ySuperscriptYSize", info, "openTypeOS2SuperscriptYSize")
    copyAttr(os2, "ySuperscriptXOffset", info, "openTypeOS2SuperscriptXOffset")
    copyAttr(os2, "ySuperscriptYOffset", info, "openTypeOS2SuperscriptYOffset")
    copyAttr(os2, "yStrikeoutSize", info, "openTypeOS2StrikeoutSize")
    copyAttr(os2, "yStrikeoutPosition", info, "openTypeOS2StrikeoutPosition")

def _extractInfoHhea(source, info):
    if "hhea" not in source:
        return
    hhea = source["hhea"]
    info.openTypeHheaAscender = hhea.ascent
    info.openTypeHheaDescender = hhea.descent
    info.openTypeHheaLineGap = hhea.lineGap
    info.openTypeHheaCaretSlopeRise = hhea.caretSlopeRise
    info.openTypeHheaCaretSlopeRun = hhea.caretSlopeRun
    info.openTypeHheaCaretOffset = hhea.caretOffset

def _extractInfoVhea(source, info):
    if "vhea" not in source:
        return
    vhea = source["vhea"]
    info.openTypeVheaVertTypoAscender = vhea.ascent
    info.openTypeVheaVertTypoDescender = vhea.descent
    info.openTypeVheaVertTypoLineGap = vhea.lineGap
    info.openTypeVheaCaretSlopeRise = vhea.caretSlopeRise
    info.openTypeVheaCaretSlopeRun = vhea.caretSlopeRun
    if hasattr(vhea, "caretOffset"):
        info.openTypeVheaCaretOffset = vhea.caretOffset

def _extractInfoPost(source, info):
    post = source["post"]
    info.italicAngle = post.italicAngle
    info.postscriptUnderlineThickness = post.underlineThickness
    info.postscriptUnderlinePosition = post.underlinePosition
    info.postscriptIsFixedPitch = bool(post.isFixedPitch)

def _extractInfoCFF(source, info):
    if "CFF " not in source:
        return
    cff = source["CFF "].cff
    info.postscriptFontName = cff.fontNames[0]
    # TopDict
    topDict = cff.topDictIndex[0]
    info.postscriptFullName = topDict.rawDict.get("FullName", None)
    info.postscriptWeightName = topDict.rawDict.get("Weight", None)
    # Private
    # CID doesn't have this, so safely extract.
    if hasattr(topDict, "Private"):
        private = topDict.Private
        info.postscriptBlueValues = private.rawDict.get("BlueValues", [])
        info.postscriptOtherBlues = private.rawDict.get("OtherBlues", [])
        info.postscriptFamilyBlues = private.rawDict.get("FamilyBlues", [])
        info.postscriptFamilyOtherBlues = private.rawDict.get("FamilyOtherBlues", [])
        info.postscriptStemSnapH = private.rawDict.get("StemSnapH", [])
        info.postscriptStemSnapV = private.rawDict.get("StemSnapV", [])
        info.postscriptBlueFuzz = private.rawDict.get("BlueFuzz", None)
        info.postscriptBlueShift = private.rawDict.get("BlueShift", None)
        info.postscriptBlueScale = private.rawDict.get("BlueScale", None)
        info.postscriptForceBold = bool(private.rawDict.get("ForceBold", None))
        info.postscriptNominalWidthX = private.rawDict.get("nominalWidthX", None)
        info.postscriptDefaultWidthX = private.rawDict.get("defaultWidthX", None)
    # XXX postscriptSlantAngle
    # XXX postscriptUniqueID

def _extractInfoGasp(source, info):
    if "gasp" not in source:
        return
    gasp = source["gasp"]
    records = []
    for size, bits in sorted(gasp.gaspRange.items()):
        behavior = []
        if bits & 0x0001:
            behavior.append(0)
        if bits & 0x0002:
            behavior.append(1)
        if bits & 0x0004:
            behavior.append(2)
        if bits & 0x0008:
            behavior.append(3)
        record = dict(
            rangeMaxPPEM=size,
            rangeGaspBehavior=behavior
        )
        records.append(record)
    info.openTypeGaspRangeRecords = records

# Tools

def binaryToIntList(value, start=0):
    intList = []
    counter = start
    while value:
        if value & 1:
            intList.append(counter)
        value >>= 1
        counter += 1
    return intList

# --------
# Outlines
# --------

def extractOpenTypeGlyphs(source, destination):
    # grab the cmap
    cmap = source["cmap"]
    vmtx = source.get("vmtx")
    vorg = source.get("VORG")
    preferred = [
        (3, 10, 12),
        (3, 10, 4),
        (3, 1, 12),
        (3, 1, 4),
        (0, 3, 12),
        (0, 3, 4),
        (3, 0, 12),
        (3, 0, 4),
        (1, 0, 12),
        (1, 0, 4)
    ]
    found = {}
    for table in cmap.tables:
        found[table.platformID, table.platEncID, table.format] = table
        table = None
    for key in preferred:
        if key not in found:
            continue
        table = found[key]
        break
    reversedMapping = {}
    if table is not None:
        for uniValue, glyphName in table.cmap.items():
            reversedMapping[glyphName] = uniValue
    # grab the glyphs
    glyphSet = source.getGlyphSet()
    for glyphName in glyphSet.keys():
        sourceGlyph = glyphSet[glyphName]
        # make the new glyph
        destination.newGlyph(glyphName)
        destinationGlyph = destination[glyphName]
        # outlines
        pen = destinationGlyph.getPen()
        sourceGlyph.draw(pen)
        # width
        destinationGlyph.width = sourceGlyph.width
        # height and vertical origin
        if vmtx is not None and glyphName in vmtx.metrics:
            destinationGlyph.height = vmtx[glyphName][0]
            if vorg is not None:
                if glyphName in vorg.VOriginRecords:
                    destinationGlyph.verticalOrigin = vorg[glyphName]
                else:
                    destinationGlyph.verticalOrigin = vorg.defaultVertOriginY
            else:
                tsb = vmtx[glyphName][1]
                bounds_pen = ControlBoundsPen(glyphSet)
                sourceGlyph.draw(bounds_pen)
                if bounds_pen.bounds is None:
                    continue
                xMin, yMin, xMax, yMax = bounds_pen.bounds
                destinationGlyph.verticalOrigin = tsb + yMax
        # unicode
        destinationGlyph.unicode = reversedMapping.get(glyphName)

# -------
# Kerning
# -------

def extractOpenTypeKerning(source, destination):
    kerning = {}
    groups = {}
    if "GPOS" in source:
        kerning, groups = _extractOpenTypeKerningFromGPOS(source)
    elif "kern" in source:
        kerning = _extractOpenTypeKerningFromKern(source)
        groups = {}
    for name, group in groups.items():
        groups[name] = list(sorted(group))
    return kerning, groups

def _extractOpenTypeKerningFromGPOS(source):
    gpos = source["GPOS"].table
    # get an ordered list of scripts
    scriptOrder = _makeScriptOrder(gpos)
    # extract kerning and classes from each applicable lookup
    kerningDictionaries, leftClassDictionaries, rightClassDictionaries = _gatherDataFromLookups(gpos, scriptOrder)
    # merge all kerning pairs
    kerning = _mergeKerningDictionaries(kerningDictionaries)
    # get rid of groups that have only one member
    leftSingleMemberGroups = _findSingleMemberGroups(leftClassDictionaries)
    rightSingleMemberGroups = _findSingleMemberGroups(rightClassDictionaries)
    # filter out the single glyph groups from the kerning
    kerning = _removeSingleMemberGroupReferences(kerning, leftSingleMemberGroups, rightSingleMemberGroups)
    # merge groups that have the exact same member list
    leftClasses, leftClassRename = _mergeClasses(leftClassDictionaries)
    rightClasses, rightClassRename = _mergeClasses(rightClassDictionaries)
    # search for overlapping groups and raise an error if any were found
    _validateClasses(leftClasses)
    _validateClasses(rightClasses)
    # populate the class marging into the kerning
    kerning = _replaceRenamedPairMembers(kerning, leftClassRename, rightClassRename)
    # rename the groups to final names
    leftClassRename = _renameClasses(leftClasses, "public.kern1.")
    rightClassRename = _renameClasses(rightClasses, "public.kern2.")
    # populate the final group names
    kerning = _replaceRenamedPairMembers(kerning, leftClassRename, rightClassRename)
    leftGroups = _setGroupNames(leftClasses, leftClassRename)
    rightGroups = _setGroupNames(rightClasses, rightClassRename)
    # combine the side groups
    groups = {}
    groups.update(leftGroups)
    groups.update(rightGroups)
    # done.
    return kerning, groups

def _makeScriptOrder(gpos):
    """
    Run therough GPOS and make an alphabetically
    ordered list of scripts. If DFLT is in the list,
    move it to the front.
    """
    scripts = []
    for scriptRecord in gpos.ScriptList.ScriptRecord:
        scripts.append(scriptRecord.ScriptTag)
    if "DFLT" in scripts:
        scripts.remove("DFLT")
        scripts.insert(0, "DFLT")
    return sorted(scripts)

def _gatherDataFromLookups(gpos, scriptOrder):
    """
    Gather kerning and classes from the applicable lookups
    and return them in script order.
    """
    lookupIndexes = _gatherLookupIndexes(gpos)
    seenLookups = set()
    kerningDictionaries = []
    leftClassDictionaries = []
    rightClassDictionaries = []
    for script in scriptOrder:
        kerning = []
        leftClasses = []
        rightClasses = []
        for lookupIndex in lookupIndexes[script]:
            if lookupIndex in seenLookups:
                continue
            seenLookups.add(lookupIndex)
            result = _gatherKerningForLookup(gpos, lookupIndex)
            if result is None:
                continue
            k, lG, rG = result
            kerning.append(k)
            leftClasses.append(lG)
            rightClasses.append(rG)
        if kerning:
            kerningDictionaries.append(kerning)
            leftClassDictionaries.append(leftClasses)
            rightClassDictionaries.append(rightClasses)
    return kerningDictionaries, leftClassDictionaries, rightClassDictionaries

def _gatherLookupIndexes(gpos):
    """
    Gather a mapping of script to lookup indexes
    referenced by the kern feature for each script.
    Returns a dictionary of this structure:
        {
            "latn" : [0],
            "DFLT" : [0]
        }
    """
    # gather the indexes of the kern features
    kernFeatureIndexes = [index for index, featureRecord in enumerate(gpos.FeatureList.FeatureRecord) if featureRecord.FeatureTag == "kern"]
    # find scripts and languages that have kern features
    scriptKernFeatureIndexes = {}
    for scriptRecord in gpos.ScriptList.ScriptRecord:
        script = scriptRecord.ScriptTag
        thisScriptKernFeatureIndexes = []
        defaultLangSysRecord = scriptRecord.Script.DefaultLangSys
        if defaultLangSysRecord is not None:
            f = []
            for featureIndex in defaultLangSysRecord.FeatureIndex:
                if featureIndex not in kernFeatureIndexes:
                    continue
                f.append(featureIndex)
            if f:
                thisScriptKernFeatureIndexes.append((None, f))
        if scriptRecord.Script.LangSysRecord is not None:
            for langSysRecord in scriptRecord.Script.LangSysRecord:
                langSys = langSysRecord.LangSysTag
                f = []
                for featureIndex in langSysRecord.LangSys.FeatureIndex:
                    if featureIndex not in kernFeatureIndexes:
                        continue
                    f.append(featureIndex)
                if f:
                    thisScriptKernFeatureIndexes.append((langSys, f))
        scriptKernFeatureIndexes[script] = thisScriptKernFeatureIndexes
    # convert the feature indexes to lookup indexes
    scriptLookupIndexes = {}
    for script, featureDefinitions in scriptKernFeatureIndexes.items():
        lookupIndexes = scriptLookupIndexes[script] = []
        for language, featureIndexes in featureDefinitions:
            for featureIndex in featureIndexes:
                featureRecord = gpos.FeatureList.FeatureRecord[featureIndex]
                for lookupIndex in featureRecord.Feature.LookupListIndex:
                    if lookupIndex not in lookupIndexes:
                        lookupIndexes.append(lookupIndex)
    # done
    return scriptLookupIndexes

def _gatherKerningForLookup(gpos, lookupIndex):
    """
    Gather the kerning and class data for a particular lookup.
    Returns kerning, left clases, right classes.
    The kerning dictionary is of this structure:
        {
            ("a", "a") : 10,
            ((1, 1, 3), "a") : -20
        }
    The class dictionaries have this structure:
        {
            (1, 1, 3) : ["x", "y", "z"]
        }
    Where the tuple means this:
        (lookup index, subtable index, class index)
    """
    allKerning = {}
    allLeftClasses = {}
    allRightClasses = {}
    lookup = gpos.LookupList.Lookup[lookupIndex]
    # only handle pair positioning and extension
    if lookup.LookupType not in (2, 9):
        return
    for subtableIndex, subtable in enumerate(lookup.SubTable):
        if lookup.LookupType == 2:
            format = subtable.Format
            lookupType = subtable.LookupType
            if (lookupType, format) == (2, 1):
                kerning = _handleLookupType2Format1(subtable)
                allKerning.update(kerning)
            elif (lookupType, format) == (2, 2):
                kerning, leftClasses, rightClasses = _handleLookupType2Format2(subtable, lookupIndex, subtableIndex)
                allKerning.update(kerning)
                allLeftClasses.update(leftClasses)
                allRightClasses.update(rightClasses)
        elif lookup.LookupType == 9:
            extSubtable = subtable.ExtSubTable
            format = extSubtable.Format
            lookupType = extSubtable.LookupType
            if (lookupType, format) == (2, 1):
                kerning = _handleLookupType2Format1(extSubtable)
                allKerning.update(kerning)
            elif (lookupType, format) == (2, 2):
                kerning, leftClasses, rightClasses = _handleLookupType2Format2(extSubtable, lookupIndex, subtableIndex)
                allKerning.update(kerning)
                allLeftClasses.update(leftClasses)
                allRightClasses.update(rightClasses)
    # done
    return allKerning, allLeftClasses, allRightClasses

def _handleLookupType2Format1(subtable):
    """
    Extract a kerning dictionary from a Lookup Type 2 Format 1.
    """
    kerning = {}
    coverage = subtable.Coverage.glyphs
    valueFormat1 = subtable.ValueFormat1
    pairSets = subtable.PairSet
    for index, leftGlyphName in enumerate(coverage):
        pairSet = pairSets[index]
        for pairValueRecord in pairSet.PairValueRecord:
            rightGlyphName = pairValueRecord.SecondGlyph
            if valueFormat1:
                value = pairValueRecord.Value1
            else:
                value = pairValueRecord.Value2
            if hasattr(value, "XAdvance"):
                value = value.XAdvance
                kerning[leftGlyphName, rightGlyphName] = value
    return kerning

def _handleLookupType2Format2(subtable, lookupIndex, subtableIndex):
    """
    Extract kerning, left class and right class dictionaries from a Lookup Type 2 Format 2.
    """
    # extract the classes
    leftClasses = _extractFeatureClasses(lookupIndex=lookupIndex, subtableIndex=subtableIndex, classDefs=subtable.ClassDef1.classDefs, coverage=subtable.Coverage.glyphs)
    rightClasses = _extractFeatureClasses(lookupIndex=lookupIndex, subtableIndex=subtableIndex, classDefs=subtable.ClassDef2.classDefs)
    # extract the pairs
    kerning = {}
    for class1RecordIndex, class1Record in enumerate(subtable.Class1Record):
        for class2RecordIndex, class2Record in enumerate(class1Record.Class2Record):
            leftClass = (lookupIndex, subtableIndex, class1RecordIndex)
            rightClass = (lookupIndex, subtableIndex, class2RecordIndex)
            valueFormat1 = subtable.ValueFormat1
            if valueFormat1:
                value = class2Record.Value1
            else:
                value = class2Record.Value2
            if hasattr(value, "XAdvance") and value.XAdvance != 0:
                value = value.XAdvance
                kerning[leftClass, rightClass] = value
    return kerning, leftClasses, rightClasses

def _mergeKerningDictionaries(kerningDictionaries):
    """
    Merge all of the kerning dictionaries found into
    one flat dictionary.
    """
    # work through the dictionaries backwards since
    # this uses an update to load the kerning. this
    # will ensure that the script order is honored.
    kerning = {}
    for dictionaryGroup in reversed(kerningDictionaries):
        for dictionary in dictionaryGroup:
            kerning.update(dictionary)
    # done.
    return kerning

def _findSingleMemberGroups(classDictionaries):
    """
    Find all classes that have only one member.
    """
    toRemove = {}
    for classDictionaryGroup in classDictionaries:
        for classDictionary in classDictionaryGroup:
            for name, members in list(classDictionary.items()):
                if len(members) == 1:
                    toRemove[name] = list(members)[0]
                    del classDictionary[name]
    return toRemove

def _removeSingleMemberGroupReferences(kerning, leftGroups, rightGroups):
    """
    Translate group names into glyph names in pairs
    if the group only contains one glyph.
    """
    new = {}
    for (left, right), value in kerning.items():
        left = leftGroups.get(left, left)
        right = rightGroups.get(right, right)
        new[left, right] = value
    return new

def _mergeClasses(classDictionaries):
    """
    Look for classes that have the exact same list
    of members and flag them for removal.
    This returns left classes, left rename map,
    right classes and right rename map.
    The classes have the standard class structure.
    The rename maps have this structure:
        {
            (1, 1, 3) : (2, 3, 4),
            old name : new name
        }
    Where the key is the class that should be
    preserved and the value is a list of classes
    that should be removed.
    """
    # build a mapping of members to names
    memberTree = {}
    for classDictionaryGroup in classDictionaries:
        for classDictionary in classDictionaryGroup:
            for name, members in classDictionary.items():
                if members not in memberTree:
                    memberTree[members] = set()
                memberTree[members].add(name)
    # find members that have more than one name
    classes = {}
    rename = {}
    for members, names in memberTree.items():
        name = names.pop()
        if len(names) > 0:
            for otherName in names:
                rename[otherName] = name
        classes[name] = members
    return classes, rename

def _setGroupNames(classes, classRename):
    """
    Set the final names into the groups.
    """
    groups = {}
    for groupName, glyphList in classes.items():
        groupName = classRename.get(groupName, groupName)
        # if the glyph list has only one member,
        # the glyph name will be used in the pairs.
        # no group is needed.
        if len(glyphList) == 1:
            continue
        groups[groupName] = glyphList
    return groups

def _validateClasses(classes):
    """
    Check to make sure that a glyph is not part of more than
    one class. If this is found, an ExtractorError is raised.
    """
    glyphToClass = {}
    for className, glyphList in classes.items():
        for glyphName in glyphList:
            if glyphName not in glyphToClass:
                glyphToClass[glyphName] = set()
            glyphToClass[glyphName].add(className)
    conflicts = 0
    for glyphName, groupList in glyphToClass.items():
        if len(groupList) > 1:
            print('Conflicting kerning classes for %s:' % glyphName)
            for groupId in groupList:
                group = classes[groupId]
                print('  %r => %s' % (groupId, ', '.join(group)))
            conflicts += 1
    if conflicts > 0:
        raise ExtractorError("Kerning classes are in an conflicting state")

def _replaceRenamedPairMembers(kerning, leftRename, rightRename):
    """
    Populate the renamed pair members into the kerning.
    """
    renamedKerning = {}
    for (left, right), value in kerning.items():
        left = leftRename.get(left, left)
        right = rightRename.get(right, right)
        renamedKerning[left, right] = value
    return renamedKerning

def _renameClasses(classes, prefix):
    """
    Replace class IDs with nice strings.
    """
    renameMap = {}
    for classID, glyphList in classes.items():
        if len(glyphList) == 0:
            groupName = "%s_empty_lu.%d_st.%d_cl.%d" % (prefix, classID[0], classID[1], classID[2])
        elif len(glyphList) == 1:
            groupName = list(glyphList)[0]
        else:
            glyphList = list(sorted(glyphList))
            groupName = prefix + glyphList[0]
        renameMap[classID] = groupName
    return renameMap

def _extractFeatureClasses(lookupIndex, subtableIndex, classDefs, coverage=None):
    """
    Extract classes for a specific lookup in a specific subtable.
    This is relatively straightforward, except for class 0 interpretation.
    Some fonts don't have class 0. Some fonts have a list of class
    members that are clearly not all to be used in kerning pairs.
    In the case of a missing class 0, the coverage is used as a basis
    for the class and glyph names used in classed 1+ are filtered out.
    In the case of class 0 having glyph names that are not part of the
    kerning pairs, the coverage is used to filter out the unnecessary
    glyph names.
    """
    # gather the class members
    classDict = {}
    for glyphName, classIndex in classDefs.items():
        if classIndex not in classDict:
            classDict[classIndex] = set()
        classDict[classIndex].add(glyphName)
    # specially handle class index 0
    revisedClass0 = set()
    if coverage is not None and 0 in classDict:
        for glyphName in classDict[0]:
            if glyphName in coverage:
                revisedClass0.add(glyphName)
    elif coverage is not None and 0 not in classDict:
        revisedClass0 = set(coverage)
        for glyphList in classDict.values():
            revisedClass0 = revisedClass0 - glyphList
    classDict[0] = revisedClass0
    # flip the class map around
    classes = {}
    for classIndex, glyphList in classDict.items():
        classes[lookupIndex, subtableIndex, classIndex] = frozenset(glyphList)
    return classes

def _extractOpenTypeKerningFromKern(source):
    kern = source["kern"]
    kerning = {}
    for subtable in kern.kernTables:
        if subtable.version != 0:
            raise ExtractorError("Unknown kern table formst: %d" % subtable.version)
        # XXX the spec defines coverage values for
        # kerning direction (horizontal or vertical)
        # minimum (some sort of kerning restriction)
        # cross-stream (direction of the kerns within the direction of the table. odd.)
        # override (if the values in this subtable should override the values of others)
        # however, it is vague about how these should be stored.
        # as such, we just assume that the direction is horizontal,
        # that the values of all subtables are additive and that
        # there are no minimum values.
        kerning.update(subtable.kernTable)
    return kerning
