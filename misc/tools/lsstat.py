import sys, os, os.path, re, argparse, pprint, shutil
import yaml
try:
  from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
  from yaml import Loader as YamlLoader, Dumper as YamlDumper
from collections import OrderedDict
from multiprocessing import Pool
from fontTools.ttLib import TTFont


TODO_PRINTS = dict()


def getName(nametab: object, nameID: int) -> str:
  return nametab.getName(nameID, 3, 1).toUnicode()


def read_stat_table(filename: str) -> {str:dict}:
  font = TTFont(filename, recalcBBoxes=False, recalcTimestamp=False)
  nametab = font["name"]
  stattab = font["STAT"].table.__dict__

  designAxisRecord = stattab['DesignAxisRecord'].Axis
  axisValueArray = stattab['AxisValueArray'].AxisValue

  axes = OrderedDict()
  axesArray = []

  for r in designAxisRecord:
    tag = str(r.AxisTag)
    axis = dict(
      tag    = tag,
      name   = getName(nametab, r.AxisNameID),
      values = [],
    )
    axesArray.append(axis)
    axes[tag] = axis

  for r in axisValueArray:
    axis = axesArray[r.AxisIndex]
    format = r.Format
    value = dict(
      axisIndex = r.AxisIndex,
      format = format,
      flags = r.Flags,
      name = getName(nametab, r.ValueNameID),
    )
    if format == 1:
      value['value'] = r.Value
    elif format == 2:
      value['value'] = r.NominalValue
      value['rangeMaxValue'] = r.RangeMaxValue
      value['rangeMinValue'] = r.RangeMinValue
    elif format == 3:
      value['value'] = r.Value
      value['linkedValue'] = r.LinkedValue
    elif format == 4:
      if not TODO_PRINTS.get('format4'):
        TODO_PRINTS['format4'] = True
        print('TODO: implement support for format 4 STAT records', file=sys.stderr)
    axis['values'].append(value)

  version = stattab['Version']  # e.g. 0x00010002 for 1.2

  return dict(
    version = '%d.%d' % (version >> 16, version & 0xffff),
    axes = axes,
    elidedFallbackName = getName(nametab, stattab['ElidedFallbackNameID']),
  )


def fmtstructured(tables: [dict], files: [str], cl: dict) -> str:
  doc = {}
  for i, tab in enumerate(tables):
    file = files[i]
    doc[file] = dict(tab)
  cols = shutil.get_terminal_size((80, 20)).columns
  if cl.format == 'yaml':
    return yaml.dump(doc, Dumper=YamlDumper, width=cols)
  return pprint.PrettyPrinter(indent=2, width=cols).pformat(doc)


def fmtplaintext(out: [str], header: [str], rows: [[str]], cl: dict) -> str:
  # calculate width needed for columns
  colw = [0] * len(header)
  for i, s in enumerate(header):
    colw[i] = max(colw[i], len(s))
  colw2 = [0] * len(header)
  for row in rows:
    for i, s in enumerate(row):
      colw[i] = max(colw[i], len(s))
      colw2[i] = max(colw2[i], len(s))

  # elide empty columns
  if 0 in colw2:
    emptyColsIndices = set([i for i, w in enumerate(colw2) if w == 0])
    header = [s for i, s in enumerate(header) if colw2[i] > 0]
    rows2 = []
    for row in rows:
      row2 = []
      for i, val in enumerate(row):
        if i not in emptyColsIndices:
          row2.append(val)
      rows2.append(row2)
    rows = rows2
    colw = [w for i, w in enumerate(colw) if colw2[i] > 0]

  colglue, divglue, divchar = ' │ ', '─┼─', '─'
  row_prefix, row_suffix, div_prefix = '', '\n', ''
  if cl.format == 'md':
    colglue, divglue, divchar = ' | ', ' | ', '-'
    row_prefix, row_suffix, div_prefix = '| ', ' |\n', ':'

  def format_row(row):
    out.append(row_prefix)
    out.append(colglue.join(['%-*s' % (colw[i], s) for i, s in enumerate(row)]))
    out.append(row_suffix)

  def format_divider():
    out.append(row_prefix)
    xs = [div_prefix + (divchar * (colw[i] - len(div_prefix))) for i in range(len(colw))]
    out.append(divglue.join(xs))
    out.append(row_suffix)

  format_row(header)
  format_divider()
  for row in rows:
    format_row(row)


def format_stat(tables: [dict], files: [str], cl: dict) -> str:
  if cl.format in ('yaml', 'py'):
    return fmtstructured(tables, files, cl)

  out = []

  uniqueAxes = OrderedDict()
  for tab in tables:
    for a in tab["axes"].values():
      uniqueAxes[a['tag']] = a['name']

  rubric_prefix, rubric_suffix = '', '\n'
  if cl.format == 'md':
    rubric_prefix, rubric_suffix = '### ', '\n\n'

  header = ['name', 'value', 'minval', 'maxval', 'linkval', 'format', 'flags', 'file']
  for axisTag, axisName in uniqueAxes.items():
    out.append(f"{rubric_prefix}{axisTag} ({axisName}){rubric_suffix}")
    rows = []
    for i, tab in enumerate(tables):
      file = files[i]
      axis = tab["axes"].get(axisTag)
      if not axis:
        continue
      for v in axis['values']:
        row = [
          v['name'],
          str(v['value']),
          str(v.get('rangeMinValue', '')),
          str(v.get('rangeMaxValue', '')),
          str(v.get('linkedValue', '')),
          str(v['format']),
          str(v['flags']),
          file,
        ]
        rows.append(row)

    fmtplaintext(out, header, rows, cl)
    out.append('\n')

  if len(uniqueAxes) > 0:
    out.pop()  # undo last \n

  return ''.join(out)


if __name__ == '__main__':
  argparser = argparse.ArgumentParser(description='Print STAT table entries')
  a = lambda *args, **kwargs: argparser.add_argument(*args, **kwargs)
  a('-f', '--format', metavar='<format>', help='One of: plain, yaml, py, md')
  a('inputs', metavar='<file>', nargs='+', help='Input fonts (ttf or otf)')
  cl = argparser.parse_args()

  if cl.format not in (None, 'plain', 'yaml', 'py', 'md'):
    raise Exception(f'unknown format: "{cl.format}"')

  with Pool() as p:
    tables = p.map(read_stat_table, cl.inputs)

  # print(pprint.PrettyPrinter(indent=2).pformat(tables[0]))

  filenames = [os.path.basename(fn) for fn in cl.inputs]
  print(format_stat(tables, filenames, cl))
