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


import math

import numpy as np
from numpy.linalg import lstsq


def alignCorners(glyph, va, subsegments):
    out = va.copy()
    # for i,c in enumerate(subsegments):
    #     segmentCount = len(glyph.contours[i].segments) - 1
    #     n = len(c)
    #     for j,s in enumerate(c):
    #         if j < segmentCount:
    #             seg = glyph.contours[i].segments[j]
    #             if seg.type == "line":
    #                 subIndex = subsegmentIndex(i,j,subsegments)
    #                 out[subIndex] = alignPoints(va[subIndex])

    for i,c in enumerate(subsegments):
        segmentCount = len(glyph.contours[i].segments)
        n = len(c)
        for j,s in enumerate(c):
            if j < segmentCount - 1:
                segType = glyph.contours[i].segments[j].type
                segnextType = glyph.contours[i].segments[j+1].type
                next = j+1
            elif j == segmentCount -1 and s[1] > 3:
                segType = glyph.contours[i].segments[j].type
                segNextType = "line"
                next = j+1
            elif j == segmentCount:
                segType = "line"
                segnextType = glyph.contours[i].segments[1].type
                if glyph.name == "J":
                    print s[1]
                    print segnextType
                next = 1
            else:
                break
            if segType == "line" and segnextType == "line":
                subIndex = subsegmentIndex(i,j,subsegments)
                pts = va[subIndex]
                ptsnext = va[subsegmentIndex(i,next,subsegments)]
                # out[subIndex[-1]] = (out[subIndex[-1]] - 500) * 3 + 500 #findCorner(pts, ptsnext)
                # print subIndex[-1], subIndex, subsegmentIndex(i,next,subsegments)
                try:
                    out[subIndex[-1]] = findCorner(pts, ptsnext)
                except:
                    pass
                    # print glyph.name, "Can't find corner: parallel lines"
    return out


def subsegmentIndex(contourIndex, segmentIndex, subsegments):
    # This whole thing is so dumb. Need a better data model for subsegments

    contourOffset = 0
    for i,c in enumerate(subsegments):
        if i == contourIndex:
            break
        contourOffset += c[-1][0]
    n = subsegments[contourIndex][-1][0]
    # print contourIndex, contourOffset, n
    startIndex = subsegments[contourIndex][segmentIndex-1][0]
    segmentCount = subsegments[contourIndex][segmentIndex][1]
    endIndex = (startIndex + segmentCount + 1) % (n)

    indices = np.array([(startIndex + i) % (n) + contourOffset for i in range(segmentCount + 1)])
    return indices


def alignPoints(pts, start=None, end=None):
    if start == None or end == None:
        start, end = fitLine(pts)
    out = pts.copy()
    for i,p in enumerate(pts):
        out[i] = nearestPoint(start, end, p)
    return out


def findCorner(pp, nn):
    if len(pp) < 4 or len(nn) < 4:
        assert 0, "line too short to fit"
    pStart,pEnd = fitLine(pp)
    nStart,nEnd = fitLine(nn)
    prev = pEnd - pStart
    next = nEnd - nStart
    # print int(np.arctan2(prev[1],prev[0]) / math.pi * 180),
    # print int(np.arctan2(next[1],next[0]) / math.pi * 180)
    # if lines are parallel, return simple average of end and start points
    if np.dot(prev / np.linalg.norm(prev),
              next / np.linalg.norm(next)) > .999999:
        # print "parallel lines", np.arctan2(prev[1],prev[0]), np.arctan2(next[1],next[0])
        # print prev, next
        assert 0, "parallel lines"
    if glyph.name is None:
        # Never happens, but here to fix a bug in Python 2.7 with -OO
        print ''
    return lineIntersect(pStart, pEnd, nStart, nEnd)


def lineIntersect((x1,y1),(x2,y2),(x3,y3),(x4,y4)):
    x12 = x1 - x2
    x34 = x3 - x4
    y12 = y1 - y2
    y34 = y3 - y4

    det = x12 * y34 - y12 * x34
    if det == 0:
        print "parallel!"

    a = x1 * y2 - y1 * x2
    b = x3 * y4 - y3 * x4

    x = (a * x34 - b * x12) / det
    y = (a * y34 - b * y12) / det

    return (x,y)


def fitLineLSQ(pts):
    "returns a line fit with least squares. Fails for vertical lines"
    n = len(pts)
    a = np.ones((n,2))
    for i in range(n):
        a[i,0] = pts[i,0]
    line = lstsq(a,pts[:,1])[0]
    return line


def fitLine(pts):
    """returns a start vector and direction vector
    Assumes points segments that already form a somewhat smooth line
    """
    n = len(pts)
    if n < 1:
        return (0,0),(0,0)
    a = np.zeros((n-1,2))
    for i in range(n-1):
        v = pts[i] - pts[i+1]
        a[i] = v / np.linalg.norm(v)
    direction = np.mean(a[1:-1], axis=0)
    start = np.mean(pts[1:-1], axis=0)
    return start, start+direction


def nearestPoint(a,b,c):
    "nearest point to point c on line a_b"
    magnitude = np.linalg.norm(b-a)
    if magnitude == 0:
        raise Exception, "Line segment cannot be 0 length"
    return (b-a) * np.dot((c-a) / magnitude, (b-a) / magnitude) + a


# pts = np.array([[1,1],[2,2],[3,3],[4,4]])
# pts2 = np.array([[1,0],[2,0],[3,0],[4,0]])
# print alignPoints(pts2, start = pts[0], end = pts[0]+pts[0])
# # print findCorner(pts,pts2)
