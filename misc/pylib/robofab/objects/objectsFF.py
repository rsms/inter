

__DEBUG__ = True
__version__ = "0.2"

"""
	RoboFab API Objects for FontForge
	http://fontforge.sourceforge.net

    FontForge python docs:
    http://fontforge.sourceforge.net/python.html
    
    Note: This is dead. EvB: "objectsFF.py is very dead and should only serve as an example of "dead"
    
    History
    Version zero. May 2007. EvB
        Experiment to see how far the API can be made to work.

    0.1 extended testing and comparisons for attributes.
	0.2 checked into svn. Still quite raw. Lots of print statements and tests at the end.

	Notes
	This code is best used with fontforge compiled as a python extension.

	FontForge Python API:
        __doc__
        str(object) -> string

        Return a nice string representation of the object.
        If the argument is a string, the return value is the same object.

        __file__
        str(object) -> string

        Return a nice string representation of the object.
        If the argument is a string, the return value is the same object.

        __name__
        str(object) -> string

        Return a nice string representation of the object.
        If the argument is a string, the return value is the same object.

        activeFont
        If invoked from the UI, this returns the currently active font. When not in UI this returns None

        activeFontInUI
        If invoked from the UI, this returns the currently active font. When not in UI this returns None

        activeGlyph
        If invoked from the UI, this returns the currently active glyph (or None)

        ask
        Pops up a dialog asking the user a question and providing a set of buttons for the user to reply with

        askChoices
        Pops up a dialog asking the user a question and providing a scrolling list for the user to reply with

        askString
        Pops up a dialog asking the user a question and providing a textfield for the user to reply with

        contour
        fontforge Contour objects

        contouriter
        None

        cvt
        fontforge cvt objects

        defaultOtherSubrs
        Use FontForge's default "othersubrs" functions for Type1 fonts

        font
        FontForge Font object

        fontiter
        None

        fonts
        Returns a tuple of all loaded fonts

        fontsInFile
        Returns a tuple containing the names of any fonts in an external file

        getPrefs
        Get FontForge preference items

        glyph
        FontForge GlyphPen object

        glyphPen
        FontForge Glyph object

        hasSpiro
        Returns whether this fontforge has access to Raph Levien's spiro package

        hasUserInterface
        Returns whether this fontforge session has a user interface (True if it has opened windows) or is just running a script (False)

        hooks
        dict() -> new empty dictionary.
        dict(mapping) -> new dictionary initialized from a mapping object's
            (key, value) pairs.
        dict(seq) -> new dictionary initialized as if via:
            d = {}
            for k, v in seq:
                d[k] = v
        dict(**kwargs) -> new dictionary initialized with the name=value pairs
            in the keyword argument list.  For example:  dict(one=1, two=2)

        layer
        fontforge Layer objects

        layeriter
        None

        loadEncodingFile
        Load an encoding file into the list of encodings

        loadNamelist
        Load a namelist into the list of namelists

        loadNamelistDir
        Load a directory of namelist files into the list of namelists

        loadPlugin
        Load a FontForge plugin

        loadPluginDir
        Load a directory of FontForge plugin files

        loadPrefs
        Load FontForge preference items

        logWarning
        Adds a non-fatal message to the Warnings window

        open
        Opens a font and returns it

        openFilename
        Pops up a file picker dialog asking the user for a filename to open

        parseTTInstrs
        Takes a string and parses it into a tuple of truetype instruction bytes

        point
        fontforge Point objects

        postError
        Pops up an error dialog box with the given title and message

        postNotice
        Pops up an notice window with the given title and message

        preloadCidmap
        Load a cidmap file

        printSetup
        Prepare to print a font sample (select default printer or file, page size, etc.)

        private
        FontForge private dictionary

        privateiter
        None

        readOtherSubrsFile
        Read from a file, "othersubrs" functions for Type1 fonts

        registerImportExport
        Adds an import/export spline conversion module

        registerMenuItem
        Adds a menu item (which runs a python script) to the font or glyph (or both) windows -- in the Tools menu

        saveFilename
        Pops up a file picker dialog asking the user for a filename to use for saving

        savePrefs
        Save FontForge preference items

        selection
        fontforge selection objects

        setPrefs
        Set FontForge preference items

        spiroCorner
        int(x[, base]) -> integer

        Convert a string or number to an integer, if possible.  A floating point
        argument will be truncated towards zero (this does not include a string
        representation of a floating point number!)  When converting a string, use
        the optional base.  It is an error to supply a base when converting a
        non-string. If the argument is outside the integer range a long object
        will be returned instead.

        spiroG2
        int(x[, base]) -> integer

        Convert a string or number to an integer, if possible.  A floating point
        argument will be truncated towards zero (this does not include a string
        representation of a floating point number!)  When converting a string, use
        the optional base.  It is an error to supply a base when converting a
        non-string. If the argument is outside the integer range a long object
        will be returned instead.

        spiroG4
        int(x[, base]) -> integer

        Convert a string or number to an integer, if possible.  A floating point
        argument will be truncated towards zero (this does not include a string
        representation of a floating point number!)  When converting a string, use
        the optional base.  It is an error to supply a base when converting a
        non-string. If the argument is outside the integer range a long object
        will be returned instead.

        spiroLeft
        int(x[, base]) -> integer

        Convert a string or number to an integer, if possible.  A floating point
        argument will be truncated towards zero (this does not include a string
        representation of a floating point number!)  When converting a string, use
        the optional base.  It is an error to supply a base when converting a
        non-string. If the argument is outside the integer range a long object
        will be returned instead.

        spiroOpen
        int(x[, base]) -> integer

        Convert a string or number to an integer, if possible.  A floating point
        argument will be truncated towards zero (this does not include a string
        representation of a floating point number!)  When converting a string, use
        the optional base.  It is an error to supply a base when converting a
        non-string. If the argument is outside the integer range a long object
        will be returned instead.

        spiroRight
        int(x[, base]) -> integer

        Convert a string or number to an integer, if possible.  A floating point
        argument will be truncated towards zero (this does not include a string
        representation of a floating point number!)  When converting a string, use
        the optional base.  It is an error to supply a base when converting a
        non-string. If the argument is outside the integer range a long object
        will be returned instead.

        unParseTTInstrs
        Takes a tuple of truetype instruction bytes and converts to a human readable string

        unicodeFromName
        Given a name, look it up in the namelists and find what unicode code point it maps to (returns -1 if not found)

        version
        Returns a string containing the current version of FontForge, as 20061116




Problems:
    XXX: reading glif from UFO: is the contour order changed in some way?
        
    
ToDo:
    - segments ?
    

"""

