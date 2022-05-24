import sys, os, os.path
import defcon
from multiprocessing import Pool
from fontTools.designspaceLib import DesignSpaceDocument

def fix_opsz_maximum(designspace):
  for a in designspace.axes:
    if a.tag == "opsz":
      # TODO: find maximum by looking at the source
      a.maximum = 72
      break
  return designspace

def should_decompose_glyph(g):
  # A trivial glyph is one that does not use components or where component transformation
  # does not include mirroring (i.e. "flipped").
  if g.components and len(g.components) > 0:
    for c in g.components:
      # has non-trivial transformation? (i.e. scaled)
      # Example of optimally trivial transformation:
      #   (1, 0, 0, 1, 0, 0)  no scale or offset
      # Example of scaled transformation matrix:
      #   (-1.0, 0, 0.3311, 1, 1464.0, 0)  flipped x axis, sheered and offset
      xScale = c.transformation[0]
      yScale = c.transformation[3]
      # If glyph is reflected along x or y axes, it won't slant well.
      if xScale < 0 or yScale < 0:
        return True
  return False

def find_glyphs_to_decompose(designspace):
  source = designspace.sources[int(len(designspace.sources)/2)]
  print("find_glyphs_to_decompose sourcing from %r" % source.name)
  ufo = defcon.Font(source.path)
  return sorted([g.name for g in ufo if should_decompose_glyph(g)])

def set_ufo_filter(ufo, **filter_dict):
  filters = ufo.lib.setdefault("com.github.googlei18n.ufo2ft.filters", [])
  for i in range(len(filters)):
    if filters[i].get("name") == filter_dict["name"]:
      filters[i] = filter_dict
      return
  filters.append(filter_dict)

def update_source_ufo(ufo_file, glyphs_to_decompose):
  print("update %s" % os.path.basename(ufo_file))
  ufo = defcon.Font(ufo_file)
  set_ufo_filter(ufo, name="decomposeComponents", include=glyphs_to_decompose)
  ufo.save(ufo_file)

def update_sources(designspace):
  glyphs_to_decompose = find_glyphs_to_decompose(designspace)
  #print("glyphs marked to be decomposed: %s" % ', '.join(glyphs_to_decompose))
  sources = [source for source in designspace.sources]
  # sources = [s for s in sources if s.name == "Inter Thin"] # DEBUG
  source_files = list(set([s.path for s in sources]))
  with Pool(len(source_files)) as p:
    p.starmap(update_source_ufo, [(file, glyphs_to_decompose) for file in source_files])
  return designspace

def main(argv):
  designspace_file = argv[1]
  designspace = DesignSpaceDocument.fromfile(designspace_file)
  designspace = fix_opsz_maximum(designspace)
  designspace = update_sources(designspace)
  designspace.write(designspace_file)

if __name__ == '__main__':
  main(sys.argv)
