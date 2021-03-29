#!/usr/bin/env python
# encoding: utf8
#
# This program is run by the Makefile target "docs_fonts" and generates
# subset font files and CSS for the web fonts.
#
from __future__ import print_function
import os, sys, subprocess, os.path
from os.path import dirname, basename, abspath, join as pjoin
from multiprocessing import Pool as ProcPool
from fontTools import ttLib
from itertools import groupby
from operator import itemgetter
sys.path.append(dirname(abspath(__file__)))
from common import BASEDIR, VENVDIR


# FORCE can be set to True to subset all fonts regardless if the input source
# font has changed or not
FORCE = False


# fonts to subset
FONTS = [

  # Text family
  { 'infile':  'build/fonts/var/Inter.var.ttf',
    'outfile': 'build/fonts/subset/Inter.{subset}.var.woff2',
    'css_family': 'Inter var experimental',
    'css_weight': '100 900',
    'css_style':  'oblique 0deg 10deg',
  },

  { 'infile':  'build/fonts/var/Inter-roman.var.ttf',
    'outfile': 'build/fonts/subset/Inter-roman.{subset}.var.woff2',
    'css_family': 'Inter var',
    'css_weight': '100 900',
    'css_style':  'normal',
    'css_extra':  "font-named-instance: 'Regular';",
  },

  { 'infile':  'build/fonts/var/Inter-italic.var.ttf',
    'outfile': 'build/fonts/subset/Inter-italic.{subset}.var.woff2',
    'css_family': 'Inter var',
    'css_weight': '100 900',
    'css_style':  'italic',
    'css_extra':  "font-named-instance: 'Italic';",
  },

  # Display family
  { 'infile':  'build/fonts/var/InterDisplay.var.ttf',
    'outfile': 'build/fonts/subset/InterDisplay.{subset}.var.woff2',
    'css_family': 'InterDisplay var experimental',
    'css_weight': '100 900',
    'css_style':  'oblique 0deg 10deg',
  },

  { 'infile':  'build/fonts/var/InterDisplay-roman.var.ttf',
    'outfile': 'build/fonts/subset/InterDisplay-roman.{subset}.var.woff2',
    'css_family': 'InterDisplay var',
    'css_weight': '100 900',
    'css_style':  'normal',
    'css_extra':  "font-named-instance: 'Regular';",
  },

  { 'infile':  'build/fonts/var/InterDisplay-italic.var.ttf',
    'outfile': 'build/fonts/subset/InterDisplay-italic.{subset}.var.woff2',
    'css_family': 'InterDisplay var',
    'css_weight': '100 900',
    'css_style':  'italic',
    'css_extra':  "font-named-instance: 'Italic';",
  },
]

# template for CSS
CSS_TEMPLATE = '''
/* {comment} */
@font-face {{
  font-family: '{family}';
  font-style: {style};
  font-weight: {weight};
  font-display: swap;
  src: url('font-files/{filename}?v={{{{font_v}}}}') format('woff2');
  unicode-range: {unicode_range};{extra}
}}
'''

