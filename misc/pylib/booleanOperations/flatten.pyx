from __future__ import print_function, division, absolute_import
import math
from fontTools.misc import bezierTools
from fontTools.pens.basePen import decomposeQuadraticSegment
import pyclipper

"""
To Do:
- the stuff listed below
- need to know what kind of curves should be used for
  curve fit--curve or qcurve
- false curves and duplicate points need to be filtered early on

notes:
- the flattened segments *must* be cyclical.
  if they aren't, matching is almost impossible.


optimization ideas:
- the flattening of the output segment in the full contour
  matching is probably expensive.
- there should be a way to flag an input contour as
  entirely used so that it isn't tried and tried and
  tried for segment matches.
- do a faster test when matching segments: when a end
  match is found, jump back input length and grab the
  output segment. test for match with the input.
- cache input contour objects. matching these to incoming
  will be a little difficult because of point names and
  identifiers. alternatively, deal with those after the fact.
- some tests on input before conversion to input objects
  could yield significant speedups. would need to check
  each contour for self intersection and each
  non-self-intersectingcontour for collision with other
  contours. and contours that don't have a hit could be
  skipped. this cound be done roughly with bounds.
  this should probably be done by extenal callers.
- set a proper starting points of the output segments based on known points
  known points are:
    input oncurve points
    if nothing found intersection points (only use this is in the final curve fitting stage)

test cases:
- untouched contour: make clockwise and counter-clockwise tests
  of the same contour
"""
epsilon = 1e-8

# factors for transferring coordinates to and from Clipper
clipperScale = 1 << 17
inverseClipperScale = 1.0 / clipperScale

# approximateSegmentLength setting
_approximateSegmentLength = 5.3


# -------------
# Input Objects
# -------------

# Input

class InputContour(object):

    def __init__(self, contour):
        # gather the point data
        pointPen = ContourPointDataPen()
        contour.drawPoints(pointPen)
        points = pointPen.getData()
        reversedPoints = _reversePoints(points)
        # gather segments
        self.segments = _convertPointsToSegments(points)
        # only calculate once all the flat points.
        # it seems to have some tiny difference and its a lot faster
        # if the flat points are calculated from the reversed input points.
        self.reversedSegments = _convertPointsToSegments(reversedPoints, willBeReversed=True)
        # simple reverse the flat points and store them in the reversedSegments
        index = 0
        for segment in self.segments:
            otherSegment = self.reversedSegments[index]
            otherSegment.flat = segment.getReversedFlatPoints()
            index -= 1
        # get the direction; returns True if counter-clockwise, False otherwise
        self.clockwise = not pyclipper.Orientation(points)
        # store the gathered data
        if self.clockwise:
            self.clockwiseSegments = self.segments
            self.counterClockwiseSegments = self.reversedSegments
        else:
            self.clockwiseSegments = self.reversedSegments
            self.counterClockwiseSegments = self.segments
        # flag indicating if the contour has been used
        self.used = False

    # ----------
    # Attributes
    # ----------

    # the original direction in flat segments

    def _get_originalFlat(self):
        if self.clockwise:
            return self.clockwiseFlat
        else:
            return self.counterClockwiseFlat

    originalFlat = property(_get_originalFlat)

    # the clockwise direction in flat segments

    def _get_clockwiseFlat(self):
        flat = []
        segments = self.clockwiseSegments
        for segment in segments:
            flat.extend(segment.flat)
        return flat

    clockwiseFlat = property(_get_clockwiseFlat)

    # the counter-clockwise direction in flat segments

    def _get_counterClockwiseFlat(self):
        flat = []
        segments = self.counterClockwiseSegments
        for segment in segments:
            flat.extend(segment.flat)
        return flat

    counterClockwiseFlat = property(_get_counterClockwiseFlat)

    def hasOnCurve(self):
        for inputSegment in self.segments:
            if not inputSegment.used and inputSegment.segmentType != "line":
                return True
        return False


