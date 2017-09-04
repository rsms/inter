"""

    Speed comparison between the fontTools numpy based arrayTools and bezierTools,
    and the pure python implementation in robofab.path.arrayTools and robofab.path.bezierTools

"""

import time

from fontTools.misc import arrayTools
from fontTools.misc import bezierTools

import numpy

import robofab.misc.arrayTools as noNumpyArrayTools
import robofab.misc.bezierTools as noNumpyBezierTools

################

pt1 = (100, 100)
pt2 = (200, 20)
pt3 = (30, 580)
pt4 = (153, 654)
rect = [20, 20, 100, 100]

## loops
c = 10000

print "(loop %s)"%c


print "with numpy:"
print "calcQuadraticParameters\t\t",
n = time.time()
for i in range(c):
    bezierTools.calcQuadraticParameters(pt1, pt2, pt3)
print time.time() - n

print "calcBounds\t\t\t",
n = time.time()
for i in range(c):
    arrayTools.calcBounds([pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3])
print time.time() - n

print "pointsInRect\t\t\t",
n = time.time()
for i in range(c):
    arrayTools.pointsInRect([pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3, pt4], rect)
print time.time() - n

print "calcQuadraticBounds\t\t",
n = time.time()
for i in range(c):
    bezierTools.calcQuadraticBounds(pt1, pt2, pt3)
print time.time() - n

print "calcCubicBounds\t\t\t",
n = time.time()
for i in range(c):
    bezierTools.calcCubicBounds(pt1, pt2, pt3, pt4)
print time.time() - n

print 
##############

print "no-numpy"
print "calcQuadraticParameters\t\t",
n = time.time()
for i in range(c):
    noNumpyBezierTools.calcQuadraticParameters(pt1, pt2, pt3)
print time.time() - n

print "calcBounds\t\t\t",
n = time.time()
for i in range(c):
    noNumpyArrayTools.calcBounds([pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3])
print time.time() - n

print "pointsInRect\t\t\t",
n = time.time()
for i in range(c):
    noNumpyArrayTools.pointsInRect([pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3, pt1, pt2, pt3, pt4], rect)
print time.time() - n

print "calcQuadraticBounds\t\t",
n = time.time()
for i in range(c):
    noNumpyBezierTools.calcQuadraticBounds(pt1, pt2, pt3)
print time.time() - n

print "calcCubicBounds\t\t\t",
n = time.time()
for i in range(c):
    noNumpyBezierTools.calcCubicBounds(pt1, pt2, pt3, pt4)
print time.time() - n
    


   
