# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from numpy import array, append
import copy
import json
from robofab.objects.objectsRF import RPoint, RGlyph
from robofab.world import OpenFont
from decomposeGlyph import decomposeGlyph


class FFont:
    "Font wrapper for floating point operations"
    
    def __init__(self,f=None):
        self.glyphs = {}
        self.hstems = []
        self.vstems = []
        self.kerning = {}
        if isinstance(f,FFont):
            #self.glyphs = [g.copy() for g in f.glyphs]
            for key,g in f.glyphs.iteritems():
                self.glyphs[key] = g.copy()
            self.hstems = list(f.hstems)
            self.vstems = list(f.vstems)
            self.kerning = dict(f.kerning)
        elif f != None:
            self.copyFromFont(f)

    def copyFromFont(self, f):
        for g in f:
            self.glyphs[g.name] = FGlyph(g)
        self.hstems = [s for s in f.info.postscriptStemSnapH]
        self.vstems = [s for s in f.info.postscriptStemSnapV]
        self.kerning = f.kerning.asDict()


    def copyToFont(self, f):
        for g in f:
            try:
                gF = self.glyphs[g.name]
                gF.copyToGlyph(g)
            except:
                print "Copy to glyph failed for" + g.name
        f.info.postscriptStemSnapH = self.hstems
        f.info.postscriptStemSnapV = self.vstems
        for pair in self.kerning:
            f.kerning[pair] = self.kerning[pair]

    def getGlyph(self, gname):
        try:
            return self.glyphs[gname]
        except:
            return None
        
    def setGlyph(self, gname, glyph):
        self.glyphs[gname] = glyph
    
    def addDiff(self,b,c):
        newFont = FFont(self)
        for key,g in newFont.glyphs.iteritems():
            gB = b.getGlyph(key)
            gC = c.getGlyph(key)
            try:
                newFont.glyphs[key] = g.addDiff(gB,gC)
            except:
                print "Add diff failed for '%s'" %key
        return newFont

class FGlyph:
    "provides a temporary floating point compatible glyph data structure"
    
    def __init__(self, g=None):
        self.contours = []
        self.width = 0.
        self.components = []
        self.anchors = []
        if g != None:
            self.copyFromGlyph(g)
        
    def copyFromGlyph(self,g):
        self.name = g.name
        valuesX = []
        valuesY = []
        self.width = len(valuesX)
        valuesX.append(g.width)
        for c in g.components:
            self.components.append((len(valuesX), len(valuesY)))
            valuesX.append(c.scale[0])
            valuesY.append(c.scale[1])
            valuesX.append(c.offset[0])
            valuesY.append(c.offset[1])

        for a in g.anchors:
            self.anchors.append((len(valuesX), len(valuesY)))
            valuesX.append(a.x)
            valuesY.append(a.y)

        for i in range(len(g)):
            self.contours.append([])
            for j in range (len(g[i].points)):
                self.contours[i].append((len(valuesX), len(valuesY)))
                valuesX.append(g[i].points[j].x)
                valuesY.append(g[i].points[j].y)

        self.dataX = array(valuesX, dtype=float)
        self.dataY = array(valuesY, dtype=float)
        
    def copyToGlyph(self,g):
        g.width = self._derefX(self.width)
        if len(g.components) == len(self.components):
            for i in range(len(self.components)):
                g.components[i].scale = (self._derefX(self.components[i][0] + 0, asInt=False),
                                         self._derefY(self.components[i][1] + 0, asInt=False))
                g.components[i].offset = (self._derefX(self.components[i][0] + 1),
                                          self._derefY(self.components[i][1] + 1))
        if len(g.anchors) == len(self.anchors):
            for i in range(len(self.anchors)):
                g.anchors[i].x = self._derefX( self.anchors[i][0])
                g.anchors[i].y = self._derefY( self.anchors[i][1])
        for i in range(len(g)) :
            for j in range (len(g[i].points)):
                g[i].points[j].x = self._derefX(self.contours[i][j][0])
                g[i].points[j].y = self._derefY(self.contours[i][j][1])

    def isCompatible(self, g):
        return (len(self.dataX) == len(g.dataX) and
                len(self.dataY) == len(g.dataY) and
                len(g.contours) == len(self.contours))
    
    def __add__(self,g):
        if self.isCompatible(g):
            newGlyph = self.copy()
            newGlyph.dataX = self.dataX + g.dataX
            newGlyph.dataY = self.dataY + g.dataY
            return newGlyph
        else:
            print "Add failed for '%s'" %(self.name)
            raise Exception
    
    def __sub__(self,g):
        if self.isCompatible(g):
            newGlyph = self.copy()
            newGlyph.dataX = self.dataX - g.dataX
            newGlyph.dataY = self.dataY - g.dataY
            return newGlyph
        else:
            print "Subtract failed for '%s'" %(self.name)
            raise Exception
    
    def __mul__(self,scalar):
        newGlyph = self.copy()
        newGlyph.dataX = self.dataX * scalar
        newGlyph.dataY = self.dataY * scalar
        return newGlyph
    
    def scaleX(self,scalar):
        newGlyph = self.copy()
        if len(self.dataX) > 0:
            newGlyph.dataX = self.dataX * scalar
            for i in range(len(newGlyph.components)):
                newGlyph.dataX[newGlyph.components[i][0]] = self.dataX[newGlyph.components[i][0]]
        return newGlyph
        
    def shift(self,ammount):
        newGlyph = self.copy()
        newGlyph.dataX = self.dataX + ammount
        for i in range(len(newGlyph.components)):
            newGlyph.dataX[newGlyph.components[i][0]] = self.dataX[newGlyph.components[i][0]]
        return newGlyph
    
    def interp(self, g, v):
        gF = self.copy()
        if not self.isCompatible(g):
            print "Interpolate failed for '%s'; outlines incompatible" %(self.name)
            raise Exception
        
        gF.dataX += (g.dataX - gF.dataX) * v.x
        gF.dataY += (g.dataY - gF.dataY) * v.y
        return gF
    
    def copy(self):
        ng = FGlyph()
        ng.contours = list(self.contours)
        ng.width = self.width
        ng.components = list(self.components)
        ng.anchors = list(self.anchors)
        ng.dataX = self.dataX.copy()
        ng.dataY = self.dataY.copy()
        ng.name = self.name
        return ng
    
    def _derefX(self,id, asInt=True):
        val = self.dataX[id]
        return int(round(val)) if asInt else val
    
    def _derefY(self,id, asInt=True):
        val = self.dataY[id]
        return int(round(val)) if asInt else val
    
    def addDiff(self,gB,gC):
        newGlyph = self + (gB - gC)
        return newGlyph
        
    