class InputSegment(object):

    # __slots__ = ["points", "previousOnCurve", "scaledPreviousOnCurve", "flat", "used"]

    def __init__(self, points=None, previousOnCurve=None, willBeReversed=False):
        if points is None:
            points = []
        self.points = points
        self.previousOnCurve = previousOnCurve
        self.scaledPreviousOnCurve = _scaleSinglePoint(previousOnCurve, scale=clipperScale)
        self.used = False
        self.flat = []
        # if the bcps are equal to the oncurves convert the segment to a line segment.
        # otherwise this causes an error when flattening.
        if self.segmentType == "curve":
            if previousOnCurve == points[0].coordinates and points[1].coordinates == points[-1].coordinates:
                oncurve = points[-1]
                oncurve.segmentType = "line"
                self.points = points = [oncurve]
            elif previousOnCurve[0] == points[0].coordinates[0] == points[1].coordinates[0] == points[-1].coordinates[0]:
                oncurve = points[-1]
                oncurve.segmentType = "line"
                self.points = points = [oncurve]
            elif previousOnCurve[1] == points[0].coordinates[1] == points[1].coordinates[1] == points[-1].coordinates[1]:
                oncurve = points[-1]
                oncurve.segmentType = "line"
                self.points = points = [oncurve]
        # its a reversed segment the flat points will be set later on in the InputContour
        if willBeReversed:
            return
        pointsToFlatten = []
        if self.segmentType == "qcurve":
            assert len(points) >= 0
            flat = []
            currentOnCurve = previousOnCurve
            pointCoordinates = [point.coordinates for point in points]
            for pt1, pt2 in decomposeQuadraticSegment(pointCoordinates[1:]):
                pt0x, pt0y = currentOnCurve
                pt1x, pt1y = pt1
                pt2x, pt2y = pt2
                mid1x = pt0x + 0.66666666666666667 * (pt1x - pt0x)
                mid1y = pt0y + 0.66666666666666667 * (pt1y - pt0y)
                mid2x = pt2x + 0.66666666666666667 * (pt1x - pt2x)
                mid2y = pt2y + 0.66666666666666667 * (pt1y - pt2y)

                convertedQuadPointToFlatten = [currentOnCurve, (mid1x, mid1y), (mid2x, mid2y), pt2]
                flat.extend(_flattenSegment(convertedQuadPointToFlatten))
                currentOnCurve = pt2
            self.flat = flat
            # this shoudl be easy.
            # copy the quad to cubic from fontTools.pens.basePen
        elif self.segmentType == "curve":
            pointsToFlatten = [previousOnCurve] + [point.coordinates for point in points]
        else:
            assert len(points) == 1
            self.flat = [point.coordinates for point in points]
        if pointsToFlatten:
            self.flat = _flattenSegment(pointsToFlatten)
        # if len(self.flat) == 1 and self.segmentType == "curve":
        #     oncurve = self.points[-1]
        #     oncurve.segmentType = "line"
        #     self.points = [oncurve]
        self.flat = _scalePoints(self.flat, scale=clipperScale)
        self.flat = _checkFlatPoints(self.flat)
        self.used = False

    def _get_segmentType(self):
        return self.points[-1].segmentType

    segmentType = property(_get_segmentType)

    def getReversedFlatPoints(self):
        reversedFlatPoints = [self.scaledPreviousOnCurve] + self.flat[:-1]
        reversedFlatPoints.reverse()
        return reversedFlatPoints

    def split(self, tValues):
        """
        Split the segment according the t values
        """
        if self.segmentType == "curve":
            on1 = self.previousOnCurve
            off1 = self.points[0].coordinates
            off2 = self.points[1].coordinates
            on2 = self.points[2].coordinates
            return bezierTools.splitCubicAtT(on1, off1, off2, on2, *tValues)
        elif self.segmentType == "line":
            segments = []
            x1, y1 = self.previousOnCurve
            x2, y2 = self.points[0].coordinates
            dx = x2 - x1
            dy = y2 - y1
            pp = x1, y1
            for t in tValues:
                np = (x1+dx*t, y1+dy*t)
                segments.append([pp, np])
                pp = np
            segments.append([pp, (x2, y2)])
            return segments
        elif self.segmentType == "qcurve":
            raise NotImplementedError
        else:
            raise NotImplementedError

    def tValueForPoint(self, point):
        """
        get a t values for a given point

        required:
            the point must be a point on the curve.
            in an overlap cause the point will be an intersection points wich is alwasy a point on the curve
        """
        if self.segmentType == "curve":
            on1 = self.previousOnCurve
            off1 = self.points[0].coordinates
            off2 = self.points[1].coordinates
            on2 = self.points[2].coordinates
            return _tValueForPointOnCubicCurve(point, (on1, off1, off2, on2))
        elif self.segmentType == "line":
            return _tValueForPointOnLine(point, (self.previousOnCurve, self.points[0].coordinates))
        elif self.segmentType == "qcurve":
            raise NotImplementedError
        else:
            raise NotImplementedError


class InputPoint(object):

    __slots__ = ["coordinates", "segmentType", "smooth", "name", "kwargs"]

    def __init__(self, coordinates, segmentType=None, smooth=False, name=None, kwargs=None):
        x, y = coordinates
        self.coordinates = coordinates
        self.segmentType = segmentType
        self.smooth = smooth
        self.name = name
        self.kwargs = kwargs

    def __getitem__(self, i):
        return self.coordinates[i]

    def copy(self):
        copy = self.__class__(
            coordinates=self.coordinates,
            segmentType=self.segmentType,
            smooth=self.smooth,
            name=self.name,
            kwargs=self.kwargs
        )
        return copy

    def __str__(self):
        return "%s %s" % (self.segmentType, self.coordinates)

    def __repr__(self):
        return self.__str__()


# -------------
# Input Support
# -------------

class ContourPointDataPen:

    """
    Point pen for gathering raw contour data.
    An instance of this pen may only be used for one contour.
    """

    def __init__(self):
        self._points = None
        self._foundStartingPoint = False

    def getData(self):
        """
        Return a list of normalized InputPoint objects
        for the contour drawn with this pen.
        """
        # organize the points into segments
        # 1. make sure there is an on curve
        haveOnCurve = False
        for point in self._points:
            if point.segmentType is not None:
                haveOnCurve = True
                break
        # 2. move the off curves to front of the list
        if haveOnCurve:
            _prepPointsForSegments(self._points)
        # 3. ignore double points on start and end
        firstPoint = self._points[0]
        lastPoint = self._points[-1]
        if firstPoint.segmentType is not None and lastPoint.segmentType is not None:
            if firstPoint.coordinates == lastPoint.coordinates:
                if (firstPoint.segmentType in ["line", "move"]):
                    del self._points[0]
                else:
                    raise AssertionError("Unhandled point type sequence")
        # done
        return self._points

    def beginPath(self):
        assert self._points is None
        self._points = []

    def endPath(self):
        pass

    def addPoint(self, pt, segmentType=None, smooth=False, name=None, **kwargs):
        assert segmentType != "move"
        if not self._foundStartingPoint and segmentType is not None:
            kwargs['startingPoint'] = self._foundStartingPoint = True
        data = InputPoint(
            coordinates=pt,
            segmentType=segmentType,
            smooth=smooth,
            name=name,
            kwargs=kwargs
        )
        self._points.append(data)

    def addComponent(self, baseGlyphName, transformation):
        raise NotImplementedError