import os
from robofab.objects.objectsBase import BaseFont, BaseGlyph, BaseContour, BaseSegment,\
        BasePoint, BaseBPoint, BaseAnchor, BaseGuide, BaseComponent, BaseKerning, BaseInfo, BaseGroups, BaseLib,\
        roundPt, addPt, _box,\
        MOVE, LINE, CORNER, CURVE, QCURVE, OFFCURVE,\
        relativeBCPIn, relativeBCPOut, absoluteBCPIn, absoluteBCPOut
        
from robofab.objects.objectsRF import RGlyph as _RGlyph
        
import fontforge
import psMat


# a list of attributes that are to be copied when copying a glyph.
# this is used by glyph.copy and font.insertGlyph
GLYPH_COPY_ATTRS = [
    "name",
    "width",
    "unicodes",
    "note",
    "lib",
    ]



def CurrentFont():
    if fontforge.hasUserInterface():
        _font = fontforge.activeFontInUI()
        return RFont(_font)
    if __DEBUG__:
        print "CurrentFont(): fontforge not running with user interface,"
    return None
    
def OpenFont(fontPath):
    obj = fontforge.open(fontPath)
    if __DEBUG__:
        print "OpenFont", fontPath
        print "result:", obj
    return RFont(obj)
    
def NewFont(fontPath=None):
    _font = fontforge.font()
    if __DEBUG__:
        print "NewFont", fontPath
        print "result:", _font
    return RFont(_font)
    
    


