#! /opt/local/bin/pythonw2.7
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


__all__ = ["SubsegmentPen","SubsegmentsToCurvesPen", "segmentGlyph", "fitGlyph"]


from fontTools.pens.basePen import BasePen
import numpy as np
from numpy import array as v
from numpy.linalg import norm
from robofab.pens.adapterPens import GuessSmoothPointPen
from robofab.pens.pointPen import BasePointToSegmentPen


class SubsegmentsToCurvesPointPen(BasePointToSegmentPen):
    def __init__(self, glyph, subsegmentGlyph, subsegments):
        BasePointToSegmentPen.__init__(self)
        self.glyph = glyph
        self.subPen = SubsegmentsToCurvesPen(None, glyph.getPen(), subsegmentGlyph, subsegments)

    def setMatchTangents(self, b):
        self.subPen.matchTangents = b

    def _flushContour(self, segments):
        #
        # adapted from robofab.pens.adapterPens.rfUFOPointPen
        #
        assert len(segments) >= 1
        # if we only have one point and it has a name, we must have an anchor
        first = segments[0]
        segmentType, points = first
        pt, smooth, name, kwargs = points[0]
        if len(segments) == 1 and name != None:
            self.glyph.appendAnchor(name, pt)
            return
        else:
            segmentType, points = segments[-1]
            movePt, smooth, name, kwargs = points[-1]
            if smooth:
                # last point is smooth, set pen to start smooth
                self.subPen.setLastSmooth(True)
            if segmentType == 'line':
                    del segments[-1]

        self.subPen.moveTo(movePt)

        # do the rest of the segments
        for segmentType, points in segments:
            isSmooth = True in [smooth for pt, smooth, name, kwargs in points]
            pp = [pt for pt, smooth, name, kwargs in points]
            if segmentType == "line":
                    assert len(pp) == 1
                    if isSmooth:
                        self.subPen.smoothLineTo(pp[0])
                    else:
                        self.subPen.lineTo(pp[0])
            elif segmentType == "curve":
                    assert len(pp) == 3
                    if isSmooth:
                        self.subPen.smoothCurveTo(*pp)
                    else:
                        self.subPen.curveTo(*pp)
            elif segmentType == "qcurve":
                    assert 0, "qcurve not supported"
            else:
                    assert 0, "illegal segmentType: %s" % segmentType
        self.subPen.closePath()

    def addComponent(self, glyphName, transform):
        self.subPen.addComponent(glyphName, transform)