def _prepPointsForSegments(points):
    """
    Move any off curves at the end of the contour
    to the beginning of the contour. This makes
    segmentation easier.
    """
    while 1:
        point = points[-1]
        if point.segmentType:
            break
        else:
            point = points.pop()
            points.insert(0, point)
            continue
        break


def _copyPoints(points):
    """
    Make a shallow copy of the points.
    """
    copied = [point.copy() for point in points]
    return copied


def _reversePoints(points):
    """
    Reverse the points. This differs from the
    reversal point pen in RoboFab in that it doesn't
    worry about maintaing the start point position.
    That has no benefit within the context of this module.
    """
    # copy the points
    points = _copyPoints(points)
    # find the first on curve type and recycle
    # it for the last on curve type
    firstOnCurve = None
    for index, point in enumerate(points):
        if point.segmentType is not None:
            firstOnCurve = index
            break
    lastSegmentType = points[firstOnCurve].segmentType
    # reverse the points
    points = reversed(points)
    # work through the reversed remaining points
    final = []
    for point in points:
        segmentType = point.segmentType
        if segmentType is not None:
            point.segmentType = lastSegmentType
            lastSegmentType = segmentType
        final.append(point)
    # move any offcurves at the end of the points
    # to the start of the points
    _prepPointsForSegments(final)
    # done
    return final


def _convertPointsToSegments(points, willBeReversed=False):
    """
    Compile points into InputSegment objects.
    """
    # get the last on curve
    previousOnCurve = None
    for point in reversed(points):
        if point.segmentType is not None:
            previousOnCurve = point.coordinates
            break
    assert previousOnCurve is not None
    # gather the segments
    offCurves = []
    segments = []
    for point in points:
        # off curve, hold.
        if point.segmentType is None:
            offCurves.append(point)
        else:
            segment = InputSegment(
                points=offCurves + [point],
                previousOnCurve=previousOnCurve,
                willBeReversed=willBeReversed
            )
            segments.append(segment)
            offCurves = []
            previousOnCurve = point.coordinates
    assert not offCurves
    return segments


# --------------
# Output Objects
# --------------