class RFont(BaseFont):
    def __init__(self, font=None):
        if font is None:
            # make a new font
            pass
        else:
            self._object = font
    
    # -----------------------------------------------------------------
    #
    #   access

    def keys(self):
        """FF implements __iter__ for the font object - better?"""
        return [n.glyphname for n in self._object.glyphs()]
    
    def has_key(self, glyphName):
        return glyphName in self
        
    def _get_info(self):
        return RInfo(self._object)

    info = property(_get_info, doc="font info object")

    def __iter__(self):
        for glyphName in self.keys():
            yield self.getGlyph(glyphName)

    
    # -----------------------------------------------------------------
    #
    #   file

    def _get_path(self):
        return self._object.path
        
    path = property(_get_path, doc="path of this file")
    
    def __contains__(self, glyphName):
        return glyphName in self.keys()
    
    def save(self, path=None):
        """Save this font as sfd file.
        XXX: how to set a sfd path if is none
        """
        if path is not None:
            # trying to save it somewhere else
            _path = path
        else:
            _path = self.path
        if os.path.splitext(_path)[-1] != ".sfd":
            _path = os.path.splitext(_path)[0]+".sfd"
        if __DEBUG__:
            print "RFont.save() to", _path
        self._object.save(_path)

    def naked(self):
        return self._object
    
    def close(self):
        if __DEBUG__:
            print "RFont.close()"
        self._object.close()
        

    # -----------------------------------------------------------------
    #
    #   generate
    
    def dummyGeneratePreHook(self, *args):
        print "dummyGeneratePreHook", args
    
    def dummyGeneratePostHook(self, *args):
        print "dummyGeneratePostHook", args

    def generate(self, outputType, path=None):
        """
        generate the font. outputType is the type of font to ouput.
        --Ouput Types:
        'pctype1'   :   PC Type 1 font (binary/PFB)
        'pcmm'      :   PC MultipleMaster font (PFB)
        'pctype1ascii'  :   PC Type 1 font (ASCII/PFA)
        'pcmmascii' :   PC MultipleMaster font (ASCII/PFA)
        'unixascii' :   UNIX ASCII font (ASCII/PFA)
        'mactype1'  :   Mac Type 1 font (generates suitcase  and LWFN file)
        'otfcff'        :   PS OpenType (CFF-based) font (OTF)
        'otfttf'        :   PC TrueType/TT OpenType font (TTF)
        'macttf'    :   Mac TrueType font (generates suitcase)
        'macttdfont'    :   Mac TrueType font (generates suitcase with resources in data fork)
                    (doc adapted from http://dev.fontlab.net/flpydoc/)
        
        path can be a directory or a directory file name combo:
        path="DirectoryA/DirectoryB"
        path="DirectoryA/DirectoryB/MyFontName"
        if no path is given, the file will be output in the same directory
        as the vfb file. if no file name is given, the filename will be the
        vfb file name with the appropriate suffix.
        """
        
        extensions = {
            'pctype1': 'pfm',
            'otfcff': 'otf',
        }

        if __DEBUG__:
            print "font.generate", outputType, path
        
        # set pre and post hooks (necessary?)
        temp = getattr(self._object, "temporary")
        if temp is None:
            self._object.temporary = {}
        else:
            if type(self._object.temporary)!=dict:
                self._object.temporary = {}
        self._object.temporary['generateFontPreHook'] = self.dummyGeneratePreHook
        self._object.temporary['generateFontPostHook'] = self.dummyGeneratePostHook
        
        # make a path for the destination
        if path is None:
            fileName = os.path.splitext(os.path.basename(self.path))[0]
            dirName = os.path.dirname(self.path)
            extension = extensions.get(outputType)
            if extension is not None:
                fileName = "%s.%s"%(fileName, extension)
            else:
                if __DEBUG__:
                    print "can't generate font in %s format"%outputType
                    return
            path = os.path.join(dirName, fileName)
        
        # prepare OTF fields
        generateFlags = []
        generateFlags.append('opentype')
        # generate
        self._object.generate(filename=path, flags=generateFlags)
        if __DEBUG__:
            print "font.generate():", path
        return path


    # -----------------------------------------------------------------
    #
    #   kerning stuff

    def _get_kerning(self):
        kerning = {}
        f = self._object
        for g in f.glyphs:
            for p in g.kerning:
                try:
                    key = (g.name, f[p.key].name)
                    kerning[key] = p.value
                except AttributeError: pass #catch for TT exception
        rk = RKerning(kerning)
        rk.setParent(self)
        return rk

    kerning = property(_get_kerning, doc="a kerning object")

    # -----------------------------------------------------------------
    #
    #   glyph stuff
        
    def getGlyph(self, glyphName):
        try:
            ffGlyph = self._object[glyphName]
        except TypeError:
            print "font.getGlyph, can't find glyphName, returning new glyph"
            return self.newGlyph(glyphName)
        glyph = RGlyph(ffGlyph)
        glyph.setParent(self)
        return glyph

    def newGlyph(self, glyphName, clear=True):
        """Make a new glyph
        
        Notes: not sure how to make a new glyph without an encoded name.
        createChar() seems to be intended for that, but when I pass it -1
        for the unicode, it complains that it wants -1. Perhaps a bug?
        """
        # is the glyph already there?
        glyph = None
        if glyphName in self:
            if clear:
                self._object[glyphName].clear()
                return self[glyphName]
        else:
            # is the glyph in an encodable place:
            slot = self._object.findEncodingSlot(glyphName)
            if slot == -1:
                # not encoded
                print "font.newGlyph: unencoded slot", slot, glyphName
                glyph = self._object.createChar(-1, glyphName)
            else:
                glyph = self._object.createMappedChar(glyphName)
        glyph = RGlyph(self._object[glyphName])
        glyph.setParent(self)
        return glyph
        
    def removeGlyph(self, glyphName):
        self._object.removeGlyph(glyphName)
    
    


