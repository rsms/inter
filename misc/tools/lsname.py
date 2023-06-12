import sys, os, os.path, re, argparse
from collections import OrderedDict
from multiprocessing import Pool
from fontTools.ttLib import TTFont


# NAME_LABELS maps name table ID to symbolic names.
# See https://learn.microsoft.com/en-us/typography/opentype/spec/name#name-ids
NAME_LABELS = {
  # TrueType & OpenType
   0: 'Copyright',
   1: 'Font Family',
   2: 'Font Subfamily',
   3: 'Unique identifier',
   4: 'Full font name',
   5: 'Version',
   6: 'PostScript name',
   7: 'Trademark',
   8: 'Manufacturer',
   9: 'Designer',
  10: 'Description',
  11: 'Vendor URL',
  12: 'Designer URL',
  13: 'License Description',
  14: 'License URL',
  # 15 RESERVED
  16: 'Typo Family',
  17: 'Typo Subfamily',
  18: 'Mac Compatible Full Name',
  19: 'Sample text',

  # OpenType
  20: 'PostScript CID',
  21: 'WWS Family',
  22: 'WWS Subfamily',
  23: 'Light Background Palette',
  24: 'Dark Background Palette',
  25: 'Variations PostScript Name Prefix',

  # 26-255: Reserved for future expansion
  # 256-32767: Font-specific names (layout features and settings, variations, track names, etc.)
}


class AnySet:
  def __contains__(self, k):
    return True


def read_name_table(filename: str) -> {int:str}:
  font = TTFont(filename, recalcBBoxes=False, recalcTimestamp=False)
  nametab = font["name"]
  names = {}
  for rec in nametab.names:
    names[rec.nameID] = rec.toUnicode()
  return OrderedDict(sorted(names.items()))


def build_table(name_tables: [{int:str}], filenames: [str], name_ids_filter: set[str]):
  columns = {}
  for names in name_tables:
    for name_id, value in names.items():
      if name_id not in name_ids_filter:
        continue
      label = None
      if name_id in NAME_LABELS:
        label = f'{name_id} {NAME_LABELS[name_id]}'
      else:
        label = f'{name_id}'
      columns[name_id] = label

  columns = OrderedDict([(-1, "Filename")] + sorted(columns.items()))

  nameid_to_colidx = {}
  i = 0
  for id in columns:
    nameid_to_colidx[id] = i
    i += 1

  rows = [ list(columns.values()) ]

  for i in range(len(name_tables)):
    names = name_tables[i]
    row = [''] * len(rows[0])
    row[0] = filenames[i]
    for name_id, value in names.items():
      if name_id not in name_ids_filter:
        continue
      row[nameid_to_colidx[name_id]] = value
    rows.append(row)

  return rows


def format_table_one(header: [(int,str)], rows: [[str]], colw: [int]) -> str:
  ncols = len(header)
  out = []
  row = rows[0]

  w = 0
  for id, label in header:
    w = max(w, len(label))

  for i in range(ncols):
    id, label = header[i]
    if id < 0:
      out.append('%-*s     = %s' % (w, label, row[i]))
    else:
      out.append('%-*s %3d = %s' % (w, label, id, row[i]))

  return '\n'.join(out)


def format_table_plain(header: [(int,str)], rows: [[str]], colw: [int], no_labels: bool) -> str:
  ncols = len(header)
  out = []

  # print header labels
  if not no_labels:
    for i in range(ncols):
      if i > 0:
        out.append(' │ ')
      out.append('%-*s' % (colw[i], header[i][1]))
    out.append('\n')
  for i in range(ncols):
    id = header[i][0]
    if i > 0:
      out.append(' │ ')
    if isinstance(id, str):
      out.append('%-*s' % (colw[i], id))
    elif id < 0:
      out.append('%-*s' % (colw[i], 'name ID →'))
    else:
      out.append('%-*d' % (colw[i], id))
  out.append('\n')

  # print header divider
  for i in range(ncols):
    if i > 0:
      out.append('─┼─')
    out.append('─' * colw[i])
  out.append('\n')

  # print data rows
  for row in rows:
    for i in range(ncols):
      if i > 0:
        out.append(' │ ')
      out.append('%-*s' % (colw[i], row[i]))
    out.append('\n')

  out.pop()
  return ''.join(out)