class OutputContour(object):

    def __init__(self, pointList):
        if pointList[0] == pointList[-1]:
            del pointList[-1]
        self.clockwise = not pyclipper.Orientation(pointList)
        self.segments = [
            OutputSegment(
                segmentType="flat",
                points=[point]
            ) for point in pointList
        ]

    def _scalePoint(self, point):
        x, y = point
        x = x * inverseClipperScale
        if int(x) == x:
            x = int(x)
        y = y * inverseClipperScale
        if int(y) == y:
            y = int(y)
        return x, y

    # ----------
    # Attributes
    # ----------

    def _get_final(self):
        # XXX this could be optimized:
        # store a fixed value after teh contour is finalized
        # don't do the dymanic searching if that flag is set to True
        for segment in self.segments:
            if not segment.final:
                return False
        return True

    final = property(_get_final)

    # --------------------------
    # Re-Curve and Curve Fitting
    # --------------------------

    def reCurveFromEntireInputContour(self, inputContour):
        """
        Match if entire input contour matches entire output contour,
        allowing for different start point.
        """
        if self.clockwise:
            inputFlat = inputContour.clockwiseFlat
        else:
            inputFlat = inputContour.counterClockwiseFlat
        outputFlat = []
        for segment in self.segments:
            # XXX this could be expensive
            assert segment.segmentType == "flat"
            outputFlat += segment.points
        # test lengths
        haveMatch = False
        if len(inputFlat) == len(outputFlat):
            if inputFlat == outputFlat:
                haveMatch = True
            else:
                inputStart = inputFlat[0]
                if inputStart in outputFlat:
                    # there should be only one occurance of the point
                    # but handle it just in case
                    if outputFlat.count(inputStart) > 1:
                        startIndexes = [index for index, point in enumerate(outputFlat) if point == inputStart]
                    else:
                        startIndexes = [outputFlat.index(inputStart)]
                    # slice and dice to test possible orders
                    for startIndex in startIndexes:
                        test = outputFlat[startIndex:] + outputFlat[:startIndex]
                        if inputFlat == test:
                            haveMatch = True
                            break
        if haveMatch:
            # clear out the flat points
            self.segments = []
            # replace with the appropriate points from the input
            if self.clockwise:
                inputSegments = inputContour.clockwiseSegments
            else:
                inputSegments = inputContour.counterClockwiseSegments
            for inputSegment in inputSegments:
                self.segments.append(
                    OutputSegment(
                        segmentType=inputSegment.segmentType,
                        points=[
                            OutputPoint(
                                coordinates=point.coordinates,
                                segmentType=point.segmentType,
                                smooth=point.smooth,
                                name=point.name,
                                kwargs=point.kwargs
                            )
                            for point in inputSegment.points
                        ],
                        final=True
                    )
                )
                inputSegment.used = True
            # reset the direction of the final contour
            self.clockwise = inputContour.clockwise
            return True
        return False

    def reCurveFromInputContourSegments(self, inputContour):
        return
        # match individual segments
        if self.clockwise:
            inputSegments = inputContour.clockwiseSegments
        else:
            inputSegments = inputContour.counterClockwiseSegments
        for inputSegment in inputSegments:
            # skip used
            if inputSegment.used:
                continue
            # skip if the input contains more points than the entire output contour
            if len(inputSegment.flat) > len(self.segments):
                continue
            # skip if the input end is not in the contour
            inputSegmentLastPoint = inputSegment.flat[-1]
            outputFlat = [segment.points[-1] for segment in self.segments]
            if inputSegmentLastPoint not in outputFlat:
                continue
            # work through all output segments
            for outputSegmentIndex, outputSegment in enumerate(self.segments):
                # skip finalized
                if outputSegment.final:
                    continue
                # skip if the output point doesn't match the input end
                if outputSegment.points[-1] != inputSegmentLastPoint:
                    continue
                # make a set of ranges for slicing the output into a testable list of points
                inputLength = len(inputSegment.flat)
                outputRanges = []
                outputSegmentIndex += 1
                if outputSegmentIndex - inputLength < 0:
                    r1 = (len(self.segments) + outputSegmentIndex - inputLength, len(self.segments))
                    outputRanges.append(r1)
                    r2 = (0, outputSegmentIndex)
                    outputRanges.append(r2)
                else:
                    outputRanges.append((outputSegmentIndex - inputLength, outputSegmentIndex))
                # gather the output segments
                testableOutputSegments = []
                for start, end in outputRanges:
                    testableOutputSegments += self.segments[start:end]
                # create a list of points
                test = []
                for s in testableOutputSegments:
                    # stop if a segment is final
                    if s.final:
                        test = None
                        break
                    test.append(s.points[-1])
                if test == inputSegment.flat and inputSegment.segmentType != "line":
                    # insert new segment
                    newSegment = OutputSegment(
                        segmentType=inputSegment.segmentType,
                        points=[
                            OutputPoint(
                                coordinates=point.coordinates,
                                segmentType=point.segmentType,
                                smooth=point.smooth,
                                name=point.name,
                                kwargs=point.kwargs
                            )
                            for point in inputSegment.points
                        ],
                        final=True
                    )
                    self.segments.insert(outputSegmentIndex, newSegment)
                    # remove old segments
                    # XXX this is sloppy
                    for start, end in outputRanges:
                        if start > outputSegmentIndex:
                            start += 1
                            end += 1
                        del self.segments[start:end]
                    # flag the original as used
                    inputSegment.used = True
                    break
        # ? match line start points (to prevent curve fit in shortened line)
        return False

    def reCurveSubSegmentsCheckInputContoursOnHasCurve(self, inputContours):
        # test is the remaining input contours contains only lineTo points
        # XXX could be cached
        return True
        # for inputContour in inputContours:
        #     if inputContour.used:
        #         continue
        #     if inputContour.hasOnCurve():
        #         return True
        # return False

    def reCurveSubSegments(self, inputContours):
        if not self.segments:
            # its all done
            return
        # the inputContours has some curved segments
        # if not it all the segments will be converted at the end
        if self.reCurveSubSegmentsCheckInputContoursOnHasCurve(inputContours):
            # collect all flat points in a dict of unused inputContours
            # collect both clockwise segment and counterClockwise segments
            # it happens a lot that the directions turns around
            # the clockwise attribute can help but testing the directions is always needed
            # collect all oncurve points as well
            flatInputPointsSegmentDict = dict()
            reversedFlatInputPointsSegmentDict = dict()
            flatIntputOncurves = set()
            for inputContour in inputContours:
                if inputContour.used:
                    continue
                if self.clockwise:
                    inputSegments = inputContour.clockwiseSegments
                    reversedSegments = inputContour.counterClockwiseSegments
                else:
                    inputSegments = inputContour.counterClockwiseSegments
                    reversedSegments = inputContour.clockwiseSegments
                for inputSegment in inputSegments:
                    if inputSegment.used:
                        continue
                    for p in inputSegment.flat:
                        flatInputPointsSegmentDict[p] = inputSegment
                    flatIntputOncurves.add(inputSegment.scaledPreviousOnCurve)

                for inputSegment in reversedSegments:
                    if inputSegment.used:
                        continue
                    for p in inputSegment.flat:
                        reversedFlatInputPointsSegmentDict[p] = inputSegment
                    flatIntputOncurves.add(inputSegment.scaledPreviousOnCurve)
            flatInputPoints = set(flatInputPointsSegmentDict.keys())
            # reset the starting point to a known point.
            # not somewhere in the middle of a flatten point list
            firstSegment = self.segments[0]
            foundStartingPoint = True
            if firstSegment.segmentType == "flat":
                foundStartingPoint = False
                for index, segment in enumerate(self.segments):
                    if segment.segmentType in ["line", "curve", "qcurve"]:
                        foundStartingPoint = True
                        break
                if foundStartingPoint:
                    # if found re index the segments
                    # if there is no known starting point found do it later based on the intersection points
                    self.segments = self.segments[index:] + self.segments[:index]
            # collect all flat points in a intersect segment
            remainingSubSegment = OutputSegment(segmentType="intersect", points=[])
            # store all segments in one big temp list
            newSegments = []
            for index, segment in enumerate(self.segments):
                if segment.segmentType != "flat":
                    # when the segment contains only one points its a line cause it is a single intersection point
                    if len(remainingSubSegment.points) == 1:
                        remainingSubSegment.segmentType = "line"
                        remainingSubSegment.final = True
                        remainingSubSegment.points = [
                                          OutputPoint(
                                                coordinates=self._scalePoint(point),
                                                segmentType="line",
                                                smooth=point.smooth,
                                                name=point.name,
                                                kwargs=point.kwargs
                                              )
                                          for point in remainingSubSegment.points
                                          ]
                    newSegments.append(remainingSubSegment)
                    remainingSubSegment = OutputSegment(segmentType="intersect", points=[])
                    newSegments.append(segment)
                    continue
                remainingSubSegment.points.extend(segment.points)
            newSegments.append(remainingSubSegment)
            # loop over all segments
            for segment in newSegments:
                # handle only segments tagged as intersect
                if segment.segmentType != "intersect":
                    continue
                # skip empty segments
                if not segment.points:
                    continue
                # get al inputSegments, this is an unorderd list of all points no in the the flatInputPoints
                segmentPointsSet = set(segment.points)
                intersectionPoints = segmentPointsSet - flatInputPoints
                # merge both oncurves and intersectionPoints as known points
                possibleStartingPoints = flatIntputOncurves | intersectionPoints
                hasOncurvePoints = segmentPointsSet & flatIntputOncurves
                # if not starting point is found earlier do it here
                foundStartingPointIndex = None
                if not foundStartingPoint:
                    for index, p in enumerate(segment.points):
                        if p in flatIntputOncurves:
                            foundStartingPointIndex = index
                            break
                    if foundStartingPointIndex is None:
                        for index, p in enumerate(segment.points):
                            if p in intersectionPoints:
                                foundStartingPointIndex = index
                                break
                    segment.points = segment.points[foundStartingPointIndex:] + segment.points[:foundStartingPointIndex]
                # split list based on oncurvepoints and intersection points, aka possibleStartingPoints.
                segmentedFlatPoints = [[]]
                for p in segment.points:
                    segmentedFlatPoints[-1].append(p)
                    if p in possibleStartingPoints:
                        segmentedFlatPoints.append([])
                if not segmentedFlatPoints[-1]:
                    segmentedFlatPoints.pop(-1)
                if len(segmentedFlatPoints) > 1 and len(segmentedFlatPoints[0]) == 1:
                    # if last segment is a curve, the start point may be last point on the last segment. If so, merge them.
                    # check if they both have the same inputSegment or reversedInputSegment
                    fp = segmentedFlatPoints[0][0]
                    lp = segmentedFlatPoints[-1][-1]
                    mergeFirstSegments = False
                    if fp in flatInputPoints and lp in flatInputPoints:
                        firstInputSegment = flatInputPointsSegmentDict[fp]
                        lastInputSegment = flatInputPointsSegmentDict[lp]
                        reversedFirstInputSegment = reversedFlatInputPointsSegmentDict[fp]
                        reversedLastInputSegment = reversedFlatInputPointsSegmentDict[lp]
                        if (firstInputSegment.segmentType == reversedFirstInputSegment.segmentType == "curve") or (lastInputSegment.segmentType == reversedLastInputSegment.segmentType == "curve"):
                            if firstInputSegment == lastInputSegment or reversedFirstInputSegment == reversedLastInputSegment:
                                mergeFirstSegments = True
                            # elif len(firstInputSegment.points) > 1 and len(lastInputSegment.points) > 1:
                            elif fp == lastInputSegment.scaledPreviousOnCurve:
                                mergeFirstSegments = True
                            elif lp == firstInputSegment.scaledPreviousOnCurve:
                                mergeFirstSegments = True
                            elif fp == reversedLastInputSegment.scaledPreviousOnCurve:
                                mergeFirstSegments = True
                            elif lp == reversedFirstInputSegment.scaledPreviousOnCurve:
                                mergeFirstSegments = True
                    elif not hasOncurvePoints and _distance(fp, lp):
                        # Merge last segment with first segment if the distance between the last point and the first
                        # point is less than the step distance between the last two points. _approximateSegmentLength
                        # can be significantly smaller than this step size.
                        if len(segmentedFlatPoints[-1]) > 1:
                            f1 = segmentedFlatPoints[-1][-2]
                            f2 = segmentedFlatPoints[-1][-1]
                            stepLen = _distance(f1, f2)
                        else:
                            stepLen = _approximateSegmentLength*clipperScale

                        if _distance(fp, lp) <= stepLen:
                                mergeFirstSegments = True
                    if mergeFirstSegments:
                        segmentedFlatPoints[0] = segmentedFlatPoints[-1] + segmentedFlatPoints[0]
                        segmentedFlatPoints.pop(-1)
                        mergeFirstSegments = False
                convertedSegments = []
                previousIntersectionPoint = None
                if segmentedFlatPoints[-1][-1] in intersectionPoints:
                    previousIntersectionPoint = self._scalePoint(segmentedFlatPoints[-1][-1])
                elif segmentedFlatPoints[0][0] in intersectionPoints:
                    previousIntersectionPoint = self._scalePoint(segmentedFlatPoints[0][0])

                for flatSegment in segmentedFlatPoints:
                    # search two points in the flat segment that is not an inputOncurve or intersection point
                    # to get a proper direction of the flatSegment
                    # based on these two points pick a inputSegment
                    fp = ep = None
                    for p in flatSegment:
                        if p in possibleStartingPoints:
                            continue
                        elif fp is None:
                            fp = p
                        elif ep is None:
                            ep = p
                        else:
                            break
                    canDoFastLine = True
                    if ep is None and ((fp is None) or (len(flatSegment) == 2)):
                        # if fp is not None, then it is a flattened part of a curve, and should be used to derive the input segment.
                        # It may be either the first or second point.
                        # If fp is None, I use the original logic.
                        if fp is None:
                            fp = flatSegment[-1]
                        # flat segment only contains two intersection points or one intersection point and one input oncurve point
                        # this can be ignored cause this is a very small line
                        # and will be converted to a simple line
                        if self.clockwise:
                            inputSegment = reversedFlatInputPointsSegmentDict.get(fp)
                        else:
                            inputSegment = flatInputPointsSegmentDict.get(fp)
                    else:
                        # get inputSegment based on the clockwise settings
                        inputSegment = flatInputPointsSegmentDict[fp]
                        if ep is not None and ep in inputSegment.flat:
                            # if two points are found get indexes
                            fi = inputSegment.flat.index(fp)
                            ei = inputSegment.flat.index(ep)
                            if fi > ei:
                                # if the start index is bigger
                                # get the reversed inputSegment
                                inputSegment = reversedFlatInputPointsSegmentDict[fp]
                        else:
                            # if flat segment is short and has only one point not in intersections and input oncurves
                            # test it against the reversed inputSegment
                            reversedInputSegment = reversedFlatInputPointsSegmentDict[fp]
                            if flatSegment[0] == reversedInputSegment.flat[0] and flatSegment[-1] == reversedInputSegment.flat[-1]:
                                inputSegment = reversedInputSegment
                            elif flatSegment[0] in intersectionPoints and flatSegment[-1] == reversedInputSegment.flat[-1]:
                                inputSegment = reversedInputSegment
                            elif flatSegment[-1] in intersectionPoints and flatSegment[0] == reversedInputSegment.flat[0]:
                                inputSegment = reversedInputSegment
                            canDoFastLine = False
                        # if there is only one point in a flat segment
                        # this is a single intersection points (two crossing lineTo's)
                        if inputSegment.segmentType == "curve":
                            canDoFastLine = False
                    if (len(flatSegment) == 1 or inputSegment is None) and canDoFastLine:
                        # p = flatSegment[0]
                        for p in flatSegment:
                            previousIntersectionPoint = self._scalePoint(p)
                            pointInfo = dict()
                            kwargs = dict()
                            if p in flatInputPointsSegmentDict:
                                lineSegment = flatInputPointsSegmentDict[p]
                                segmentPoint = lineSegment.points[-1]
                                pointInfo["smooth"] = segmentPoint.smooth
                                pointInfo["name"] = segmentPoint.name
                                kwargs.update(segmentPoint.kwargs)
                            convertedSegments.append(OutputPoint(coordinates=previousIntersectionPoint, segmentType="line", kwargs=kwargs, **pointInfo))
                        continue
                    tValues = None
                    lastPointWithAttributes = None
                    if flatSegment[0] == inputSegment.flat[0] and flatSegment[-1] != inputSegment.flat[-1]:
                        # needed the first part of the segment
                        # if previousIntersectionPoint is None:
                        #    previousIntersectionPoint = self._scalePoint(flatSegment[-1])
                        searchPoint = self._scalePoint(flatSegment[-1])
                        tValues = inputSegment.tValueForPoint(searchPoint)
                        curveNeeded = 0
                        replacePointOnNewCurve = [(3, searchPoint)]
                        previousIntersectionPoint = searchPoint
                    elif flatSegment[-1] == inputSegment.flat[-1] and flatSegment[0] != inputSegment.flat[0]:
                        # needed the end of the segment
                        if previousIntersectionPoint is None:
                            previousIntersectionPoint = self._scalePoint(flatSegment[0])
                            convertedSegments.append(OutputPoint(
                                coordinates=previousIntersectionPoint,
                                segmentType="line",
                            ))
                        tValues = inputSegment.tValueForPoint(previousIntersectionPoint)
                        curveNeeded = -1
                        replacePointOnNewCurve = [(0, previousIntersectionPoint)]
                        previousIntersectionPoint = None
                        lastPointWithAttributes = inputSegment.points[-1]
                    elif flatSegment[0] != inputSegment.flat[0] and flatSegment[-1] != inputSegment.flat[-1]:
                        # needed the a middle part of the segment
                        if previousIntersectionPoint is None:
                            previousIntersectionPoint = self._scalePoint(flatSegment[0])
                        tValues = inputSegment.tValueForPoint(previousIntersectionPoint)
                        searchPoint = self._scalePoint(flatSegment[-1])
                        tValues.extend(inputSegment.tValueForPoint(searchPoint))
                        curveNeeded = 1
                        replacePointOnNewCurve = [(0, previousIntersectionPoint), (3, searchPoint)]
                        previousIntersectionPoint = searchPoint
                    else:
                        # take the whole segments as is
                        newCurve = [
                            OutputPoint(
                                coordinates=point.coordinates,
                                segmentType=point.segmentType,
                                smooth=point.smooth,
                                name=point.name,
                                kwargs=point.kwargs
                            )
                            for point in inputSegment.points
                        ]
                        convertedSegments.extend(newCurve)
                        previousIntersectionPoint = None
                    # if we found some tvalue, split the curve and get the requested parts of the splitted curves
                    if tValues:
                        newCurve = inputSegment.split(tValues)
                        newCurve = list(newCurve[curveNeeded])
                        for i, replace in replacePointOnNewCurve:
                            newCurve[i] = replace
                        newCurve = [OutputPoint(coordinates=p, segmentType=None) for p in newCurve[1:]]
                        newCurve[-1].segmentType = inputSegment.segmentType
                        if lastPointWithAttributes is not None:
                            newCurve[-1].smooth = lastPointWithAttributes.smooth
                            newCurve[-1].name = lastPointWithAttributes.name
                            newCurve[-1].kwargs = lastPointWithAttributes.kwargs
                        convertedSegments.extend(newCurve)
                # replace the the points with the converted segments
                segment.points = convertedSegments
                segment.segmentType = "reCurved"
            self.segments = newSegments
        # XXX convert all of the remaining segments to lines
        for segment in self.segments:
            if not segment.points:
                continue
            if segment.segmentType not in ["intersect", "flat"]:
                continue
            segment.segmentType = "line"
            segment.points = [
                OutputPoint(
                    coordinates=self._scalePoint(point),
                    segmentType="line",
                    # smooth=point.smooth,
                    # name=point.name,
                    # kwargs=point.kwargs
                )
                for point in segment.points
            ]

    # ----
    # Draw
    # ----

    def drawPoints(self, pointPen):
        pointPen.beginPath()
        points = []
        for segment in self.segments:
            points.extend(segment.points)

        hasOnCurve = False
        originalStartingPoints = []
        for index, point in enumerate(points):
            if point.segmentType is not None:
                hasOnCurve = True
                if point.kwargs is not None and point.kwargs.get("startingPoint"):
                    distanceFromOrigin = math.hypot(*point)
                    originalStartingPoints.append((distanceFromOrigin, index))
        if originalStartingPoints:
            # use the original starting point that is closest to the origin
            startingPointIndex = sorted(originalStartingPoints)[0][1]
            points = points[startingPointIndex:] + points[:startingPointIndex]
        elif hasOnCurve:
            while points[0].segmentType is None:
                p = points.pop(0)
                points.append(p)
        previousPointCoordinates = None
        for point in points:
            if previousPointCoordinates is not None and point.segmentType and tuple(point.coordinates) == previousPointCoordinates:
                continue
            kwargs = {}
            if point.kwargs is not None:
                kwargs = point.kwargs
            pointPen.addPoint(
                point.coordinates,
                segmentType=point.segmentType,
                smooth=point.smooth,
                name=point.name,
                **kwargs
            )
            if point.segmentType:
                previousPointCoordinates = tuple(point.coordinates)
            else:
                previousPointCoordinates = None
        pointPen.endPath()


