def test():
	"""
		# some tests for the ps Hints operations
		>>> from robofab.world import RFont, RGlyph
		>>> g = RGlyph()
		>>> g.psHints.isEmpty()
		True

		>>> h = RGlyph()
		>>> i = g + h
		>>> i.psHints.isEmpty()
		True
		
		>>> i = g - h
		>>> i.psHints.isEmpty()
		True
		
		>>> i = g * 2
		>>> i.psHints.isEmpty()
		True
		
		>>> i = g / 2
		>>> i.psHints.isEmpty()
		True
		
		>>> g.psHints.vHints = [(100, 50), (200, 50)]
		>>> g.psHints.hHints = [(100, 50), (200, 5)]

		>>> not g.psHints.isEmpty()
		True
		
		>>> gc = g.copy()
		>>> gc.psHints.asDict() == g.psHints.asDict()
		True
		
		# multiplication
		>>> v = g.psHints * 2
		>>> v.asDict() == {'vHints': [[200, 100], [400, 100]], 'hHints': [[200, 100], [400, 10]]}
		True

		# division
		>>> v = g.psHints / 2
		>>> v.asDict() == {'vHints': [[50.0, 25.0], [100.0, 25.0]], 'hHints': [[50.0, 25.0], [100.0, 2.5]]}
		True

		# multiplication with x, y, factor
		# vertically oriented values should respond different
		>>> v = g.psHints * (.5, 10)
		>>> v.asDict() == {'vHints': [[1000, 500], [2000, 500]], 'hHints': [[50.0, 25.0], [100.0, 2.5]]}
		True

		# division with x, y, factor
		# vertically oriented values should respond different
		>>> v = g.psHints / (.5, 10)
		>>> v.asDict() == {'vHints': [[10.0, 5.0], [20.0, 5.0]], 'hHints': [[200.0, 100.0], [400.0, 10.0]]}
		True

		# rounding to integer
		>>> v = g.psHints / 2
		>>> v.round()
		>>> v.asDict() == {'vHints': [(50, 25), (100, 25)], 'hHints': [(50, 25), (100, 3)]}
		True

		# "ps hint values calculating with a glyph"
		# ps hint values as part of glyphmath operations.
		# multiplication
		>>> h = g * 10
		>>> h.psHints.asDict() == {'vHints': [[1000, 500], [2000, 500]], 'hHints': [[1000, 500], [2000, 50]]}
		True

		# division
		>>> h = g / 2
		>>> h.psHints.asDict() == {'vHints': [[50.0, 25.0], [100.0, 25.0]], 'hHints': [[50.0, 25.0], [100.0, 2.5]]}
		True

		# x, y factor multiplication
		>>> h = g * (.5, 10)
		>>> h.psHints.asDict() == {'vHints': [[1000, 500], [2000, 500]], 'hHints': [[50.0, 25.0], [100.0, 2.5]]}
		True

		# x, y factor division
		>>> h = g / (.5, 10)
		>>> h.psHints.asDict() == {'vHints': [[10.0, 5.0], [20.0, 5.0]], 'hHints': [[200.0, 100.0], [400.0, 10.0]]}
		True

		# "font ps hint values"
		>>> f = RFont()
		>>> f.psHints.isEmpty()
		True

		>>> f.psHints.blueScale = .5
		>>> f.psHints.blueShift = 1
		>>> f.psHints.blueFuzz = 1
		>>> f.psHints.forceBold = True
		>>> f.psHints.hStems = (100, 90)
		>>> f.psHints.vStems = (500, 10)

		>>> not f.psHints.isEmpty()
		True

		>>> f.insertGlyph(g, name="new")
		<RGlyph for None.new>
		>>> f["new"].psHints.asDict() == g.psHints.asDict()
		True
	"""

if __name__ == "__main__":
	import doctest
	doctest.testmod()

