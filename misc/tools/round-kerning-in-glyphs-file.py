#!/usr/bin/env python
# encoding: utf8
__doc__ = """
Rounds all kerning values in a Glyphs file to integers
"""
import os, sys, re

pat = re.compile(r'(.*=\s*)(\-?\d[\d\.]*);\n')
file = sys.argv[1]
outlines = []
count = 0

with open(file, "r") as f:
  print(f)
  level = 0
  done = False
  for lineno, line in enumerate(f):
    if not done:
      if level == 0:
        if line == "kerning = {\n":
          print("BEGIN at line", lineno)
          level = 1
      else:
        if line.find("{") != -1:
          level += 1
        if line.find("}") != -1:
          level -= 1
        m = pat.match(line)
        if m is not None:
          val = m.group(2)
          val2 = str(int(float(val)))
          line = m.group(1) + val2 + ";\n"
          if val != val2:
            count += 1
        if level == 0:
          print("END at line", lineno)
          done = True
    outlines.append(line)

if count == 0:
  print("all kerning values in %s are integers (no change)" % file)
else:
  print("rounded %r kerning values in %s" % (count, file))
  with open(file, "w") as f:
    f.write("".join(outlines))