class SubsegmentsToCurvesPen(BasePen):
    def __init__(self, glyphSet, otherPen, subsegmentGlyph, subsegments):
        BasePen.__init__(self, None)
        self.otherPen = otherPen
        self.ssglyph = subsegmentGlyph
        self.subsegments = subsegments
        self.contourIndex = -1
        self.segmentIndex = -1
        self.lastPoint = (0,0)
        self.lastSmooth = False
        self.nextSmooth = False

    def setLastSmooth(self, b):
        self.lastSmooth = b

    def _moveTo(self, (x, y)):
        self.contourIndex += 1
        self.segmentIndex = 0
        self.startPoint = (x,y)
        p = self.ssglyph.contours[self.contourIndex][0].points[0]
        self.otherPen.moveTo((p.x, p.y))
        self.lastPoint = (x,y)

    def _lineTo(self, (x, y)):
        self.segmentIndex += 1
        index = self.subsegments[self.contourIndex][self.segmentIndex][0]
        p = self.ssglyph.contours[self.contourIndex][index].points[0]
        self.otherPen.lineTo((p.x, p.y))
        self.lastPoint = (x,y)
        self.lastSmooth = False

    def smoothLineTo(self, (x, y)):
        self.lineTo((x,y))
        self.lastSmooth = True

    def smoothCurveTo(self, (x1, y1), (x2, y2), (x3, y3)):
        self.nextSmooth = True
        self.curveTo((x1, y1), (x2, y2), (x3, y3))
        self.nextSmooth = False
        self.lastSmooth = True

    def _curveToOne(self, (x1, y1), (x2, y2), (x3, y3)):
        self.segmentIndex += 1
        c = self.ssglyph.contours[self.contourIndex]
        n = len(c)
        startIndex = (self.subsegments[self.contourIndex][self.segmentIndex-1][0])
        segmentCount = (self.subsegments[self.contourIndex][self.segmentIndex][1])
        endIndex = (startIndex + segmentCount + 1) % (n)

        indices = [(startIndex + i) % (n) for i in range(segmentCount + 1)]
        points = np.array([(c[i].points[0].x, c[i].points[0].y) for i in indices])
        prevPoint = (c[(startIndex - 1)].points[0].x, c[(startIndex - 1)].points[0].y)
        nextPoint = (c[(endIndex) % n].points[0].x, c[(endIndex) % n].points[0].y)
        prevTangent = prevPoint - points[0]
        nextTangent = nextPoint - points[-1]

        tangent1 = points[1] - points[0]
        tangent3 = points[-2] - points[-1]
        prevTangent /= np.linalg.norm(prevTangent)
        nextTangent /= np.linalg.norm(nextTangent)
        tangent1 /= np.linalg.norm(tangent1)
        tangent3 /= np.linalg.norm(tangent3)

        tangent1, junk = self.smoothTangents(tangent1, prevTangent, self.lastSmooth)
        tangent3, junk = self.smoothTangents(tangent3, nextTangent, self.nextSmooth)
        if self.matchTangents == True:
            cp = fitBezier(points, tangent1, tangent3)
            cp[1] = norm(cp[1] - cp[0]) * tangent1 / norm(tangent1) + cp[0]
            cp[2] = norm(cp[2] - cp[3]) * tangent3 / norm(tangent3) + cp[3]
        else:
            cp = fitBezier(points)
        # if self.ssglyph.name == 'r':
        #     print "-----------"
        #     print self.lastSmooth, self.nextSmooth
        #     print "%i %i : %i %i \n %i %i : %i %i \n %i %i : %i %i"%(x1,y1, cp[1,0], cp[1,1], x2,y2, cp[2,0], cp[2,1], x3,y3, cp[3,0], cp[3,1])
        self.otherPen.curveTo((cp[1,0], cp[1,1]), (cp[2,0], cp[2,1]), (cp[3,0], cp[3,1]))
        self.lastPoint = (x3, y3)
        self.lastSmooth = False

    def smoothTangents(self,t1,t2,forceSmooth = False):
        if forceSmooth or (abs(t1.dot(t2)) > .95 and norm(t1-t2) > 1):
            # print t1,t2,
            t1 = (t1 - t2) / 2
            t2 = -t1
            # print t1,t2
        return t1 / norm(t1), t2 / norm(t2)

    def _closePath(self):
        self.otherPen.closePath()

    def _endPath(self):
        self.otherPen.endPath()

    def addComponent(self, glyphName, transformation):
        self.otherPen.addComponent(glyphName, transformation)


class SubsegmentPointPen(BasePointToSegmentPen):
    def __init__(self, glyph, resolution):
        BasePointToSegmentPen.__init__(self)
        self.glyph = glyph
        self.resolution = resolution
        self.subPen = SubsegmentPen(None, glyph.getPen())

    def getSubsegments(self):
        return self.subPen.subsegments[:]

    def _flushContour(self, segments):
        #
        # adapted from robofab.pens.adapterPens.rfUFOPointPen
        #
        assert len(segments) >= 1
        # if we only have one point and it has a name, we must have an anchor
        first = segments[0]
        segmentType, points = first
        pt, smooth, name, kwargs = points[0]
        if len(segments) == 1 and name != None:
            self.glyph.appendAnchor(name, pt)
            return
        else:
            segmentType, points = segments[-1]
            movePt, smooth, name, kwargs = points[-1]
            if segmentType == 'line':
                    del segments[-1]

        self.subPen.moveTo(movePt)

        # do the rest of the segments
        for segmentType, points in segments:
            points = [pt for pt, smooth, name, kwargs in points]
            if segmentType == "line":
                    assert len(points) == 1
                    self.subPen.lineTo(points[0])
            elif segmentType == "curve":
                    assert len(points) == 3
                    self.subPen.curveTo(*points)
            elif segmentType == "qcurve":
                    assert 0, "qcurve not supported"
            else:
                    assert 0, "illegal segmentType: %s" % segmentType
        self.subPen.closePath()

    def addComponent(self, glyphName, transform):
        self.subPen.addComponent(glyphName, transform)