# codepoints of "extra" glyphs that should end up in a separate extra set as "symbols"
# Listed here as codepoints rather than ranges to that copy-pasting from e.g. Glyphs app
# is easier.
SYMBOL_UNICODES = [
  0x2190, 0x27F5, 0x1F850, 0x21D0, 0x27F8, 0x2192, 0x27F6, 0x1F852, 0x21D2,
  0x27F9, 0x2196, 0x2197, 0x2198, 0x2199, 0x2194, 0x27F7, 0x21D4, 0x27FA, 0x2191,
  0x2193, 0x2195, 0x21A9, 0x21AA, 0x2713, 0x2717, 0x25BC, 0x25B2, 0x25C0, 0x25C4,
  0x25BA, 0x25B6, 0x25BD, 0x25B3, 0x25C1, 0x25C5, 0x25B7, 0x25BB, 0x26A0, 0x25CF,
  0x25CB, 0x25A0, 0x25A1, 0x25A2, 0x2B12, 0x2B13, 0x25C6, 0x2756, 0x25C7, 0xE000,
  0x263C, 0x2600, 0x2661, 0x2665, 0x2764, 0x2605, 0x2606, 0x2B06, 0x21E7, 0x21EA,
  0x2318, 0x2303, 0x2305, 0x2380, 0x2325, 0x2387, 0x238B, 0x21BA, 0x21BB, 0x232B,
  0x2326, 0x2327, 0x23CF, 0x23CE, 0x21B5, 0x21B3, 0x21B0, 0x21B1, 0x21B4, 0x21E4,
  0x21E5, 0x21DE, 0x21DF, 0x25EF, 0x2B1C, 0x20DD, 0x20DE, 0x24B6, 0x24B7, 0x24B8,
  0x24B9, 0x24BA, 0x24BB, 0x24BC, 0x24BD, 0x24BE, 0x24BF, 0x24C0, 0x24C1, 0x24C2,
  0x24C3, 0x24C4, 0x24C5, 0x24C6, 0x24C7, 0x24C8, 0x24C9, 0x24CA, 0x24CB, 0x24CC,
  0x24CD, 0x24CE, 0x24CF, 0x24EA, 0x2460, 0x2780, 0x2461, 0x2781, 0x2462, 0x2782,
  0x2463, 0x2783, 0x2464, 0x2784, 0x2465, 0x2785, 0x2466, 0x2786, 0x2467, 0x2787,
  0x2468, 0x2788, 0xE12B, 0xE12C, 0xE12D, 0xE12E, 0xE12F, 0xE130, 0xE131, 0xE132,
  0xE133, 0xE134, 0xE135, 0xE136, 0xE137, 0xE15F, 0xE160, 0xE161, 0xE162, 0xE138,
  0xE139, 0xE13A, 0xE13B, 0xE13C, 0xE13D, 0x1F130, 0x1F131, 0x1F132, 0x1F133,
  0x1F134, 0x1F135, 0x1F136, 0x1F137, 0x1F138, 0x1F139, 0x1F13A, 0x1F13B, 0x1F13C,
  0x1F13D, 0x1F13E, 0x1F13F, 0x1F140, 0x1F141, 0x1F142, 0x1F143, 0x1F144, 0x1F145,
  0x1F146, 0x1F147, 0x1F148, 0x1F149, 0xE13E, 0xE13F, 0xE140, 0xE141, 0xE142,
  0xE143, 0xE144, 0xE145, 0xE146, 0xE147, 0xE148, 0xE149, 0xE14A, 0xE14B, 0xE14C,
  0xE14D, 0xE14E, 0xE14F, 0xE150, 0xE151, 0xE152, 0xE153, 0xE154, 0xE155, 0xE156,
  0xE157, 0xE158, 0xE159, 0xE15A, 0xE15B, 0xE15C, 0xE15D, 0xE15E,
]


SELF_SCRIPT_MTIME = 0


def main(argv):
  # defines subsets.
  # Ranges are inclusive.
  # Order should be from most frequently used to least frequently used.
  subsets = (

  defsubset('latin',  # Latin & ASCII
    range(0x0000,0x00FF),
    0x0131,
    range(0x0152, 0x0153),
    range(0x02BB, 0x02BC),
    0x02C6,
    0x02DA,
    0x02DC,
    range(0x2000, 0x206F),
    0x2074,
    0x20AC,
    0x2122,
    0x2191,
    0x2193,
    0x2212,
    0x2215,
    0xFEFF,
    0xFFFD,
  ),

  defsubset('latin-ext',  # Latin extended A & B
    range(0x0100, 0x024F),
    0x0259,
    range(0x1E00, 0x1EFF),
    0x2020,
    range(0x20A0, 0x20AB),
    range(0x20AD, 0x20CF),
    0x2113,
    range(0x2C60, 0x2C7F),
    range(0xA720, 0xA7FF),
  ),

  defsubset('vietnamese',
    range(0x0102, 0x0103),
    range(0x0110, 0x0111),
    range(0x0128, 0x0129),
    range(0x0168, 0x0169),
    range(0x01A0, 0x01A1),
    range(0x01AF, 0x01B0),
    range(0x1EA0, 0x1EF9),
    0x20AB,
  ),

  defsubset('greek',
    range(0x0370, 0x03FF),
    range(0x1F00, 0x1FFF),  # extended
  ),

  defsubset('cyrillic',
    range(0x0400, 0x045F),
    range(0x0490, 0x0491),
    range(0x04B0, 0x04B1),
    0x2116,
    # extended:
    range(0x0460, 0x052F),
    range(0x1C80, 0x1C88),
    0x20B4,
    range(0x2DE0, 0x2DFF),
    range(0xA640, 0xA69F),
    range(0xFE2E, 0xFE2F),
  ),

  defsubset('symbols',
    *genCompactIntRanges(SYMBOL_UNICODES)
  ),

  # defsubset('alternates',
  #   # all private-use codepoints are mapped to alternate glyphs, normally accessed by
  #   # OpenType features.
  #   range(0xE000, 0xF8FF),
  # ),
  # Note: Disabled so that alternates are all added automatically to the "extra" set.

  )

  global SELF_SCRIPT_MTIME
  SELF_SCRIPT_MTIME = os.path.getmtime(__file__)

  # XXX DEBUG
  global FONTS
  FONTS = FONTS[1:2]

  # generate subset fonts
  with ProcPool() as procpool:
    for fontinfo in FONTS:
      subset_font(fontinfo, subsets, procpool)
    procpool.close()
    procpool.join()

  # generate CSS
  for fontinfo in FONTS:
    css = genCSS(fontinfo, subsets)
    infile, _ = os.path.splitext(basename(fontinfo['infile']))
    cssfile = pjoin(BASEDIR, 'docs/_includes', infile + '.css')
    # print('css:\n' + css) # DEBUG
    print('write', cssfile)
    with open(cssfile, 'w') as f:
      f.write(css)