class Master:

    def __init__(self, font=None, v=0, kernlist=None, overlay=None):
        if isinstance(font, FFont):
            self.font = None
            self.ffont = font
        elif isinstance(font,str):
            self.openFont(font,overlay)
        elif isinstance(font,Mix):
            self.font = font
        else:
            self.font = font
            self.ffont = FFont(font)
        if isinstance(v,float) or isinstance(v,int):
            self.v = RPoint(v, v)
        else:
            self.v = v
        if kernlist != None:
            kerns = [i.strip().split() for i in open(kernlist).readlines()]
            
            self.kernlist = [{'left':k[0], 'right':k[1], 'value': k[2]} 
                            for k in kerns 
                            if not k[0].startswith("#")
                            and not k[0] == ""]
            #TODO implement class based kerning / external kerning file
    
    def openFont(self, path, overlayPath=None):
        self.font = OpenFont(path)
        for g in self.font:
          size = len(g)
          csize = len(g.components)
          if (size > 0 and csize > 0):
            decomposeGlyph(self.font, self.font[g.name])

        if overlayPath != None:
            overlayFont = OpenFont(overlayPath)
            font = self.font
            for overlayGlyph in overlayFont:
                font.insertGlyph(overlayGlyph)

        self.ffont = FFont(self.font)


class Mix:
    def __init__(self,masters,v):
        self.masters = masters
        if isinstance(v,float) or isinstance(v,int):
            self.v = RPoint(v,v)
        else:
            self.v = v
    
    def getFGlyph(self, master, gname):
        if isinstance(master.font, Mix):
            return font.mixGlyphs(gname)
        return master.ffont.getGlyph(gname)
    
    def getGlyphMasters(self,gname):
        masters = self.masters
        if len(masters) <= 2:
            return self.getFGlyph(masters[0], gname), self.getFGlyph(masters[-1], gname)
    
    def generateFFont(self):
        ffont = FFont(self.masters[0].ffont)
        for key,g in ffont.glyphs.iteritems():
            ffont.glyphs[key] = self.mixGlyphs(key)
        ffont.kerning = self.mixKerns()
        return ffont
    
    def generateFont(self, baseFont):
        newFont = baseFont.copy()
        #self.mixStems(newFont)  todo _ fix stems code
        for g in newFont:
            gF = self.mixGlyphs(g.name)
            if gF == None:
                g.mark = True
            elif isinstance(gF, RGlyph):
                newFont[g.name] = gF.copy()
            else:
                gF.copyToGlyph(g)

        newFont.kerning.clear()
        newFont.kerning.update(self.mixKerns() or {})
        return newFont
    
    def mixGlyphs(self,gname):
        gA,gB = self.getGlyphMasters(gname)        
        try:
            return gA.interp(gB,self.v)
        except:
            print "mixglyph failed for %s" %(gname)
            if gA != None:
                return gA.copy()

    def getKerning(self, master):
        if isinstance(master.font, Mix):
            return master.font.mixKerns()
        return master.ffont.kerning

    def mixKerns(self):
        masters = self.masters
        kA, kB = self.getKerning(masters[0]), self.getKerning(masters[-1])
        return interpolateKerns(kA, kB, self.v)


def narrowFLGlyph(g, gThin, factor=.75):
    gF = FGlyph(g)
    if not isinstance(gThin,FGlyph):
        gThin = FGlyph(gThin)
    gCondensed = gThin.scaleX(factor)
    try:
        gNarrow = gF + (gCondensed - gThin)
        gNarrow.copyToGlyph(g)
    except:
        print "No dice for: " + g.name
            
def interpolate(a,b,v,e=0):
    if e == 0:
        return a+(b-a)*v
    qe = (b-a)*v*v*v + a   #cubic easing
    le = a+(b-a)*v   # linear easing
    return le + (qe-le) * e

def interpolateKerns(kA, kB, v):
    # to yield correct kerning for Roboto output, we must emulate the behavior
    # of old versions of this code; namely, take the kerning values of the first
    # master instead of actually interpolating.
    # old code:
    # https://github.com/google/roboto/blob/7f083ac31241cc86d019ea6227fa508b9fcf39a6/scripts/lib/fontbuild/mix.py
    # bug:
    # https://github.com/google/roboto/issues/213
    # return dict(kA)

    kerns = {}
    for pair, val in kA.items():
       kerns[pair] = interpolate(val, kB.get(pair, 0), v.x)
    for pair, val in kB.items():
       lerped_val = interpolate(val, kA.get(pair, 0), 1 - v.x)
       if pair in kerns:
           assert abs(kerns[pair] - lerped_val) < 1e-6
       else:
           kerns[pair] = lerped_val
    return kerns
