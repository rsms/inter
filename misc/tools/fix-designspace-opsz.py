#!/usr/bin/env python
import sys, os
from fontTools.designspaceLib import DesignSpaceDocument

designspace_file = sys.argv[1]
designspace = DesignSpaceDocument.fromfile(designspace_file)
for a in designspace.axes:
  if a.tag == "opsz":
    a.maximum = 72
    break
designspace.write(designspace_file)