class RGlyph(BaseGlyph):
    """Fab wrapper for FF Glyph object"""
    def __init__(self, ffGlyph=None):
        if ffGlyph is None:
            raise RoboFabError
        self._object = ffGlyph
        # XX anchors seem to be supported, but in a different way
        # XX so, I will ignore them for now to get something working.
        self.anchors = []
        self.lib = {}
        
    def naked(self):
        return self._object
        
    def setChanged(self):
        self._object.changed()
        

    # -----------------------------------------------------------------
    #
    #   attributes

    def _get_name(self):
        return self._object.glyphname
    def _set_name(self, value):
        self._object.glyphname = value
    name = property(_get_name, _set_name, doc="name")
    
    def _get_note(self):
        return self._object.comment
    def _set_note(self, note):
        self._object.comment = note
    note = property(_get_note, _set_note, doc="note")

    def _get_width(self):
        return self._object.width
    def _set_width(self, width):
        self._object.width = width
    width = property(_get_width, _set_width, doc="width")
    
    def _get_leftMargin(self):
        return self._object.left_side_bearing
    def _set_leftMargin(self, leftMargin):
        self._object.left_side_bearing = leftMargin
    leftMargin = property(_get_leftMargin, _set_leftMargin, doc="leftMargin")
    
    def _get_rightMargin(self):
        return self._object.right_side_bearing
    def _set_rightMargin(self, rightMargin):
        self._object.right_side_bearing = rightMargin
    rightMargin = property(_get_rightMargin, _set_rightMargin, doc="rightMargin")
    
    def _get_unicodes(self):
        return [self._object.unicode]
    def _set_unicodes(self, unicodes):
        assert len(unicodes)==1
        self._object.unicode = unicodes[0]
    unicodes = property(_get_unicodes, _set_unicodes, doc="unicodes")

    def _get_unicode(self):
        return self._object.unicode
    def _set_unicode(self, unicode):
        self._object.unicode = unicode
    unicode = property(_get_unicode, _set_unicode, doc="unicode")
    
    def _get_box(self):
        bounds = self._object.boundingBox()
        return bounds
    box = property(_get_box, doc="the bounding box of the glyph: (xMin, yMin, xMax, yMax)")
    
    def _get_mark(self):
        """color of the glyph box in the font view. This accepts a 6 hex digit number.
        
        XXX the FL implementation accepts a 
        """
        import colorsys
        r = (self._object.color&0xff0000)>>16
        g = (self._object.color&0xff00)>>8
        g = (self._object.color&0xff)>>4
        return colorsys.rgb_to_hsv( r, g, b)[0]
    
    def _set_mark(self, markColor=-1):
        import colorsys
        self._object.color = colorSys.hsv_to_rgb(markColor, 1, 1)
            
    mark = property(_get_mark, _set_mark, doc="the color of the glyph box in the font view")

    
    # -----------------------------------------------------------------
    #
    #   pen, drawing

    def getPen(self):
        return self._object.glyphPen()
    
    def __getPointPen(self):
        """Return a point pen.
        
        Note: FontForge doesn't support segment pen, so return an adapter.
        """
        from robofab.pens.adapterPens import PointToSegmentPen
        segmentPen = self._object.glyphPen()
        return PointToSegmentPen(segmentPen)
    
    def getPointPen(self):
        from robofab.pens.rfUFOPen import RFUFOPointPen
        pen = RFUFOPointPen(self)
        #print "getPointPen", pen, pen.__class__, dir(pen)
        return pen
        
    def draw(self, pen):
        """draw
        
        """
        self._object.draw(pen)
        pen = None

    def drawPoints(self, pen):
        """drawPoints
        
        Note: FontForge implements glyph.draw, but not glyph.drawPoints.
        """
        from robofab.pens.adapterPens import PointToSegmentPen, SegmentToPointPen
        adapter = SegmentToPointPen(pen)
        self._object.draw(adapter)
        pen = None
        
    def appendGlyph(self, other):
        pen = self.getPen()
        other.draw(pen)

    # -----------------------------------------------------------------
    #
    #   glyphmath

    def round(self):
        self._object.round()
        
    def _getMathDestination(self):
        from robofab.objects.objectsRF import RGlyph as _RGlyph
        return _RGlyph()

    def _mathCopy(self):
        # copy self without contour, component and anchor data
        glyph = self._getMathDestination()
        glyph.name = self.name
        glyph.unicodes = list(self.unicodes)
        glyph.width = self.width
        glyph.note = self.note
        glyph.lib = dict(self.lib)
        return glyph

    def __mul__(self, factor):
        if __DEBUG__:
            print "glyphmath mul", factor
        return self.copy() *factor

    __rmul__ = __mul__

    def __sub__(self, other):
        if __DEBUG__:
            print "glyphmath sub", other, other.__class__
        return self.copy() - other.copy()

    def __add__(self, other):
        if __DEBUG__:
            print "glyphmath add", other, other.__class__
        return self.copy() + other.copy()

    def getParent(self):
        return self
    
    def copy(self, aParent=None):
        """Make a copy of this glyph.
        Note: the copy is not a duplicate fontlab glyph, but
        a RF RGlyph with the same outlines. The new glyph is
        not part of the fontlab font in any way. Use font.appendGlyph(glyph)
        to get it in a FontLab glyph again."""
        from robofab.objects.objectsRF import RGlyph as _RGlyph
        newGlyph = _RGlyph()
        newGlyph.appendGlyph(self)
        for attr in GLYPH_COPY_ATTRS:
            value = getattr(self, attr)
            setattr(newGlyph, attr, value)
        parent = self.getParent()
        if aParent is not None:
            newGlyph.setParent(aParent)
        elif self.getParent() is not None:
            newGlyph.setParent(self.getParent())
        return newGlyph
    
    def _get_contours(self):
        # find the contour data and wrap it
        
        """get the contours in this glyph"""
        contours = []
        for n in range(len(self._object.foreground)):
            item = self._object.foreground[n]
            rc = RContour(item, n)
            rc.setParent(self)
            contours.append(rc)
        #print contours
        return contours
    
    contours = property(_get_contours, doc="allow for iteration through glyph.contours")
    
    # -----------------------------------------------------------------
    #
    #   transformations
    
    def move(self, (x, y)):
        matrix = psMat.translate((x,y))
        self._object.transform(matrix)
        
    def scale(self, (x, y), center=(0,0)):
        matrix = psMat.scale(x,y)
        self._object.transform(matrix)
        
    def transform(self, matrix):
        self._object.transform(matrix)
        
    def rotate(self, angle, offset=None):
        matrix = psMat.rotate(angle)
        self._object.transform(matrix)
        
    def skew(self, angle, offset=None):
        matrix = psMat.skew(angle)
        self._object.transform(matrix)

    # -----------------------------------------------------------------
    #
    #   components stuff

    def decompose(self):
        self._object.unlinkRef()

    # -----------------------------------------------------------------
    #
    #   unicode stuff

    def autoUnicodes(self):
        if __DEBUG__:
            print "objectsFF.RGlyph.autoUnicodes() not implemented yet."
        
    # -----------------------------------------------------------------
    #
    #   contour stuff
    
    def removeOverlap(self):
        self._object.removeOverlap()
    
    def correctDirection(self, trueType=False):
        # no option for trueType, really.
        self._object.correctDirection()
    
    def clear(self):
        self._object.clear()

    def __getitem__(self, index):
        return self.contours[index]
    