def subset_font(fontinfo, subsets, procpool):
  infile          = pjoin(BASEDIR, fontinfo['infile'])
  outfileTemplate = pjoin(BASEDIR, fontinfo['outfile'])
  font            = ttLib.TTFont(infile)
  ucall           = set(getUnicodeMap(font)) # set of all codepoints mapped by the font
  covered         = set()  # set of codepoints covered by 'subsets'

  for subset in subsets:
    unicodes, unicodeRange = genUnicodeRange(subset['codepoints'])
    unicodes = unicodes - covered
    covered = covered.union(unicodes)
    outfile = outfileTemplate.format(subset=subset['name'])
    subset_range_async(procpool, infile, outfile, unicodeRange)

  # generate "extra" subset of remaining codepoints
  extraUnicodes = ucall - covered
  _, extraUnicodeRange = genUnicodeRange(extraUnicodes)
  outfile = outfileTemplate.format(subset='extra')
  subset_range_async(procpool, infile, outfile, unicodeRange)


def subset_range_async(procpool :ProcPool, infile :str, outfile :str, unicodeRange :str):
  if not FORCE:
    try:
      outmtime = os.path.getmtime(outfile)
      if outmtime > os.path.getmtime(infile) and outmtime > SELF_SCRIPT_MTIME:
        print('up-to-date %s -> %s' % (relpath(infile), relpath(outfile)))
        return
    except:
      pass
  procpool.apply_async( subset_range,(infile, outfile, unicodeRange),
                        error_callback=lambda err: onProcErr(procpool, err) )


def onProcErr(procpool, err):
  procpool.terminate()
  raise err
  sys.exit(1)


def subset_range(infile :str, outfile :str, unicodeRange :str):
  pyftsubset = pjoin(VENVDIR, 'bin/pyftsubset')

  args = [
    pyftsubset,
    '--unicodes=' + unicodeRange,
    '--layout-features=*',
    '--recommended-glyphs',
    '--no-recalc-bounds',
    '--no-prune-unicode-ranges',
    '--no-hinting',
    '--output-file=' + outfile,
    infile
  ]
  if outfile.endswith('.woff2'):
    args.append('--flavor=woff2')

  print("pyftsubset %s -> %s" % (relpath(infile), relpath(outfile)))
  # print('\n  '.join([repr(a) for a in args]))  # debug
  p = subprocess.run(
    args,
    shell=False,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    encoding='utf-8', # py3
  )
  if p.returncode != 0:
    raise Exception(
      'pyftsubset failed:\n-- stdout:\n%s\n\n-- stderr:\n%s\n\n-- invocation:\n%s' % (
      p.stdout.strip(),
      p.stderr.strip(),
      '\n  '.join([repr(a) for a in args]),
    ))
    # sys.exit(p.returncode)
  print("write", outfile)

# (name, ...[int|range(int)]) -> { name:str codepoints:[int|range(int)] }
def defsubset(name, *codepoints):
  return { 'name':name, 'codepoints':codepoints }


