import os
import glob
import unittest

import robofab.test

if __name__ == "__main__":
	testDir = os.path.dirname(robofab.test.__file__)
	testFiles = glob.glob1(testDir, "test_*.py")
	
	loader = unittest.TestLoader()
	suites = []
	for fileName in testFiles:
		modName = "robofab.test." + fileName[:-3]
		print "importing", fileName
		try:
			mod = __import__(modName, {}, {}, ["*"])
		except ImportError:
			print "*** skipped", fileName
			continue
	
		suites.append(loader.loadTestsFromModule(mod))
	
	print "running tests..."
	testRunner = unittest.TextTestRunner(verbosity=0)
	testSuite = unittest.TestSuite(suites)
	testRunner.run(testSuite)
