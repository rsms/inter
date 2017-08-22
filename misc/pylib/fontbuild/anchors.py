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


def getGlyph(gname, font):
    return font[gname] if font.has_key(gname) else None


def getComponentByName(f, g, componentName):
    for c in g.components:
        if c.baseGlyph == componentName:
            return c

def getAnchorByName(g,anchorName):
    for a in g.anchors:
        if a.name == anchorName:
            return a

def moveMarkAnchors(f, g, anchorName, accentName, dx, dy):
    if "top"==anchorName:
        anchors = f[accentName].anchors
        for anchor in anchors:
            if "mkmktop_acc" == anchor.name:
                for anc in g.anchors:
                    if anc.name == "top":
                        g.removeAnchor(anc)
                        break
                g.appendAnchor("top", (anchor.x + int(dx), anchor.y + int(dy)))
 
    elif anchorName in ["bottom", "bottomu"]:
        anchors = f[accentName].anchors
        for anchor in anchors:
            if "mkmkbottom_acc" == anchor.name:
                for anc in g.anchors:
                    if anc.name == "bottom":
                        g.removeAnchor(anc)
                        break
                x = anchor.x + int(dx)
                for anc in anchors:
                    if "top" == anc.name:
                        x = anc.x + int(dx)
                g.appendAnchor("bottom", (x, anchor.y + int(dy)))


def alignComponentToAnchor(f,glyphName,baseName,accentName,anchorName):
    g = getGlyph(glyphName,f)
    base = getGlyph(baseName,f)
    accent = getGlyph(accentName,f)
    if g == None or base == None or accent == None:
        return
    a1 = getAnchorByName(base,anchorName)
    a2 = getAnchorByName(accent,"_" + anchorName)
    if a1 == None or a2 == None:
        return
    offset = (a1.x - a2.x, a1.y - a2.y)
    c = getComponentByName(f, g, accentName)
    c.offset = offset
    moveMarkAnchors(f, g, anchorName, accentName, offset[0], offset[1])


def alignComponentsToAnchors(f,glyphName,baseName,accentNames):
    for a in accentNames:
        if len(a) == 1:
            continue
        alignComponentToAnchor(f,glyphName,baseName,a[0],a[1])

