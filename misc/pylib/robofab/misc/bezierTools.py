"""fontTools.misc.bezierTools.py -- tools for working with bezier path segments.
Rewritten to elimate the numpy dependency
"""


__all__ = [
    "calcQuadraticBounds",
    "calcCubicBounds",
    "splitLine",
    "splitQuadratic",
    "splitCubic",
    "splitQuadraticAtT",
    "splitCubicAtT",
    "solveQuadratic",
    "solveCubic",
]

from robofab.misc.arrayTools import calcBounds

epsilon = 1e-12


def calcQuadraticBounds(pt1, pt2, pt3):
    """Return the bounding rectangle for a qudratic bezier segment.
    pt1 and pt3 are the "anchor" points, pt2 is the "handle".

        >>> calcQuadraticBounds((0, 0), (50, 100), (100, 0))
        (0, 0, 100, 50.0)
        >>> calcQuadraticBounds((0, 0), (100, 0), (100, 100))
        (0.0, 0.0, 100, 100)
    """
    (ax, ay), (bx, by), (cx, cy) = calcQuadraticParameters(pt1, pt2, pt3)
    ax2 = ax*2.0
    ay2 = ay*2.0
    roots = []
    if ax2 != 0:
        roots.append(-bx/ax2)
    if ay2 != 0:
        roots.append(-by/ay2)
    points = [(ax*t*t + bx*t + cx, ay*t*t + by*t + cy) for t in roots if 0 <= t < 1] + [pt1, pt3]
    return calcBounds(points)


def calcCubicBounds(pt1, pt2, pt3, pt4):
    """Return the bounding rectangle for a cubic bezier segment.
    pt1 and pt4 are the "anchor" points, pt2 and pt3 are the "handles".

        >>> calcCubicBounds((0, 0), (25, 100), (75, 100), (100, 0))
        (0, 0, 100, 75.0)
        >>> calcCubicBounds((0, 0), (50, 0), (100, 50), (100, 100))
        (0.0, 0.0, 100, 100)
        >>> calcCubicBounds((50, 0), (0, 100), (100, 100), (50, 0))
        (35.566243270259356, 0, 64.43375672974068, 75.0)
    """
    (ax, ay), (bx, by), (cx, cy), (dx, dy) = calcCubicParameters(pt1, pt2, pt3, pt4)
    # calc first derivative
    ax3 = ax * 3.0
    ay3 = ay * 3.0
    bx2 = bx * 2.0
    by2 = by * 2.0
    xRoots = [t for t in solveQuadratic(ax3, bx2, cx) if 0 <= t < 1]
    yRoots = [t for t in solveQuadratic(ay3, by2, cy) if 0 <= t < 1]
    roots = xRoots + yRoots
    
    points = [(ax*t*t*t + bx*t*t + cx * t + dx, ay*t*t*t + by*t*t + cy * t + dy) for t in roots] + [pt1, pt4]
    return calcBounds(points)


def splitLine(pt1, pt2, where, isHorizontal):
    """Split the line between pt1 and pt2 at position 'where', which
    is an x coordinate if isHorizontal is False, a y coordinate if
    isHorizontal is True. Return a list of two line segments if the
    line was successfully split, or a list containing the original
    line.

        >>> printSegments(splitLine((0, 0), (100, 200), 50, False))
        ((0, 0), (50.0, 100.0))
        ((50.0, 100.0), (100, 200))
        >>> printSegments(splitLine((0, 0), (100, 200), 50, True))
        ((0, 0), (25.0, 50.0))
        ((25.0, 50.0), (100, 200))
        >>> printSegments(splitLine((0, 0), (100, 100), 50, True))
        ((0, 0), (50.0, 50.0))
        ((50.0, 50.0), (100, 100))
        >>> printSegments(splitLine((0, 0), (100, 100), 100, True))
        ((0, 0), (100, 100))
        >>> printSegments(splitLine((0, 0), (100, 100), 0, True))
        ((0, 0), (0.0, 0.0))
        ((0.0, 0.0), (100, 100))
        >>> printSegments(splitLine((0, 0), (100, 100), 0, False))
        ((0, 0), (0.0, 0.0))
        ((0.0, 0.0), (100, 100))
    """
    pt1x, pt1y = pt1
    pt2x, pt2y = pt2
    
    ax = (pt2x - pt1x)
    ay = (pt2y - pt1y)
    
    bx = pt1x
    by = pt1y
    
    ax1 = (ax, ay)[isHorizontal]
    
    if ax1 == 0:
        return [(pt1, pt2)]
        
    t = float(where - (bx, by)[isHorizontal]) / ax1
    if 0 <= t < 1:
        midPt = ax * t + bx, ay * t + by
        return [(pt1, midPt), (midPt, pt2)]
    else:
        return [(pt1, pt2)]


