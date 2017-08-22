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


"""Mitre Glyph: 

mitreSize : Length of the segment created by the mitre. The default is 4.
maxAngle :  Maximum angle in radians at which segments will be mitred. The default is .9 (about 50 degrees).
            Works for both inside and outside angles

"""

import math
from robofab.objects.objectsRF import RPoint, RSegment
from fontbuild.convertCurves import replaceSegments

def getTangents(contours):
    tmap = []
    for c in contours:
        clen = len(c)
        for i in range(clen):
            s = c[i]
            p = s.points[-1]
            ns = c[(i + 1) % clen]
            ps = c[(clen + i - 1) % clen]
            np = ns.points[1] if ns.type == 'curve' else ns.points[-1]
            pp = s.points[2] if s.type == 'curve' else ps.points[-1]
            tmap.append((pp - p, np - p))
    return tmap    

def normalizeVector(p):
    m = getMagnitude(p);
    if m != 0:
        return p*(1/m)
    else:
        return RPoint(0,0)

def getMagnitude(p):
    return math.sqrt(p.x*p.x + p.y*p.y)
    
def getDistance(v1,v2):
    return getMagnitude(RPoint(v1.x - v2.x, v1.y - v2.y))

def getAngle(v1,v2):
    angle = math.atan2(v1.y,v1.x) - math.atan2(v2.y,v2.x)
    return (angle + (2*math.pi)) % (2*math.pi)
    
def angleDiff(a,b):
    return math.pi - abs((abs(a - b) % (math.pi*2)) - math.pi)

def getAngle2(v1,v2):
    return abs(angleDiff(math.atan2(v1.y, v1.x), math.atan2(v2.y, v2.x)))

def getMitreOffset(n,v1,v2,mitreSize=4,maxAngle=.9):
    
    # dont mitre if segment is too short
    if abs(getMagnitude(v1)) < mitreSize * 2 or abs(getMagnitude(v2)) < mitreSize * 2:
        return
    angle = getAngle2(v2,v1)
    v1 = normalizeVector(v1)
    v2 = normalizeVector(v2)
    if v1.x == v2.x and v1.y == v2.y:
        return
    
    
    # only mitre corners sharper than maxAngle
    if angle > maxAngle:
        return
    
    radius = mitreSize / abs(getDistance(v1,v2))
    offset1 = RPoint(round(v1.x * radius), round(v1.y * radius))
    offset2 = RPoint(round(v2.x * radius), round(v2.y * radius))
    return offset1, offset2

def mitreGlyph(g,mitreSize,maxAngle):
    if g == None:
        return
    
    tangents = getTangents(g.contours)
    sid = -1
    for c in g.contours:
        segments = []
        needsMitring = False
        for s in c:
            sid += 1
            v1, v2 = tangents[sid]
            off = getMitreOffset(s,v1,v2,mitreSize,maxAngle)
            s1 = s.copy()
            if off != None:
                offset1, offset2 = off
                p2 = s.points[-1] + offset2
                s2 = RSegment('line', [(p2.x, p2.y)])
                s1.points[0] += offset1
                segments.append(s1)
                segments.append(s2)
                needsMitring = True
            else:
                segments.append(s1)
        if needsMitring:
            replaceSegments(c, segments)