class OutputSegment(object):

    __slots__ = ["segmentType", "points", "final"]

    def __init__(self, segmentType=None, points=None, final=False):
        self.segmentType = segmentType
        if points is None:
            points = []
        self.points = points
        self.final = final


class OutputPoint(InputPoint):
    pass


# ----------
# Misc. Math
# ----------

def _tValueForPointOnCubicCurve(point, cubicCurve, isHorizontal=0):
    """
    Finds a t value on a curve from a point.
    The points must be originaly be a point on the curve.
    This will only back trace the t value, needed to split the curve in parts
    """
    pt1, pt2, pt3, pt4 = cubicCurve
    a, b, c, d = bezierTools.calcCubicParameters(pt1, pt2, pt3, pt4)
    solutions = bezierTools.solveCubic(a[isHorizontal], b[isHorizontal], c[isHorizontal],
        d[isHorizontal] - point[isHorizontal])
    solutions = [t for t in solutions if 0 <= t < 1]
    if not solutions and not isHorizontal:
        # can happen that a horizontal line doens intersect, try the vertical
        return _tValueForPointOnCubicCurve(point, (pt1, pt2, pt3, pt4), isHorizontal=1)
    if len(solutions) > 1:
        intersectionLenghts = {}
        for t in solutions:
            tp = _getCubicPoint(t, pt1, pt2, pt3, pt4)
            dist = _distance(tp, point)
            intersectionLenghts[dist] = t
        minDist = min(intersectionLenghts.keys())
        solutions = [intersectionLenghts[minDist]]
    return solutions