class RContour(BaseContour):
    def __init__(self, contour, index=None):
        self._object = contour
        self.index = index
        
    def _get_points(self):
        pts = []
        for pt in self._object:
            wpt = RPoint(pt)
            wpt.setParent(self)
            pts.append(wpt)
        return pts
    
    points = property(_get_points, doc="get contour points")
    
    def _get_box(self):
        return self._object.boundingBox()
    
    box = property(_get_box, doc="get contour bounding box")
    
    def __len__(self):
        return len(self._object)

    def __getitem__(self, index):
        return self.points[index]



class RPoint(BasePoint):

    def __init__(self, pointObject):
        self._object = pointObject
        
    def _get_x(self):
        return self._object.x

    def _set_x(self, value):
        self._object.x = value

    x = property(_get_x, _set_x, doc="")

    def _get_y(self):
        return self._object.y

    def _set_y(self, value):
        self._object.y = value

    y = property(_get_y, _set_y, doc="")
    
    def _get_type(self):
        if self._object.on_curve == 0:
            return OFFCURVE
            
        # XXX not always curve
        return CURVE
    
    def _set_type(self, value):
        self._type = value
        self._hasChanged()

    type = property(_get_type, _set_type, doc="")

    def __repr__(self):
        font = "unnamed_font"
        glyph = "unnamed_glyph"
        contourIndex = "unknown_contour"
        contourParent = self.getParent()
        if contourParent is not None:
            try:
                contourIndex = `contourParent.index`
            except AttributeError: pass
            glyphParent = contourParent.getParent()
            if glyphParent is not None:
                try:
                    glyph = glyphParent.name
                except AttributeError: pass
                fontParent = glyphParent.getParent()
                if fontParent is not None:
                    try:
                        font = fontParent.info.fullName
                    except AttributeError: pass
        return "<RPoint for %s.%s[%s]>"%(font, glyph, contourIndex)
        
 