def genUnicodeRange(codepoints :list) -> (set, str):
  unicodes = set()
  unicodeRange = []
  for v in codepoints:
    if isinstance(v, int):
      unicodes.add(v)
      unicodeRange.append('U+%04X' % v)
    else:
      first = 0
      for v2 in v:
        first = v2
        break
      last = 0
      for v2 in v:
        unicodes.add(v2)
        last = v2
      last += 1 # since unicode ranges are inclusive (but python ranges aren't)
      unicodes.add(last)
      unicodeRange.append('U+%04X-%04X' % (first,last))
  return unicodes, ','.join(unicodeRange)


def getUnicodeMap(font :ttLib.TTFont) -> {int:str} :  # codepoint=>glyphname
  # https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html
  bestCodeSubTable = None
  bestCodeSubTableFormat = 0
  for st in font['cmap'].tables:
    if st.platformID == 0: # 0=unicode, 1=mac, 2=(reserved), 3=microsoft
      if st.format > bestCodeSubTableFormat:
        bestCodeSubTable = st
        bestCodeSubTableFormat = st.format
  return bestCodeSubTable.cmap


def genCompactCodepointRanges(codepoints :[int], groupAllThreshold :int) -> str:
  unicodeRange = []
  codepoints = sorted(codepoints)
  for k, g in groupby(enumerate(codepoints), lambda t: t[0]-t[1]):
    ilist = list(map(itemgetter(1), g))
    if len(ilist) > 1:
      # unicodeRange.append(range(ilist[0], ilist[-1]+1))
      unicodeRange.append('U+%04X-%04X' % (ilist[0], ilist[-1]))
    else:
      v = ilist[0]
      if v > groupAllThreshold:
        unicodeRange.append('U+%04X-%04X' % (v, max(codepoints)))
        break
      else:
        unicodeRange.append('U+%04X' % v)
  return ','.join(unicodeRange)


def genCompactIntRanges(codepoints :[int]) -> [[int]]:
  compact = []
  codepoints = sorted(codepoints)
  for k, g in groupby(enumerate(codepoints), lambda t: t[0]-t[1]):
    ilist = list(map(itemgetter(1), g))
    if len(ilist) > 1:
      compact.append(range(ilist[0], ilist[-1]+1))
    else:
      compact.append(ilist[0])
  return compact


def genCSS(fontinfo, subsets):
  outfileTemplate = pjoin(BASEDIR, fontinfo['outfile'])

  css_family = fontinfo.get('css_family', 'Inter')
  css_style  = fontinfo.get('css_style', 'normal')
  css_weight = fontinfo.get('css_weight', '400')
  css_extra  = fontinfo.get('css_extra', '')
  if len(css_extra) > 0:
    css_extra = '\n  ' + css_extra
  css = []

  for subset in list(subsets) + [{ 'name':'extra' }]:
    outfile = outfileTemplate.format(subset=subset['name'])
    # Read effective codepoint coverage. This may be greater than requested
    # in case of OT features. For example, the Latin subset includes some common arrow
    # glyphs since "->" is a ligature for "→".
    font = ttLib.TTFont(outfile)
    unicodes = set(getUnicodeMap(font))
    if min(unicodes) < 0x30:
      # the "base" (latin) subset. extend it to include control codepoints
      controlCodepoints, _ = genUnicodeRange([range(0x0000, 0x001F)])
      unicodes = unicodes.union(controlCodepoints)
    _, unicodeRange = genUnicodeRange(genCompactIntRanges(unicodes))
    css.append(CSS_TEMPLATE.format(
      comment=subset['name'],
      filename=basename(outfile),
      unicode_range=unicodeRange,
      family=css_family,
      style=css_style,
      weight=css_weight,
      extra=css_extra,
    ).strip())

  # From the CSS spec on unicode-range descriptor:
  #   "If the Unicode ranges overlap for a set of @font-face rules with the same family
  #    and style descriptor values, the rules are ordered in the reverse order they were
  #    defined; the last rule defined is the first to be checked for a given character."
  # https://www.w3.org/TR/css-fonts-4/#unicode-range-desc
  css.reverse()

  return '\n'.join(css)


def relpath(path):
  return os.path.relpath(path, os.getcwd())


if __name__ == '__main__':
  main(sys.argv)
