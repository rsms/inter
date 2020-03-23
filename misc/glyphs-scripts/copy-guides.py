#MenuTitle: Copy guides from Regular & Italic to other masters
# -*- coding: utf-8 -*-
import GlyphsApp
import copy

Glyphs.clearLog()
font = Glyphs.font

romanMasterName = "Regular"
italicMasterName = "Italic"

guidesRoman = None
guidesItalic = None

guideNames = [
  "cap center",  # 0
  "low center",  # 1
  "",
  "",
]

for master in font.masters:
  if master.name == "Regular":
    guidesRoman = master.guides
  if master.name == "Italic":
    guidesItalic = master.guides

# rename guides (order is horizontal top to bottom, then vertical)
for i in range(0, len(guidesRoman)):
  guidesRoman[i].name = guideNames[i]
  guidesItalic[i].name = guideNames[i]

if regularGuides is None:
  print("mainMasterName=%r master not found" % mainMasterName)
else:
  for master in font.masters:
    print(master.name)
    if master.name.find("Italic") != -1:
      if master.name != guidesItalic:
        master.guides = [copy.copy(u) for u in guidesItalic]
    else:
      if master.name != guidesRoman:
        master.guides = [copy.copy(u) for u in guidesRoman]