def _tValueForPointOnQuadCurve(point, pts, isHorizontal=0):
    quadSegments = decomposeQuadraticSegment(pts[1:])
    previousOnCurve = pts[0]
    solutionsDict = dict()
    for index, (pt1, pt2) in enumerate(quadSegments):
        a, b, c = bezierTools.calcQuadraticParameters(previousOnCurve, pt1, pt2)
        subSolutions = bezierTools.solveQuadratic(a[isHorizontal], b[isHorizontal], c[isHorizontal] - point[isHorizontal])
        subSolutions = [t for t in subSolutions if 0 <= t < 1]
        for t in subSolutions:
            solutionsDict[(t, index)] = _getQuadPoint(t, previousOnCurve, pt1, pt2)
        previousOnCurve = pt2
    solutions = list(solutionsDict.keys())
    if not solutions and not isHorizontal:
        return _tValueForPointOnQuadCurve(point, pts, isHorizontal=1)
    if len(solutions) > 1:
        intersectionLenghts = {}
        for t in solutions:
            tp = solutionsDict[t]
            dist = _distance(tp, point)
            intersectionLenghts[dist] = t
        minDist = min(intersectionLenghts.keys())
        solutions = [intersectionLenghts[minDist]]
    return solutions


def _tValueForPointOnLine(point, line):
    pt1, pt2 = line
    dist = _distance(pt1, point)
    totalDist = _distance(pt1, pt2)
    return [dist / totalDist]


