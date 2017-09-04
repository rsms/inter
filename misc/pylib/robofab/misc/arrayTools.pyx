#
# Various array and rectangle tools, but mostly rectangles, hence the
# name of this module (not).
#

"""
Rewritten to elimate the numpy dependency
"""

import math

def calcBounds(array):
    """Return the bounding rectangle of a 2D points array as a tuple:
    (xMin, yMin, xMax, yMax)
    """
    if len(array) == 0:
        return 0, 0, 0, 0
    xs = [x for x, y in array]
    ys = [y for x, y in array]
    return min(xs), min(ys), max(xs), max(ys)

def updateBounds(bounds, pt, min=min, max=max):
    """Return the bounding recangle of rectangle bounds and point (x, y)."""
    xMin, yMin, xMax, yMax = bounds
    x, y = pt
    return min(xMin, x), min(yMin, y), max(xMax, x), max(yMax, y)

def pointInRect(pt, rect):
    """Return True when point (x, y) is inside rect."""
    xMin, yMin, xMax, yMax = rect
    return (xMin <= pt[0] <= xMax) and (yMin <= pt[1] <= yMax)

def pointsInRect(array, rect):
    """Find out which points or array are inside rect. 
    Returns an array with a boolean for each point.
    """
    if len(array) < 1:
        return []
    xMin, yMin, xMax, yMax = rect
    return [(xMin <= x <= xMax) and (yMin <= y <= yMax) for x, y in array]

def vectorLength(vector):
    """Return the length of the given vector."""
    x, y = vector
    return math.sqrt(x**2 + y**2)

def asInt16(array):
    """Round and cast to 16 bit integer."""
    return [int(math.floor(i+0.5)) for i in array]
    

def normRect(box):
    """Normalize the rectangle so that the following holds:
        xMin <= xMax and yMin <= yMax
    """
    return min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3])

def scaleRect(box, x, y):
    """Scale the rectangle by x, y."""
    return box[0] * x, box[1] * y, box[2] * x, box[3] * y

def offsetRect(box, dx, dy):
    """Offset the rectangle by dx, dy."""
    return box[0]+dx, box[1]+dy, box[2]+dx, box[3]+dy

def insetRect(box, dx, dy):
    """Inset the rectangle by dx, dy on all sides."""
    return box[0]+dx, box[1]+dy, box[2]-dx, box[3]-dy

def sectRect(box1, box2):
    """Return a boolean and a rectangle. If the input rectangles intersect, return
    True and the intersecting rectangle. Return False and (0, 0, 0, 0) if the input
    rectangles don't intersect.
    """
    xMin, yMin, xMax, yMax = (max(box1[0], box2[0]), max(box1[1], box2[1]),
                              min(box1[2], box2[2]), min(box1[3], box2[3]))
    if xMin >= xMax or yMin >= yMax:
        return 0, (0, 0, 0, 0)
    return 1, (xMin, yMin, xMax, yMax)

def unionRect(box1, box2):
    """Return the smallest rectangle in which both input rectangles are fully
    enclosed. In other words, return the total bounding rectangle of both input
    rectangles.
    """
    return (max(box1[0], box2[0]), max(box1[1], box2[1]),
            min(box1[2], box2[2]), min(box1[3], box2[3]))

def rectCenter(box):
    """Return the center of the rectangle as an (x, y) coordinate."""
    return (box[0]+box[2])/2, (box[1]+box[3])/2

def intRect(box):
    """Return the rectangle, rounded off to integer values, but guaranteeing that
    the resulting rectangle is NOT smaller than the original.
    """
    xMin, yMin, xMax, yMax = box
    xMin = int(math.floor(xMin))
    yMin = int(math.floor(yMin))
    xMax = int(math.ceil(xMax))
    yMax = int(math.ceil(yMax))
    return (xMin, yMin, xMax, yMax)


def _test():
    """
    >>> import math
    >>> calcBounds([(0, 40), (0, 100), (50, 50), (80, 10)])
    (0, 10, 80, 100)
    >>> updateBounds((0, 0, 0, 0), (100, 100))
    (0, 0, 100, 100)
    >>> pointInRect((50, 50), (0, 0, 100, 100))
    True
    >>> pointInRect((0, 0), (0, 0, 100, 100))
    True
    >>> pointInRect((100, 100), (0, 0, 100, 100))
    True
    >>> not pointInRect((101, 100), (0, 0, 100, 100))
    True
    >>> list(pointsInRect([(50, 50), (0, 0), (100, 100), (101, 100)], (0, 0, 100, 100)))
    [True, True, True, False]
    >>> vectorLength((3, 4))
    5.0
    >>> vectorLength((1, 1)) == math.sqrt(2)
    True
    >>> list(asInt16([0, 0.1, 0.5, 0.9]))
    [0, 0, 1, 1]
    >>> normRect((0, 10, 100, 200))
    (0, 10, 100, 200)
    >>> normRect((100, 200, 0, 10))
    (0, 10, 100, 200)
    >>> scaleRect((10, 20, 50, 150), 1.5, 2)
    (15.0, 40, 75.0, 300)
    >>> offsetRect((10, 20, 30, 40), 5, 6)
    (15, 26, 35, 46)
    >>> insetRect((10, 20, 50, 60), 5, 10)
    (15, 30, 45, 50)
    >>> insetRect((10, 20, 50, 60), -5, -10)
    (5, 10, 55, 70)
    >>> intersects, rect = sectRect((0, 10, 20, 30), (0, 40, 20, 50))
    >>> not intersects
    True
    >>> intersects, rect = sectRect((0, 10, 20, 30), (5, 20, 35, 50))
    >>> intersects
    1
    >>> rect
    (5, 20, 20, 30)
    >>> unionRect((0, 10, 20, 30), (0, 40, 20, 50))
    (0, 10, 20, 50)
    >>> rectCenter((0, 0, 100, 200))
    (50, 100)
    >>> rectCenter((0, 0, 100, 199.0))
    (50, 99.5)
    >>> intRect((0.9, 2.9, 3.1, 4.1))
    (0, 2, 4, 5)
    """

if __name__ == "__main__":
    import doctest
    doctest.testmod()
