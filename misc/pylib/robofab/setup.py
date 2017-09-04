from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
	Extension("objects.objectsBase", ["objects/objectsBase.pyx"]),
	Extension("objects.objectsRF", ["objects/objectsRF.pyx"]),
	Extension("pens.rfUFOPen", ["pens/rfUFOPen.pyx"]),
	Extension("pens.boundsPen", ["pens/boundsPen.pyx"]),
	Extension("xmlTreeBuilder", ["xmlTreeBuilder.pyx"]),
	Extension("misc.arrayTools", ["misc/arrayTools.pyx"]),
	Extension("glifLib", ["glifLib.pyx"]),
]

setup(
  name = 'robofab',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