def _scalePoints(points, scale=1, convertToInteger=True):
    """
    Scale points and optionally convert them to integers.
    """
    if convertToInteger:
        points = [
            (int(round(x * scale)), int(round(y * scale)))
            for (x, y) in points
        ]
    else:
        points = [(x * scale, y * scale) for (x, y) in points]
    return points


def _scaleSinglePoint(point, scale=1, convertToInteger=True):
    """
    Scale a single point
    """
    x, y = point
    if convertToInteger:
        return int(round(x * scale)), int(round(y * scale))
    else:
        return (x * scale, y * scale)


def _intPoint(pt):
    return int(round(pt[0])), int(round(pt[1]))


def _checkFlatPoints(points):
    _points = []
    previousX = previousY = None
    for x, y in points:
        if x == previousX:
            continue
        elif y == previousY:
            continue
        if (x, y) not in _points:
            # is it possible that two flat point are on top of eachother???
            _points.append((x, y))
        previousX, previousY = x, y
    if _points[-1] != points[-1]:
        _points[-1] = points[-1]
    return _points


"""
The curve flattening code was forked and modified from RoboFab's FilterPen.
That code was written by Erik van Blokland.
"""


def _flattenSegment(segment, approximateSegmentLength=_approximateSegmentLength):
    """
    Flatten the curve segment int a list of points.
    The first and last points in the segment must be
    on curves. The returned list of points will not
    include the first on curve point.

    false curves (where the off curves are not any
    different from the on curves) must not be sent here.
    duplicate points must not be sent here.
    """
    onCurve1, offCurve1, offCurve2, onCurve2 = segment
    if _pointOnLine(onCurve1, onCurve2, offCurve1) and _pointOnLine(onCurve1, onCurve2, offCurve2):
        return [onCurve2]
    est = _estimateCubicCurveLength(onCurve1, offCurve1, offCurve2, onCurve2) / approximateSegmentLength
    flat = []
    minStep = 0.1564
    step = 1.0 / est
    if step > .3:
        step = minStep
    t = step
    while t < 1:
        pt = _getCubicPoint(t, onCurve1, offCurve1, offCurve2, onCurve2)
        # ignore when point is in the same direction as the on - off curve line
        if not _pointOnLine(offCurve2, onCurve2, pt) and not _pointOnLine(onCurve1, offCurve1, pt):
            flat.append(pt)
        t += step
    flat.append(onCurve2)
    return flat