def splitQuadratic(pt1, pt2, pt3, where, isHorizontal):
    """Split the quadratic curve between pt1, pt2 and pt3 at position 'where',
    which is an x coordinate if isHorizontal is False, a y coordinate if
    isHorizontal is True. Return a list of curve segments.

        >>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 150, False))
        ((0, 0), (50, 100), (100, 0))
        >>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 50, False))
        ((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
        ((50.0, 50.0), (75.0, 50.0), (100.0, 0.0))
        >>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 25, False))
        ((0.0, 0.0), (12.5, 25.0), (25.0, 37.5))
        ((25.0, 37.5), (62.5, 75.0), (100.0, 0.0))
        >>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 25, True))
        ((0.0, 0.0), (7.32233047034, 14.6446609407), (14.6446609407, 25.0))
        ((14.6446609407, 25.0), (50.0, 75.0), (85.3553390593, 25.0))
        ((85.3553390593, 25.0), (92.6776695297, 14.6446609407), (100.0, -7.1054273576e-15))
        >>> # XXX I'm not at all sure if the following behavior is desirable:
        >>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 50, True))
        ((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
        ((50.0, 50.0), (50.0, 50.0), (50.0, 50.0))
        ((50.0, 50.0), (75.0, 50.0), (100.0, 0.0))
    """
    a, b, c = calcQuadraticParameters(pt1, pt2, pt3)
    solutions = solveQuadratic(a[isHorizontal], b[isHorizontal],
        c[isHorizontal] - where)
    solutions = [t for t in solutions if 0 <= t < 1]
    solutions.sort()
    if not solutions:
        return [(pt1, pt2, pt3)]
    return _splitQuadraticAtT(a, b, c, *solutions)


def splitCubic(pt1, pt2, pt3, pt4, where, isHorizontal):
    """Split the cubic curve between pt1, pt2, pt3 and pt4 at position 'where',
    which is an x coordinate if isHorizontal is False, a y coordinate if
    isHorizontal is True. Return a list of curve segments.

        >>> printSegments(splitCubic((0, 0), (25, 100), (75, 100), (100, 0), 150, False))
        ((0, 0), (25, 100), (75, 100), (100, 0))
        >>> printSegments(splitCubic((0, 0), (25, 100), (75, 100), (100, 0), 50, False))
        ((0.0, 0.0), (12.5, 50.0), (31.25, 75.0), (50.0, 75.0))
        ((50.0, 75.0), (68.75, 75.0), (87.5, 50.0), (100.0, 0.0))
        >>> printSegments(splitCubic((0, 0), (25, 100), (75, 100), (100, 0), 25, True))
        ((0.0, 0.0), (2.2937927384, 9.17517095361), (4.79804488188, 17.5085042869), (7.47413641001, 25.0))
        ((7.47413641001, 25.0), (31.2886200204, 91.6666666667), (68.7113799796, 91.6666666667), (92.52586359, 25.0))
        ((92.52586359, 25.0), (95.2019551181, 17.5085042869), (97.7062072616, 9.17517095361), (100.0, 1.7763568394e-15))
    """
    a, b, c, d = calcCubicParameters(pt1, pt2, pt3, pt4)
    solutions = solveCubic(a[isHorizontal], b[isHorizontal], c[isHorizontal],
        d[isHorizontal] - where)
    solutions = [t for t in solutions if 0 <= t < 1]
    solutions.sort()
    if not solutions:
        return [(pt1, pt2, pt3, pt4)]
    return _splitCubicAtT(a, b, c, d, *solutions)


