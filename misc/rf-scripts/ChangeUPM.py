# Change upm
# Jens Kutilek 2013-01-02

from mojo.roboFont import version

def scalePoints(glyph, factor):
    if version == "1.4":
        # stupid workaround for bug in RoboFont 1.4
        for contour in glyph:
            for point in contour.points:
                point.x *= factor
                point.y *= factor
        glyph.width *= factor
    else:
        glyph *= factor

def scaleGlyph(glyph, factor, scaleWidth=True, roundCoordinates=True):
    if not(scaleWidth):
        oldWidth = glyph.width
    if len(glyph.components) == 0:
        scalePoints(glyph, factor)
        if roundCoordinates:
            glyph.round()
    else:
        # save components
        # this may be a tad too convoluted ...
        components = []
        for i in range(len(glyph.components)):
            components.append(glyph.components[i])
        for c in components:
            glyph.removeComponent(c)    
        scalePoints(glyph, factor)
        if roundCoordinates:
            glyph.round()
        # restore components
        for i in range(len(components)):
            newOffset = (int(round(components[i].offset[0] * factor)),
                         int(round(components[i].offset[1] * factor)))
            glyph.appendComponent(components[i].baseGlyph, newOffset, components[i].scale)
    if not(scaleWidth):
        # restore width
        glyph.width = oldWidth


def changeUPM(font, factor, roundCoordinates=True):
        
    # Glyphs
    for g in font:
        scaleGlyph(g, factor)
        for guide in g.guides:
            # another thing that doesn't work in RoboFont 1.4 - 1.5.1
            guide.x *= factor
            guide.y *= factor
    
    # Glyph layers
    mainLayer = "foreground"
    for layerName in font.layerOrder:
        if layerName != mainLayer:
            for g in font:
                g.flipLayers(mainLayer, layerName)
                scaleGlyph(g, factor, scaleWidth=False)
                g.flipLayers(layerName, mainLayer)
    
    # Kerning
    if font.kerning:
        font.kerning.scale(factor)
        if roundCoordinates:
            if not version in ["1.4", "1.5", "1.5.1"]:
                font.kerning.round(1)
            else:
                print "WARNING: kerning values cannot be rounded to integer in this RoboFont version"
    
    # TODO: Change positioning feature code?
    
    # Vertical dimensions
    font.info.descender = int(round(font.info.descender * factor))
    font.info.xHeight   = int(round(font.info.xHeight   * factor))
    font.info.capHeight = int(round(font.info.capHeight * factor))
    font.info.ascender  = int(round(font.info.ascender  * factor))

    # Finally set new UPM
    font.info.unitsPerEm = newUpm
    
    font.update()

if __name__ == "__main__":
    from robofab.interface.all.dialogs import AskString
    
    print "Change Units Per Em"

    if CurrentFont() is not None:
        oldUpm = CurrentFont().info.unitsPerEm
        newUpm = CurrentFont().info.unitsPerEm
        try:
            newUpm = int(AskString("New units per em size?", oldUpm))
        except:
            pass
        if newUpm == oldUpm:
            print "  Not changing upm size."
        else:
            factor = float(newUpm) / oldUpm        
            print "  Scaling all font measurements by", factor
            changeUPM(CurrentFont(), factor)
    else:
        print "  Open a font first to change upm, please."

    print "  Done."
