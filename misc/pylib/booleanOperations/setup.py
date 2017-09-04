from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
  Extension("booleanGlyph", ["booleanGlyph.pyx"]),
  Extension("booleanOperationManager", ["booleanOperationManager.pyx"]),
  Extension("flatten", ["flatten.pyx"]),
]

setup(
  name = 'booleanOperations',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