class RInfo(BaseInfo):
    def __init__(self, font):
        BaseInfo.__init__(self)
        self._object = font
        
    def _get_familyName(self):
        return self._object.familyname
    def _set_familyName(self, value):
        self._object.familyname = value
    familyName = property(_get_familyName, _set_familyName, doc="familyname")
    
    def _get_fondName(self):
        return self._object.fondname
    def _set_fondName(self, value):
        self._object.fondname = value
    fondName = property(_get_fondName, _set_fondName, doc="fondname")
    
    def _get_fontName(self):
        return self._object.fontname
    def _set_fontName(self, value):
        self._object.fontname = value
    fontName = property(_get_fontName, _set_fontName, doc="fontname")
    
    # styleName doesn't have a specific field, FF has a whole sfnt dict.
    # implement fullName because a repr depends on it
    def _get_fullName(self):
        return self._object.fullname
    def _set_fullName(self, value):
        self._object.fullname = value
    fullName = property(_get_fullName, _set_fullName, doc="fullname")
    
    def _get_unitsPerEm(self):
        return self._object.em
    def _set_unitsPerEm(self, value):
        self._object.em = value
    unitsPerEm = property(_get_unitsPerEm, _set_unitsPerEm, doc="unitsPerEm value")
    
    def _get_ascender(self):
        return self._object.ascent
    def _set_ascender(self, value):
        self._object.ascent = value
    ascender = property(_get_ascender, _set_ascender, doc="ascender value")
    
    def _get_descender(self):
        return -self._object.descent
    def _set_descender(self, value):
        self._object.descent = -value
    descender = property(_get_descender, _set_descender, doc="descender value")

    def _get_copyright(self):
        return self._object.copyright
    def _set_copyright(self, value):
        self._object.copyright = value
    copyright = property(_get_copyright, _set_copyright, doc="copyright")



class RKerning(BaseKerning):
    
	""" Object representing the kerning.
		This is going to need some thinking about.
	"""
    

__all__ = [ 'RFont', 'RGlyph', 'RContour', 'RPoint', 'RInfo', 
            'OpenFont', 'CurrentFont', 'NewFont', 'CurrentFont'
            ]



