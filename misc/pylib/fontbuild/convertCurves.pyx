#! /usr/bin/env python
#
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

"""
Converts a cubic bezier curve to a quadratic spline with 
exactly two off curve points.

"""

import numpy
from numpy import array,cross,dot
from fontTools.misc import bezierTools
from robofab.objects.objectsRF import RSegment

def replaceSegments(contour, segments):
    while len(contour):
        contour.removeSegment(0)
    for s in segments:
        contour.appendSegment(s.type, [(p.x, p.y) for p in s.points], s.smooth)
    
def calcIntersect(a,b,c,d):
    numpy.seterr(all='raise')
    e = b-a
    f = d-c
    p = array([-e[1], e[0]])
    try:
        h = dot((a-c),p) / dot(f,p)
    except:
        print a,b,c,d
        raise
    return c + dot(f,h)

def simpleConvertToQuadratic(p0,p1,p2,p3):
    p = [array(i.x,i.y) for i in [p0,p1,p2,p3]]
    off = calcIntersect(p[0],p[1],p[2],p[3])

# OFFCURVE_VECTOR_CORRECTION = -.015
OFFCURVE_VECTOR_CORRECTION = 0

def convertToQuadratic(p0,p1,p2,p3):
    # TODO: test for accuracy and subdivide further if needed
    p = [(i.x,i.y) for i in [p0,p1,p2,p3]]
    # if p[0][0] == p[1][0] and p[0][0] == p[2][0] and p[0][0] == p[2][0] and p[0][0] == p[3][0]:
    #     return (p[0],p[1],p[2],p[3]) 
    # if p[0][1] == p[1][1] and p[0][1] == p[2][1] and p[0][1] == p[2][1] and p[0][1] == p[3][1]:
    #     return (p[0],p[1],p[2],p[3])     
    seg1,seg2 = bezierTools.splitCubicAtT(p[0], p[1], p[2], p[3], .5)
    pts1 = [array([i[0], i[1]]) for i in seg1]
    pts2 = [array([i[0], i[1]]) for i in seg2]
    on1 = seg1[0]
    on2 = seg2[3]
    try:
        off1 = calcIntersect(pts1[0], pts1[1], pts1[2], pts1[3])
        off2 = calcIntersect(pts2[0], pts2[1], pts2[2], pts2[3])
    except:
        return (p[0],p[1],p[2],p[3])
    off1 = (on1 - off1) * OFFCURVE_VECTOR_CORRECTION + off1
    off2 = (on2 - off2) * OFFCURVE_VECTOR_CORRECTION + off2
    return (on1,off1,off2,on2)

def cubicSegmentToQuadratic(c,sid):
    
    segment = c[sid]
    if (segment.type != "curve"):
        print "Segment type not curve"
        return
    
    #pSegment,junk = getPrevAnchor(c,sid)
    pSegment = c[sid-1] #assumes that a curve type will always be proceeded by another point on the same contour
    points = convertToQuadratic(pSegment.points[-1],segment.points[0],
                                segment.points[1],segment.points[2])
    return RSegment(
        'qcurve', [[int(i) for i in p] for p in points[1:]], segment.smooth)

def glyphCurvesToQuadratic(g):

    for c in g:
        segments = []
        for i in range(len(c)):
            s = c[i]
            if s.type == "curve":
                try:
                    segments.append(cubicSegmentToQuadratic(c, i))
                except Exception:
                    print g.name, i
                    raise
            else:
                segments.append(s)
        replaceSegments(c, segments)