def splitQuadraticAtT(pt1, pt2, pt3, *ts):
    """Split the quadratic curve between pt1, pt2 and pt3 at one or more
    values of t. Return a list of curve segments.

        >>> printSegments(splitQuadraticAtT((0, 0), (50, 100), (100, 0), 0.5))
        ((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
        ((50.0, 50.0), (75.0, 50.0), (100.0, 0.0))
        >>> printSegments(splitQuadraticAtT((0, 0), (50, 100), (100, 0), 0.5, 0.75))
        ((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
        ((50.0, 50.0), (62.5, 50.0), (75.0, 37.5))
        ((75.0, 37.5), (87.5, 25.0), (100.0, 0.0))
    """
    a, b, c = calcQuadraticParameters(pt1, pt2, pt3)
    return _splitQuadraticAtT(a, b, c, *ts)


def splitCubicAtT(pt1, pt2, pt3, pt4, *ts):
    """Split the cubic curve between pt1, pt2, pt3 and pt4 at one or more
    values of t. Return a list of curve segments.
        
        >>> printSegments(splitCubicAtT((0, 0), (25, 100), (75, 100), (100, 0), 0.5))
        ((0.0, 0.0), (12.5, 50.0), (31.25, 75.0), (50.0, 75.0))
        ((50.0, 75.0), (68.75, 75.0), (87.5, 50.0), (100.0, 0.0))
        >>> printSegments(splitCubicAtT((0, 0), (25, 100), (75, 100), (100, 0), 0.5, 0.75))
        ((0.0, 0.0), (12.5, 50.0), (31.25, 75.0), (50.0, 75.0))
        ((50.0, 75.0), (59.375, 75.0), (68.75, 68.75), (77.34375, 56.25))
        ((77.34375, 56.25), (85.9375, 43.75), (93.75, 25.0), (100.0, 0.0))
    """
    a, b, c, d = calcCubicParameters(pt1, pt2, pt3, pt4)
    return _splitCubicAtT(a, b, c, d, *ts)


def _splitQuadraticAtT(a, b, c, *ts):
    ts = list(ts)
    segments = []
    ts.insert(0, 0.0)
    ts.append(1.0)
    ax, ay = a
    bx, by = b
    cx, cy = c
    for i in range(len(ts) - 1):
        t1 = ts[i]
        t2 = ts[i+1]
        delta = (t2 - t1)
        # calc new a, b and c
        a1x = ax * delta**2
        a1y = ay * delta**2
        b1x = (2*ax*t1 + bx) * delta
        b1y = (2*ay*t1 + by) * delta
        c1x = ax*t1**2 + bx*t1 + cx
        c1y = ay*t1**2 + by*t1 + cy
    
        pt1, pt2, pt3 = calcQuadraticPoints((a1x, a1y), (b1x, b1y), (c1x, c1y))
        segments.append((pt1, pt2, pt3))
    return segments


def _splitCubicAtT(a, b, c, d, *ts):
    ts = list(ts)
    ts.insert(0, 0.0)
    ts.append(1.0)
    segments = []
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d
    for i in range(len(ts) - 1):
        t1 = ts[i]
        t2 = ts[i+1]
        delta = (t2 - t1)
        # calc new a, b, c and d
        a1x = ax * delta**3
        a1y = ay * delta**3
        b1x = (3*ax*t1 + bx) * delta**2
        b1y = (3*ay*t1 + by) * delta**2
        c1x = (2*bx*t1 + cx + 3*ax*t1**2) * delta
        c1y = (2*by*t1 + cy + 3*ay*t1**2) * delta
        d1x = ax*t1**3 + bx*t1**2 + cx*t1 + dx
        d1y = ay*t1**3 + by*t1**2 + cy*t1 + dy
        pt1, pt2, pt3, pt4 = calcCubicPoints((a1x, a1y), (b1x, b1y), (c1x, c1y), (d1x, d1y))
        segments.append((pt1, pt2, pt3, pt4))
    return segments


#
# Equation solvers.
#

from math import sqrt, acos, cos, pi


def solveQuadratic(a, b, c,
        sqrt=sqrt):
    """Solve a quadratic equation where a, b and c are real.
        a*x*x + b*x + c = 0
    This function returns a list of roots. Note that the returned list
    is neither guaranteed to be sorted nor to contain unique values!
    """
    if abs(a) < epsilon:
        if abs(b) < epsilon:
            # We have a non-equation; therefore, we have no valid solution
            roots = []
        else:
            # We have a linear equation with 1 root.
            roots = [-c/b]
    else:
        # We have a true quadratic equation.  Apply the quadratic formula to find two roots.
        DD = b*b - 4.0*a*c
        if DD >= 0.0:
            rDD = sqrt(DD)
            roots = [(-b+rDD)/2.0/a, (-b-rDD)/2.0/a]
        else:
            # complex roots, ignore
            roots = []
    return roots