if __name__ == "__main__":
    import os
    from robofab.objects.objectsRF import RFont as _RFont
    from sets import Set
    
    def dumpFontForgeAPI(testFontPath, printModule=False,
            printFont=False, printGlyph=False,
            printLayer=False, printContour=False, printPoint=False):
        def printAPI(item, name):
            print 
            print "-"*80
            print "API of", item
            names = dir(item)
            names.sort()
            print

            if printAPI:
                for n in names:
                    print
                    print "%s.%s"%(name, n)
                    try:
                        print getattr(item, n).__doc__
                    except:
                        print "# error showing", n
        # module
        if printModule:
            print "module file:", fontforge.__file__
            print "version:", fontforge.version()
            print "module doc:", fontforge.__doc__
            print "has User Interface:", fontforge.hasUserInterface()
            print "has Spiro:", fontforge.hasSpiro()
            printAPI(fontforge, "fontforge")
        
        # font
        fontObj = fontforge.open(testFontPath)
        if printFont:
            printAPI(fontObj, "font")
    
        # glyph
        glyphObj = fontObj["A"]
        if printGlyph:
                printAPI(glyphObj, "glyph")
        
        # layer
        layerObj = glyphObj.foreground
        if printLayer:
            printAPI(layerObj, "layer")

        # contour
        contourObj = layerObj[0]
        if printContour:
            printAPI(contourObj, "contour")
        
        # point
        if printPoint:
            pointObj = contourObj[0]
            printAPI(pointObj, "point")
        
        
        # other objects
        penObj = glyphObj.glyphPen()
        printAPI(penObj, "glyphPen")
        
    # use your own paths here.
    demoRoot = "/Users/erik/Develop/Mess/FontForge/objectsFF_work/"
    UFOPath = os.path.join(demoRoot, "Test.ufo")
    SFDPath = os.path.join(demoRoot, "Test_realSFD2.sfd")
    
    #dumpFontForgeAPI(UFOPath, printPoint=True)
    
    # should return None
    CurrentFont()
    
    def compareAttr(obj1, obj2, attrName, isMethod=False):
        if isMethod:
            a = getattr(obj1, attrName)()
            b = getattr(obj2, attrName)()
        else:
            a = getattr(obj1, attrName)
            b = getattr(obj2, attrName)
        if a == b and a is not None and b is not None:
            print "\tattr %s ok"%attrName, a
            return True
        else:
            print "\t?\t%s error:"%attrName, "%s:"%obj1.__class__, a, "%s:"%obj2.__class__, b
            return False

    f = OpenFont(UFOPath)
    #f = OpenFont(SFDPath)
    ref = _RFont(UFOPath)
    
    if False:
        print
        print "test font attributes"
        compareAttr(f, ref, "path")
    
        a = Set(f.keys())
        b = Set(ref.keys())
        print "glyphs in ref, not in f", b.difference(a)
        print "glyphs in f, not in ref", a.difference(b)
    
        print "A" in f, "A" in ref
        print f.has_key("A"),  ref.has_key("A")
    
        print
        print "test font info attributes"
        compareAttr(f.info, ref.info, "ascender")
        compareAttr(f.info, ref.info, "descender")
        compareAttr(f.info, ref.info, "unitsPerEm")
        compareAttr(f.info, ref.info, "copyright")
        compareAttr(f.info, ref.info, "fullName")
        compareAttr(f.info, ref.info, "familyName")
        compareAttr(f.info, ref.info, "fondName")
        compareAttr(f.info, ref.info, "fontName")

        # crash
        f.save()
    
        otfOutputPath = os.path.join(demoRoot, "test_ouput.otf")
        ufoOutputPath = os.path.join(demoRoot, "test_ouput.ufo")
        # generate without path, should end  up in the source folder
    
        f['A'].removeOverlap()
        f.generate('otfcff')    #, otfPath)
        f.generate('pctype1')   #, otfPath)
    
        # generate with path. Type is taken from the extension.
        f.generate('otfcff', otfOutputPath) #, otfPath)
        f.generate(None, ufoOutputPath) #, otfPath)
    
        featurePath = os.path.join(demoRoot, "testFeatureOutput.fea")
        f.naked().generateFeatureFile(featurePath)

    if False:
        # new glyphs
        # unencoded
        print "new glyph: unencoded", f.newGlyph("test_unencoded_glyph")
        # encoded
        print "new glyph: encoded", f.newGlyph("Adieresis")
        # existing
        print "new glyph: existing", f.newGlyph("K")

        print
        print "test glyph attributes"
        compareAttr(f['A'], ref['A'], "width")
        compareAttr(f['A'], ref['A'], "unicode")
        compareAttr(f['A'], ref['A'], "name")
        compareAttr(f['A'], ref['A'], "box")
        compareAttr(f['A'], ref['A'], "leftMargin")
        compareAttr(f['A'], ref['A'], "rightMargin")
    
    if False:
        print
        print "comparing glyph digests"
        failed = []
        for n in f.keys():
            g1 = f[n]
            #g1.round()
            g2 = ref[n]
            #g2.round()
            d1 = g1._getDigest()
            d2 = g2._getDigest()
            if d1 != d2:
                failed.append(n)
                #print "f: ", d1
                #print "ref: ", d2
        print "digest failed for %s"%". ".join(failed)
            
        g3 = f['A'] *.333
        print g3
        print g3._getDigest()
        f.save()

    if False:
        print
        print "test contour attributes"
        compareAttr(f['A'].contours[0], ref['A'].contours[0], "index")
    
        #for c in f['A'].contours:
        #   for p in c.points:
        #       print p, p.type
    
        # test with a glyph with just 1 contour so we can be sure we're comparing the same thing
        compareAttr(f['C'].contours[0], ref['C'].contours[0], "box")
        compareAttr(f['C'].contours[0], ref['C'].contours[0], "__len__", isMethod=True)
    
        ptf = f['C'].contours[0].points[0]
        ptref = ref['C'].contours[0].points[0]
        print "x, y", (ptf.x, ptf.y) == (ptref.x, ptref.y), (ptref.x, ptref.y)
        print 'type', ptf.type, ptref.type
    
        print "point inside", f['A'].pointInside((50,10)),  ref['A'].pointInside((50,10))
    
    
    print ref.kerning.keys()
    
    class GlyphLookupWrapper(dict):
        """A wrapper for the lookups / subtable data in a FF glyph.
        A lot of data is stored there, so it helps to have something to sort things out.
        """
        def __init__(self, ffGlyph):
            self._object = ffGlyph
            self.refresh()
            
        def __repr__(self):
            return "<GlyphLookupWrapper for %s, %d keys>"%(self._object.glyphname, len(self))
            
        def refresh(self):
            """Pick some of the values apart."""
            lookups = self._object.getPosSub('*')
            for t in lookups:
                print 'lookup', t
                lookupName = t[0]
                lookupType = t[1]
                if not lookupName in self:
                    self[lookupName] = []
                self[lookupName].append(t[1:])
        
        def getKerning(self):
            """Get a regular kerning dict for this glyph"""
            d = {}
            left = self._object.glyphname
            for name in self.keys():
                for item in self[name]:
                    print 'item', item
                    if item[0]!="Pair":
                        continue
                    #print 'next glyph:', item[1]
                    #print 'first glyph x Pos:', item[2]
                    #print 'first glyph y Pos:', item[3]
                    #print 'first glyph h Adv:', item[4]
                    #print 'first glyph v Adv:', item[5]

                    #print 'second glyph x Pos:', item[6]
                    #print 'second glyph y Pos:', item[7]
                    #print 'second glyph h Adv:', item[8]
                    #print 'second glyph v Adv:', item[9]
                    right = item[1]
                    d[(left, right)] = item[4]
            return d
        
        def setKerning(self, kernDict):
            """Set the values of a regular kerning dict to the lookups in a FF glyph."""
            for left, right in kernDict.keys():
                if left != self._object.glyphname:
                    # should we filter the dict before it gets here?
                    # easier just to filter it here.
                    continue
            
            
            
    # lets try to find the kerning
    A = f['A'].naked()
    positionTypes = [ "Position", "Pair", "Substitution", "AltSubs", "MultSubs","Ligature"]
    print A.getPosSub('*')
    #for t in A.getPosSub('*'):
    #    print 'lookup subtable name:', t[0]
    #    print 'positioning type:', t[1]
    #    if t[1]in positionTypes:
    #        print 'next glyph:', t[2]
    #        print 'first glyph x Pos:', t[3]
    #        print 'first glyph y Pos:', t[4]
    #        print 'first glyph h Adv:', t[5]
    #        print 'first glyph v Adv:', t[6]

    #        print 'second glyph x Pos:', t[7]
    #        print 'second glyph y Pos:', t[8]
    #        print 'second glyph h Adv:', t[9]
    #        print 'second glyph v Adv:', t[10]
    
    gw = GlyphLookupWrapper(A)
    print gw
    print gw.keys()
    print gw.getKerning()
    
    name = "'kern' Horizontal Kerning in Latin lookup 0 subtable"
    item = (name, 'quoteright', 0, 0, -200, 0, 0, 0, 0, 0)
    
    A.removePosSub(name)
    apply(A.addPosSub, item)
    
    
    print "after", A.getPosSub('*')
    
    fn = f.naked()

    name = "'kern' Horizontal Kerning in Latin lookup 0"


    print "before removing stuff", fn.gpos_lookups
    print "removing stuff", fn.removeLookup(name)
    print "after removing stuff", fn.gpos_lookups

    flags = ()
    feature_script_lang = (("kern",(("latn",("dflt")),)),)
    print fn.addLookup('kern', 'gpos_pair', flags, feature_script_lang)
    print fn.addLookupSubtable('kern', 'myKerning')
    
    
    print fn.gpos_lookups
    A.addPosSub('myKerning', 'A', 0, 0, -400, 0, 0, 0, 0, 0)
    A.addPosSub('myKerning', 'B', 0, 0, 200, 0, 0, 0, 0, 0)
    A.addPosSub('myKerning', 'C', 0, 0, 10, 0, 0, 0, 0, 0)
    A.addPosSub('myKerning', 'A', 0, 0, 77, 0, 0, 0, 0, 0)
    
    
    gw = GlyphLookupWrapper(A)
    print gw
    print gw.keys()
    print gw.getKerning()
    