def format_table_md(header: [str], rows: [[str]], colw: [int]) -> str:
  ncols = len(header)
  out = []

  # print header labels
  out.append('|')
  for i in range(ncols):
    out.append(' %-*s |' % (colw[i], header[i]))
  out.append('\n')

  # print header divider
  out.append('|')
  for i in range(ncols):
    out.append(' :' + ('-' * max(0, colw[i] - 1)) + ' |')
  out.append('\n')

  # print data rows
  for row in rows:
    out.append('|')
    for i in range(ncols):
      out.append(' %-*s |' % (colw[i], row[i]))
    out.append('\n')

  out.pop()
  return ''.join(out)


def csv_quote(s: str) -> str:
  return s.replace(",", "\\,")


def format_table_csv(header: [str], rows: [[str]]) -> str:
  ncols = len(header)
  out = []

  # print header
  for i in range(ncols):
    out.append(csv_quote(header[i]))
    out.append(',')
  out[len(out) - 1] = '\n'

  # print data
  for row in rows:
    for i in range(ncols):
      out.append(csv_quote(row[i]))
      out.append(',')
    out[len(out) - 1] = '\n'

  out.pop()
  return ''.join(out)


def format_table(rows: [[str]], format: str, no_labels: bool) -> str:
  # calculate column widths and column header labels
  ncols = len(rows[0])
  header = [None] * ncols
  colw = [0] * ncols
  i = 0
  unified_header = format == 'md' or format == 'csv'

  row = rows[0]
  if no_labels:
    while i < ncols:
      id_label = row[i].split(' ', 1)
      if len(id_label) == 1:
        id_label = [id_label[0], '']
      colw[i] = max(colw[i], len(id_label[0]))
      if unified_header:
        header[i] = id_label[0]
      else:
        header[i] = (id_label[0], id_label[0])
      i += 1
  elif unified_header:
    while i < ncols:
      colw[i] = max(colw[i], len(row[i]))
      header[i] = row[i]
      i += 1
  else:
    while i < ncols:
      id_label = row[i].split(' ', 1)
      if len(id_label) == 1:
        id_label = [-1, id_label[0]]
      colw[i] = max(colw[i], len(id_label[1]))
      header[i] = ( int(id_label[0]), id_label[1] )
      i += 1

  rows = rows[1:]

  for row in rows:
    i = 0
    while i < ncols:
      colw[i] = max(colw[i], len(row[i]))
      i += 1

  if format == 'csv':
    return format_table_csv(header, rows)
  elif format == 'md':
    return format_table_md(header, rows, colw)
  elif format == '' and len(rows) == 1:
    return format_table_one(header, rows, colw)
  elif format == 't' or format == '':
    return format_table_plain(header, rows, colw, no_labels)
  else:
    raise Exception(f'unknown format "{format}"')


if __name__ == '__main__':
  argparser = argparse.ArgumentParser(description='Print name table entries')
  a = lambda *args, **kwargs: argparser.add_argument(*args, **kwargs)
  a('-i', '--id', metavar='<nameID>',
    help='Only print <nameID>. Separate multiple IDs with comma.')
  a('-a', '--all', action='store_true', help='Print all name entries')
  a('--no-labels', action='store_true', help="Don't use nice labels, just IDs")
  a('-t', action='store_true', help='Print as table even when a single font is given')
  a('--csv', action='store_true', help='CSV output format')
  a('--md', action='store_true', help='Markdown output format')
  a('inputs', metavar='<file>', nargs='+', help='Input fonts (ttf or otf)')
  cl = argparser.parse_args()

  name_ids_filter = set((1, 2, 4, 6, 16, 17, 18, 21, 22))
  if cl.id and len(cl.id) > 0:
    name_ids_filter = set()
    for id in cl.id.split(','):
      name_ids_filter.add(int(id.strip()))
  elif cl.all:
    name_ids_filter = AnySet()

  with Pool() as p:
    name_tables = p.map(read_name_table, cl.inputs)

  filenames = [os.path.basename(fn) for fn in cl.inputs]
  rows = build_table(name_tables, filenames, name_ids_filter)

  format = ''
  if cl.csv: format = 'csv'
  if cl.md:  format = 'md'
  if cl.t:   format = 't'

  print(format_table(rows, format, no_labels=cl.no_labels))
