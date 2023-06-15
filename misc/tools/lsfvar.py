import sys, os, os.path, re, argparse, pprint, shutil
import yaml
try:
  from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
  from yaml import Loader as YamlLoader, Dumper as YamlDumper
from collections import OrderedDict
from multiprocessing import Pool
from fontTools.ttLib import TTFont


def read_fvar_table(filename: str) -> {str:dict}:
  font = TTFont(filename, recalcBBoxes=False, recalcTimestamp=False)
  nametab = font["name"]

  names = {}
  for rec in nametab.names:
    names[rec.nameID] = rec.toUnicode()

  fvartab = font["fvar"]
  axes = []
  for a in fvartab.axes:
    # axisTag
    # axisNameID
    # flags
    # minValue
    # defaultValue
    # maxValue
    d = a.__dict__
    for k in list(d.keys()):
      # replace name-table IDs with their values
      if k.endswith('NameID'):
        d[k[:-2]] = names[d[k]]
        del d[k]
    axes.append(d)

  instances = []
  for inst in fvartab.instances:
    d = inst.__dict__
    for k in list(d.keys()):
      # replace name-table IDs with their values
      if k.endswith('NameID'):
        d[k[:-2]] = names[d[k]]
        del d[k]
    instances.append(d)

  return OrderedDict(axes=axes, instances=instances)


def fmtstructured(tables: [dict], files: [str], cl: dict) -> str:
  doc = {}
  for i, tab in enumerate(tables):
    file = files[i]
    doc[file] = dict(tab)
  cols = shutil.get_terminal_size((80, 20)).columns
  if cl.format == 'yaml':
    return yaml.dump(doc, Dumper=YamlDumper, width=cols)
  return pprint.PrettyPrinter(indent=2, width=cols).pformat(doc)


def fmtplaintext(out: [str], header: [str], rows: [[str]]) -> str:
  # calculate width needed for columns
  colw = [0] * len(header)
  for i, s in enumerate(header):
    colw[i] = max(colw[i], len(s))
  for row in rows:
    for i, s in enumerate(row):
      colw[i] = max(colw[i], len(s))

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
    xs = [div_prefix + (divchar * (colw[i] - len(div_prefix))) for i in range(len(row))]
    out.append(divglue.join(xs))
    out.append(row_suffix)

  format_row(header)
  format_divider()
  for row in rows:
    format_row(row)


def build_axes(tables: [dict], files: [str]) -> ([str], [[str]]):
  uniqueAxes1 = OrderedDict()
  for i, tab in enumerate(tables):
    file = files[i]
    for a in tab["axes"]:
      vals = OrderedDict(sorted(a.items())).values()
      key = ' '.join([str(v) for v in vals])
      d = uniqueAxes1.get(key, {})
      filev = d.get('files', [])
      d.update(a)
      filev.append(file)
      d['files'] = filev
      uniqueAxes1[key] = d

  uniqueAxes = dict()  # {tag:[{axis, ...}]}
  for a in uniqueAxes1.values():
    v = uniqueAxes.get(a['axisTag'], [])
    v.append(a)
    uniqueAxes[a['axisTag']] = v

  header = ['tag', 'name', 'flags', 'min', 'default', 'max', 'files']
  rows = []
  for axesForTag in uniqueAxes.values():
    for a in axesForTag:
      rows.append([
        a["axisTag"],
        a["axisName"],
        str(a["flags"]),
        str(a["minValue"]),
        str(a["defaultValue"]),
        str(a["maxValue"]),
        ', '.join(a["files"]),
      ])

  return header, rows


def build_instances(tables: [dict], files: [str]) -> ([str], [[str]]):
  axisTags = []
  for axis in tables[0]["axes"]:
    axisTags.append(axis["axisTag"])
  header = axisTags + ['flags', 'postscriptName', 'subfamilyName', 'file']
  rows = []
  for i, tab in enumerate(tables):
    file = files[i]
    axes = tab['axes']
    for inst in tab['instances']:
      row = []
      for axisTag in axisTags:
        row.append(str(inst['coordinates'][axisTag]))
      row.append(str(inst['flags']))
      row.append(inst['postscriptName'])
      row.append(inst['subfamilyName'])
      row.append(file)
      rows.append(row)

  return header, rows


def format_fvar(tables: [dict], files: [str], cl: dict) -> str:
  if cl.format in ('yaml', 'py'):
    return fmtstructured(tables, files, cl)

  out = []

  # axes
  header, rows = build_axes(tables, files)
  fmtplaintext(out, header, rows)
  out.append('\n')

  # instances
  header, rows = build_instances(tables, files)
  fmtplaintext(out, header, rows)

  return ''.join(out)


if __name__ == '__main__':
  argparser = argparse.ArgumentParser(description='Print fvar table entries')
  a = lambda *args, **kwargs: argparser.add_argument(*args, **kwargs)
  a('-f', '--format', metavar='<format>', help='One of: plain, yaml, py, md')
  a('inputs', metavar='<file>', nargs='+', help='Input fonts (ttf or otf)')
  cl = argparser.parse_args()

  if cl.format not in (None, 'plain', 'yaml', 'py', 'md'):
    raise Exception(f'unknown format: "{cl.format}"')

  with Pool() as p:
    tables = p.map(read_fvar_table, cl.inputs)

  filenames = [os.path.basename(fn) for fn in cl.inputs]
  print(format_fvar(tables, filenames, cl))