def _distance(pt1, pt2):
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)


def _pointOnLine(pt1, pt2, a):
    return abs(_distance(pt1, a) + _distance(a, pt2) - _distance(pt1, pt2)) < epsilon


def _estimateCubicCurveLength(pt0, pt1, pt2, pt3, precision=10):
    """
    Estimate the length of this curve by iterating
    through it and averaging the length of the flat bits.
    """
    points = []
    length = 0
    step = 1.0 / precision
    factors = range(0, precision + 1)
    for i in factors:
        points.append(_getCubicPoint(i * step, pt0, pt1, pt2, pt3))
    for i in range(len(points) - 1):
        pta = points[i]
        ptb = points[i + 1]
        length += _distance(pta, ptb)
    return length


def _mid(pt1, pt2):
    """
    (Point, Point) -> Point
    Return the point that lies in between the two input points.
    """
    (x0, y0), (x1, y1) = pt1, pt2
    return 0.5 * (x0 + x1), 0.5 * (y0 + y1)


def _getCubicPoint(t, pt0, pt1, pt2, pt3):
    if t == 0:
        return pt0
    if t == 1:
        return pt3
    if t == 0.5:
        a = _mid(pt0, pt1)
        b = _mid(pt1, pt2)
        c = _mid(pt2, pt3)
        d = _mid(a, b)
        e = _mid(b, c)
        return _mid(d, e)
    else:
        cx = (pt1[0] - pt0[0]) * 3.0
        cy = (pt1[1] - pt0[1]) * 3.0
        bx = (pt2[0] - pt1[0]) * 3.0 - cx
        by = (pt2[1] - pt1[1]) * 3.0 - cy
        ax = pt3[0] - pt0[0] - cx - bx
        ay = pt3[1] - pt0[1] - cy - by
        t3 = t ** 3
        t2 = t * t
        x = ax * t3 + bx * t2 + cx * t + pt0[0]
        y = ay * t3 + by * t2 + cy * t + pt0[1]
        return x, y


def _getQuadPoint(t, pt0, pt1, pt2):
    if t == 0:
        return pt0
    if t == 1:
        return pt2
    else:
        cx = pt0[0]
        cy = pt0[1]
        bx = (pt1[0] - cx) * 2.0
        by = (pt1[1] - cy) * 2.0
        ax = pt2[0] - cx - bx
        ay = pt2[1] - cy - by
        x = ax * t**2 + bx * t + cx
        y = ay * t**2 + by * t + cy
        return x, y