class SubsegmentPen(BasePen):

    def __init__(self, glyphSet, otherPen, resolution=25):
        BasePen.__init__(self,glyphSet)
        self.resolution = resolution
        self.otherPen = otherPen
        self.subsegments = []
        self.startContour = (0,0)
        self.contourIndex = -1

    def _moveTo(self, (x, y)):
        self.contourIndex += 1
        self.segmentIndex = 0
        self.subsegments.append([])
        self.subsegmentCount = 0
        self.subsegments[self.contourIndex].append([self.subsegmentCount, 0])
        self.startContour = (x,y)
        self.lastPoint = (x,y)
        self.otherPen.moveTo((x,y))

    def _lineTo(self, (x, y)):
        count = self.stepsForSegment((x,y),self.lastPoint)
        if count < 1:
            count = 1
        self.subsegmentCount += count
        self.subsegments[self.contourIndex].append([self.subsegmentCount, count])
        for i in range(1,count+1):
            x1 = self.lastPoint[0] + (x - self.lastPoint[0]) * i/float(count)
            y1 = self.lastPoint[1] + (y - self.lastPoint[1]) * i/float(count)
            self.otherPen.lineTo((x1,y1))
        self.lastPoint = (x,y)

    def _curveToOne(self, (x1, y1), (x2, y2), (x3, y3)):
        count = self.stepsForSegment((x3,y3),self.lastPoint)
        if count < 2:
            count = 2
        self.subsegmentCount += count
        self.subsegments[self.contourIndex].append([self.subsegmentCount,count])
        x = self.renderCurve((self.lastPoint[0],x1,x2,x3),count)
        y = self.renderCurve((self.lastPoint[1],y1,y2,y3),count)
        assert len(x) == count
        if (x3 == self.startContour[0] and y3 == self.startContour[1]):
            count -= 1
        for i in range(count):
            self.otherPen.lineTo((x[i],y[i]))
        self.lastPoint = (x3,y3)

    def _closePath(self):
        if not (self.lastPoint[0] == self.startContour[0] and self.lastPoint[1] == self.startContour[1]):
            self._lineTo(self.startContour)

        # round values used by otherPen (a RoboFab SegmentToPointPen) to decide
        # whether to delete duplicate points at start and end of contour
        #TODO(jamesgk) figure out why we have to do this hack, then remove it
        c = self.otherPen.contour
        for i in [0, -1]:
            c[i] = [[round(n, 5) for n in c[i][0]]] + list(c[i][1:])

        self.otherPen.closePath()

    def _endPath(self):
        self.otherPen.endPath()

    def addComponent(self, glyphName, transformation):
        self.otherPen.addComponent(glyphName, transformation)

    def stepsForSegment(self, p1, p2):
        dist = np.linalg.norm(v(p1) - v(p2))
        out = int(dist / self.resolution)
        return out

    def renderCurve(self,p,count):
        curvePoints = []
        t = 1.0 / float(count)
        temp = t * t

        f = p[0]
        fd = 3 * (p[1] - p[0]) * t
        fdd_per_2 = 3 * (p[0] - 2 * p[1] + p[2]) * temp
        fddd_per_2 = 3 * (3 * (p[1] - p[2]) + p[3] - p[0]) * temp * t

        fddd = fddd_per_2 + fddd_per_2
        fdd = fdd_per_2 + fdd_per_2
        fddd_per_6 = fddd_per_2 * (1.0 / 3)

        for i in range(count):
            f = f + fd + fdd_per_2 + fddd_per_6
            fd = fd + fdd + fddd_per_2
            fdd = fdd + fddd
            fdd_per_2 = fdd_per_2 + fddd_per_2
            curvePoints.append(f)

        return curvePoints


