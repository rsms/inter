from robofab.pens.filterPen import flattenGlyph
from robofab.objects.objectsRF import RGlyph as _RGlyph
import math

_EPSILON = 1e-15


def normalise(a1, a2):
	"""Normalise this vector to length 1"""
	n = math.sqrt((a1*a1)+(a2*a2))
	return (a1/n, a2/n)

def inbetween((a1, a2), (b1, b2), (c1, c2)):
	"""Return True if point b is in between points a and c."""
	x = (a1-_EPSILON<=b1<=c1+_EPSILON) or (a1+_EPSILON>=b1>=c1-_EPSILON)
	y = (a2-_EPSILON<=b2<=c2+_EPSILON) or (a2+_EPSILON>=b2>=c2-_EPSILON)
	return x == y == True

def sectlines((a1, a2), (p1, p2), (b1, b2), (q1, q2)):
	'''Calculate the intersection point of two straight lines. Result in floats.'''
	if (a1, a2) == (p1, p2):
		return None
	r1 = a1-p1
	r2 = a2-p2
	r1, r2 = normalise(r1, r2)
	s1 = b1-q1
	s2 = b2-q2
	s1, s2 = normalise(s1, s2)
	f = float(s1*r2 - s2*r1)
	if f == 0:
		return None
	mu = (r1*(q2 - p2) + r2*(p1 - q1)) / f
	m1 = mu*s1 + q1
	m2 = mu*s2 + q2
	if (m1, m2) == (a1, a2):
		return None
	if inbetween((a1, a2), (m1, m2), (p1,p2)) and inbetween((b1, b2), (m1, m2), (q1,q2)):
		return m1, m2
	else:
		return None
	
def _makeFlat(aGlyph, segmentLength = 10):
	"""Helper function to flatten the glyph with a given approximate segment length."""
	return flattenGlyph(aGlyph, segmentLength)

def intersect(aGlyph,  startPt, endPt, segmentLength=10):
	"""Find the intersections between a glyph and a straight line."""
	flat = _makeFlat(aGlyph)
	return _intersect(flat, startPt, endPt, segmentLength)

def _intersect(flat,  startPt, endPt, segmentLength=10):
	"""Find the intersections between a flattened glyph and a straight line."""
	if len(flat.contours) == 0:
		return None
	if startPt == endPt:
		return None
	sect = None
	intersections = {}
	# new contains the flattened outline
	for c in flat:
		l =len(c.points)
		for i in range(l):
			cur = c.points[i]
			next = c.points[(i+1)%l]
			sect = sectlines((cur.x, cur.y), (next.x, next.y), startPt, endPt)
			if sect is None:
				continue
			intersections[sect] = 1
	return intersections.keys()

def intersectGlyphs(glyphA, glyphB, segmentLength=10):
	"""Approximate the intersection points between two glyphs by
	flattening both glyphs and checking each tiny segment for
	intersections. Slow, but perhaps more realistic then 
	solving the equasions.
	
	Seems to work for basic curves and straights, but untested
	for edges cases, alsmost hits, near hits, double points, crap like that.
	"""
	flatA = _makeFlat(glyphA)
	flatB = _makeFlat(glyphB)
	intersections = []
	for c in flatA:
		l =len(c.points)
		for i in range(l):
			cur = c.points[i]
			next = c.points[(i+1)%l]
			sect = _intersect(flatB, (cur.x, cur.y), (next.x, next.y))
			if sect is None:
				continue
			intersections = intersections + sect
	return intersections

def makeTestGlyph():
	g = _RGlyph()
	pen = g.getPen()
	pen.moveTo((100, 100))
	pen.lineTo((800, 100))
	pen.curveTo((1000, 300), (1000, 600), (800, 800))
	pen.lineTo((100, 800))
	pen.lineTo((100, 100))
	pen.closePath()
	return g

if __name__ == "__main__":
	g = makeTestGlyph()
	print intersect(g, (-10, 200), (650, 150))
	print intersect(g, (100, 100), (600, 600))