def solveCubic(a, b, c, d,
        abs=abs, pow=pow, sqrt=sqrt, cos=cos, acos=acos, pi=pi):
    """Solve a cubic equation where a, b, c and d are real.
        a*x*x*x + b*x*x + c*x + d = 0
    This function returns a list of roots. Note that the returned list
    is neither guaranteed to be sorted nor to contain unique values!
    """
    #
    # adapted from:
    #   CUBIC.C - Solve a cubic polynomial
    #   public domain by Ross Cottrell
    # found at: http://www.strangecreations.com/library/snippets/Cubic.C
    #
    if abs(a) < epsilon:
        # don't just test for zero; for very small values of 'a' solveCubic()
        # returns unreliable results, so we fall back to quad.
        return solveQuadratic(b, c, d)
    a = float(a)
    a1 = b/a
    a2 = c/a
    a3 = d/a
    
    Q = (a1*a1 - 3.0*a2)/9.0
    R = (2.0*a1*a1*a1 - 9.0*a1*a2 + 27.0*a3)/54.0
    R2_Q3 = R*R - Q*Q*Q

    if R2_Q3 < 0:
        theta = acos(R/sqrt(Q*Q*Q))
        rQ2 = -2.0*sqrt(Q)
        x0 = rQ2*cos(theta/3.0) - a1/3.0
        x1 = rQ2*cos((theta+2.0*pi)/3.0) - a1/3.0
        x2 = rQ2*cos((theta+4.0*pi)/3.0) - a1/3.0
        return [x0, x1, x2]
    else:
        if Q == 0 and R == 0:
            x = 0
        else:
            x = pow(sqrt(R2_Q3)+abs(R), 1/3.0)
            x = x + Q/x
        if R >= 0.0:
            x = -x
        x = x - a1/3.0
        return [x]


#
# Conversion routines for points to parameters and vice versa
#

def calcQuadraticParameters(pt1, pt2, pt3):
    x2, y2 = pt2
    x3, y3 = pt3
    cx, cy = pt1
    bx = (x2 - cx) * 2.0
    by = (y2 - cy) * 2.0
    ax = x3 - cx - bx
    ay = y3 - cy - by
    return (ax, ay), (bx, by), (cx, cy)


def calcCubicParameters(pt1, pt2, pt3, pt4):
    x2, y2 = pt2
    x3, y3 = pt3
    x4, y4 = pt4
    dx, dy = pt1
    cx = (x2 -dx) * 3.0
    cy = (y2 -dy) * 3.0
    bx = (x3 - x2) * 3.0 - cx
    by = (y3 - y2) * 3.0 - cy
    ax = x4 - dx - cx - bx
    ay = y4 - dy - cy - by
    return (ax, ay), (bx, by), (cx, cy), (dx, dy)


def calcQuadraticPoints(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    x1 = cx
    y1 = cy
    x2 = (bx * 0.5) + cx
    y2 = (by * 0.5) + cy
    x3 = ax + bx + cx
    y3 = ay + by + cy
    return (x1, y1), (x2, y2), (x3, y3)


def calcCubicPoints(a, b, c, d):
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d
    x1 = dx
    y1 = dy
    x2 = (cx / 3.0) + dx
    y2 = (cy / 3.0) + dy
    x3 = (bx + cx) / 3.0 + x2
    y3 = (by + cy) / 3.0 + y2
    x4 = ax + dx + cx + bx
    y4 = ay + dy + cy + by
    return (x1, y1), (x2, y2), (x3, y3), (x4, y4)


def _segmentrepr(obj):
    """
        >>> _segmentrepr([1, [2, 3], [], [[2, [3, 4], [0.1, 2.2]]]])
        '(1, (2, 3), (), ((2, (3, 4), (0.1, 2.2))))'
    """
    try:
        it = iter(obj)
    except TypeError:
        return str(obj)
    else:
        return "(%s)" % ", ".join([_segmentrepr(x) for x in it])


def printSegments(segments):
    """Helper for the doctests, displaying each segment in a list of
    segments on a single line as a tuple.
    """
    for segment in segments:
        print _segmentrepr(segment)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