def fitBezierSimple(pts):
    T = [np.linalg.norm(pts[i]-pts[i-1]) for i in range(1,len(pts))]
    tsum = np.sum(T)
    T = [0] + T
    T = [np.sum(T[0:i+1])/tsum for i in range(len(pts))]
    T = [[t**3, t**2, t, 1] for t in T]
    T = np.array(T)
    M = np.array([[-1,  3, -3, 1],
                  [ 3, -6,  3, 0],
                  [-3,  3,  0, 0],
                  [ 1,  0,  0, 0]])
    T = T.dot(M)
    T = np.concatenate((T, np.array([[100,0,0,0], [0,0,0,100]])))
    # pts = np.vstack((pts, pts[0] * 100, pts[-1] * 100))
    C = np.linalg.lstsq(T, pts)
    return C[0]


def subdivideLineSegment(pts):
    out = [pts[0]]
    for i in range(1, len(pts)):
        out.append(pts[i-1] + (pts[i] - pts[i-1]) * .5)
        out.append(pts[i])
    return np.array(out)


def fitBezier(pts,tangent0=None,tangent3=None):
    if len(pts < 4):
        pts = subdivideLineSegment(pts)
    T = [np.linalg.norm(pts[i]-pts[i-1]) for i in range(1,len(pts))]
    tsum = np.sum(T)
    T = [0] + T
    T = [np.sum(T[0:i+1])/tsum for i in range(len(pts))]
    T = [[t**3, t**2, t, 1] for t in T]
    T = np.array(T)
    M = np.array([[-1,  3, -3, 1],
                  [ 3, -6,  3, 0],
                  [-3,  3,  0, 0],
                  [ 1,  0,  0, 0]])
    T = T.dot(M)
    n = len(pts)
    pout = pts.copy()
    pout[:,0] -= (T[:,0] * pts[0,0]) + (T[:,3] * pts[-1,0])
    pout[:,1] -= (T[:,0] * pts[0,1]) + (T[:,3] * pts[-1,1])

    TT = np.zeros((n*2,4))
    for i in range(n):
        for j in range(2):
            TT[i*2,j*2] = T[i,j+1]
            TT[i*2+1,j*2+1] = T[i,j+1]
    pout = pout.reshape((n*2,1),order="C")

    if tangent0 != None and tangent3 != None:
        tangentConstraintsT = np.array([
                [tangent0[1], -tangent0[0], 0, 0],
                [0, 0, tangent3[1], -tangent3[0]]
            ])
        tangentConstraintsP = np.array([
                                [pts[0][1]  * -tangent0[0] + pts[0][0]  * tangent0[1]],
                                [pts[-1][1] * -tangent3[0] + pts[-1][0] * tangent3[1]]
                            ])
        TT = np.concatenate((TT, tangentConstraintsT * 1000))
        pout = np.concatenate((pout, tangentConstraintsP * 1000))
    C = np.linalg.lstsq(TT,pout)[0].reshape((2,2))
    return np.array([pts[0], C[0], C[1], pts[-1]])


def segmentGlyph(glyph,resolution=50):
    g1 = glyph.copy()
    g1.clear()
    dp = SubsegmentPointPen(g1, resolution)
    glyph.drawPoints(dp)
    return g1, dp.getSubsegments()


def fitGlyph(glyph, subsegmentGlyph, subsegmentIndices, matchTangents=True):
    outGlyph = glyph.copy()
    outGlyph.clear()
    fitPen = SubsegmentsToCurvesPointPen(outGlyph, subsegmentGlyph, subsegmentIndices)
    fitPen.setMatchTangents(matchTangents)
    # smoothPen = GuessSmoothPointPen(fitPen)
    glyph.drawPoints(fitPen)
    outGlyph.width = subsegmentGlyph.width
    return outGlyph


if __name__ == '__main__':
    p = SubsegmentPen(None, None)
    pts = np.array([
        [0,0],
        [.5,.5],
        [.5,.5],
        [1,1]
    ])
    print np.array(p.renderCurve(pts,10)) * 10
