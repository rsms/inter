from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
  Extension("decomposeGlyph", ["decomposeGlyph.pyx"]),
  Extension("alignpoints", ["alignpoints.pyx"]),
  Extension("Build", ["Build.pyx"]),
  Extension("convertCurves", ["convertCurves.pyx"]),
  Extension("mitreGlyph", ["mitreGlyph.pyx"]),
  Extension("mix", ["mix.pyx"]),
  Extension("italics", ["italics.pyx"]),
]

setup(
  name = 'copy',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
