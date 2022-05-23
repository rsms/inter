#!/usr/bin/env python
import sys, os
from os.path import dirname, basename, abspath, relpath, join as pjoin
from fontTools.designspaceLib import DesignSpaceDocument


def subset_designspace(designspace, filename):
  italic = filename.find('italic') != -1

  for a in designspace.axes:
    if a.tag == "slnt" or a.tag == "ital":
      designspace.axes.remove(a)
      break

  rmlist = []
  hasDefault = not italic
  for source in designspace.sources:
    isitalic = source.name.find('Italic') != -1
    if italic != isitalic:
      rmlist.append(source)
    elif italic and not hasDefault:
      source.copyLib = True
      source.copyInfo = True
      source.copyGroups = True
      source.copyFeatures = True
      hasDefault = True
  for source in rmlist:
    designspace.sources.remove(source)

  rmlist = []
  for instance in designspace.instances:
    isitalic = instance.name.find('Italic') != -1
    if italic != isitalic:
      rmlist.append(instance)
  for instance in rmlist:
    designspace.instances.remove(instance)

  print("write %s" % relpath(filename, os.getcwd()))
  designspace.write(filename)


def main(argv):
  src_designspace_file = argv[1]
  dst_designspace_file = argv[2]
  designspace = DesignSpaceDocument.fromfile(src_designspace_file)
  designspace.lib.clear()
  subset_designspace(designspace, dst_designspace_file)


if __name__ == '__main__':
  main(sys.argv)
