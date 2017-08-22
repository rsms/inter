#
# Removes local guides from all glyphs
#
if __name__ == "__main__":
  font = CurrentFont()
  print "Removing local guides from all glyphs of %r" % font
  if font is not None:
    for g in font:
      if 'com.typemytype.robofont.guides' in g.lib:
        del(g.lib['com.typemytype.robofont.guides'])
    font.update()
  else:
    print "No fonts open"

  print "Done"
