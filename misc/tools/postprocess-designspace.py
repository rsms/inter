import sys, os, os.path, re
import defcon
from multiprocessing import Pool
from fontTools.designspaceLib import DesignSpaceDocument
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tools')))
from common import getGitHash, getVersion
from postprocess_instance_ufo import ufo_set_wws


def update_version(ufo):
  version = getVersion()
  buildtag, buildtagErrs = getGitHash()
  now = datetime.utcnow()
  if buildtag == "" or len(buildtagErrs) > 0:
    buildtag = "src"
    print("warning: getGitHash() failed: %r" % buildtagErrs, file=sys.stderr)
  versionMajor, versionMinor = [int(num) for num in version.split(".")]
  ufo.info.versionMajor = versionMajor
  ufo.info.versionMinor = versionMinor
  ufo.info.year = now.year
  ufo.info.openTypeNameVersion = "Version %d.%03d;git-%s" % (versionMajor, versionMinor, buildtag)
  psFamily = re.sub(r'\s', '', ufo.info.familyName)
  psStyle = re.sub(r'\s', '', ufo.info.styleName)
  ufo.info.openTypeNameUniqueID = "%s-%s:%d:%s" % (psFamily, psStyle, now.year, buildtag)
  ufo.info.openTypeHeadCreated = now.strftime("%Y/%m/%d %H:%M:%S")


def fix_opsz_range(designspace):
  # TODO: find extremes by looking at the source
  for a in designspace.axes:
    if a.tag == "opsz":
      a.minimum = 14
      a.maximum = 32
      break
  return designspace


def fix_wght_range(designspace):
  for a in designspace.axes:
    if a.tag == "wght":
      a.minimum = 100
      a.maximum = 900
      break
  return designspace


def should_decompose_glyph(g):
  if g.components and len(g.components) > 0:
    for c in g.components:
      # Does the component have non-trivial transformation? (i.e. scaled or skewed)
      # Example of no transformation: (identity matrix)
      #   (1, 0, 0, 1, 0, 0)    no scale or offset
      # Example of simple offset transformation matrix:
      #   (1, 0, 0, 1, 20, 30)  20 x offset, 30 y offset
      # Example of scaled transformation matrix:
      #   (-1.0, 0, 0.3311, 1, 1464.0, 0)  flipped x axis, sheered and offset
      # Matrix order:
      #   (x_scale, x_skew, y_skew, y_scale, x_pos, y_pos)

      # if g.name == 'dotmacron.lc':
      #   print(f"{g.name} cn {c.baseGlyph}", c.transformation)
      # Check if transformation is not identity (ignoring x & y offset)
      m = c.transformation
      if m[0] + m[1] + m[2] + m[3] != 2.0:
        return True
  return False


def find_glyphs_to_decompose(designspace_source):
  glyph_names = set()
  # print("find_glyphs_to_decompose inspecting %r" % designspace_source.name)
  ufo = defcon.Font(designspace_source.path)
  for g in ufo:
    if should_decompose_glyph(g):
      glyph_names.add(g.name)
  return list(glyph_names)


def set_ufo_filter(ufo, **filter_dict):
  filters = ufo.lib.setdefault("com.github.googlei18n.ufo2ft.filters", [])
  for i in range(len(filters)):
    if filters[i].get("name") == filter_dict["name"]:
      filters[i] = filter_dict
      return
  filters.append(filter_dict)


def update_source_ufo(ufo_file, glyphs_to_decompose):
  print(f"update {os.path.basename(ufo_file)}")
  ufo = defcon.Font(ufo_file)
  update_version(ufo)
  set_ufo_filter(ufo, name="decomposeComponents", include=glyphs_to_decompose)
  ufo_set_wws(ufo) # Fix missing WWS entries for Display fonts
  ufo.save(ufo_file)


def update_sources(designspace):
  with Pool() as p:
    sources = [source for source in designspace.sources]
    # sources = [s for s in sources if s.name == "Inter Thin"] # DEBUG
    glyphs_to_decompose = set()
    for glyph_names in p.map(find_glyphs_to_decompose, sources):
      glyphs_to_decompose.update(glyph_names)
    glyphs_to_decompose = list(glyphs_to_decompose)
    # print("glyphs marked to be decomposed: %s" % ', '.join(glyphs_to_decompose))
    source_files = list(set([s.path for s in sources]))
    p.starmap(update_source_ufo, [(path, glyphs_to_decompose) for path in source_files])
  return designspace


def main(argv):
  designspace_file = argv[1]
  designspace = DesignSpaceDocument.fromfile(designspace_file)
  designspace = fix_opsz_range(designspace)
  designspace = fix_wght_range(designspace)
  designspace = update_sources(designspace)
  designspace.write(designspace_file)


if __name__ == '__main__':
  main(sys.argv)
