#!/usr/bin/env python3
#
# from gftools
# https://github.com/googlefonts/gftools/blob/
# 8b53f595a08d1b3f86f86eb97e07b15b1f52f671/bin/gftools-fix-vf-meta.py
#
"""
Add a STAT table to a weight only variable font.

This script can also add STAT tables to a variable font family which
consists of two fonts, one for Roman, the other for Italic.
Both of these fonts must also only contain a weight axis.

For variable fonts with multiple axes, write a python script which
uses fontTools.otlLib.builder.buildStatTable e.g
https://github.com/googlefonts/literata/blob/main/sources/gen_stat.py

The generated STAT tables use format 2 Axis Values. These are needed in
order for Indesign to work.

Special mention to Thomas Linard for reviewing the output of this script.


Usage:

Single family:
gftools fix-vf-meta FontFamily[wght].ttf

Roman + Italic family:
gftools fix-vf-meta FontFamily[wght].ttf FontFamily-Italic[wght].ttf
"""
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont
# from gftools.utils import font_is_italic
import argparse, re


whitespace_re = re.compile(r'\s+')


def remove_whitespace(s):
  return whitespace_re.sub("", s)


def font_is_italic(ttfont):
  if ttfont['head'].macStyle & 0b10:
    return True
  return False
  # # Check if the font has the word "Italic" in its stylename
  # stylename = ttfont["name"].getName(2, 3, 1, 0x409).toUnicode()
  # return True if "Italic" in stylename else False


def font_has_mac_names(ttfont):
  for record in ttfont['name'].names:
    if record.platformID == 1:
      return True
  return False


def build_stat(roman_font, italic_font=None):
  roman_wght_axis = dict(
    tag="wght",
    name="Weight",
    values=build_wght_axis_values(roman_font),
  )
  roman_opsz_axis = dict(
    tag="opsz",
    name="Optical size",
    values=build_opsz_axis_values(roman_font),
  )
  roman_axes = [roman_wght_axis, roman_opsz_axis]

  if italic_font:
    # We need to create a new Italic axis in the Roman font
    roman_axes.append(dict(
      tag="ital",
      name="Italic",
      values=[
        dict(
          name="Roman",
          flags=2,
          value=0.0,
          linkedValue=1.0,
        )
      ]
    ))
    italic_wght_axis = dict(
      tag="wght",
      name="Weight",
      values=build_wght_axis_values(italic_font),
    )
    italic_opsz_axis = dict(
      tag="opsz",
      name="Optical size",
      values=build_opsz_axis_values(italic_font),
    )
    italic_ital_axis = dict(
      tag="ital",
      name="Italic",
      values=[
        dict(
          name="Italic",
          value=1.0,
        )
      ]
    )
    italic_axes = [italic_wght_axis, italic_opsz_axis, italic_ital_axis]
    #print("buildStatTable(italic_font)", italic_axes)
    buildStatTable(italic_font, italic_axes)
  #print("buildStatTable(roman_font)", roman_axes)
  buildStatTable(roman_font, roman_axes)


def build_stat_v2(roman_font, italic_font=None):
  roman_wght_axis = dict(
    tag="wght",
    name="Weight",
  )
  roman_opsz_axis = dict(
    tag="opsz",
    name="Optical size",
  )
  roman_axes = [roman_wght_axis, roman_opsz_axis]
  locations = [
    dict(name='Regular', location=dict(wght=400, opsz=14)),
    dict(name='Regular Display', location=dict(wght=400, opsz=32)),
    dict(name='Bold', location=dict(wght=700, opsz=14)),
    dict(name='Bold Display', location=dict(wght=700, opsz=32)),
  ]
  buildStatTable(roman_font, roman_axes, locations)


def build_opsz_axis_values(ttfont):
  nametable = ttfont['name']
  instances = ttfont['fvar'].instances

  val_min = 0.0
  val_max = 0.0
  for instance in instances:
    opsz_val = instance.coordinates["opsz"]
    if val_min == 0.0 or opsz_val < val_min:
      val_min = opsz_val
    if val_max == 0.0 or opsz_val > val_max:
      val_max = opsz_val

  return [
    {
      "name": "Regular",
      "value": val_min,
      "linkedValue": val_max,
      "flags": 2,
    },
    {
      "name": "Display",
      "value": val_max,
    },
  ]

  # results = []
  # for instance in instances:
  #   opsz_val = instance.coordinates["opsz"]
  #   name = nametable.getName(instance.subfamilyNameID, 3, 1, 1033).toUnicode()
  #   name = name.replace("Italic", "").strip()
  #   if name == "":
  #     name = "Regular"
  #   inst = {
  #     "name": name,
  #     "value": opsz_val,
  #   }
  #   if int(opsz_val) == val_min:
  #     inst["flags"] = 0
  #     inst["linkedValue"] = val_max
  #   else:
  #     inst["linkedValue"] = val_min
  #   results.append(inst)

  # return results


def build_wght_axis_values(ttfont):
  results = []
  nametable = ttfont['name']
  instances = ttfont['fvar'].instances
  has_bold = any([True for i in instances if i.coordinates['wght'] == 700])
  for instance in instances:
    wght_val = instance.coordinates["wght"]
    name = nametable.getName(instance.subfamilyNameID, 3, 1, 1033).toUnicode()
    #print(nametable.getName(instance.postscriptNameID, 3, 1, 1033).toUnicode())
    name = name.replace("Italic", "").strip()
    if name == "":
      name = "Regular"
    inst = {
      "name": name,
      "nominalValue": wght_val,
    }
    if inst["nominalValue"] == 400:
      inst["flags"] = 0x2
    results.append(inst)

  # Dynamically generate rangeMinValues and rangeMaxValues
  entries = [results[0]["nominalValue"]] + \
        [i["nominalValue"] for i in results] + \
        [results[-1]["nominalValue"]]
  for i, entry in enumerate(results):
    entry["rangeMinValue"] = (entries[i] + entries[i+1]) / 2
    entry["rangeMaxValue"] = (entries[i+1] + entries[i+2]) / 2

  # Format 2 doesn't support linkedValues so we have to append another
  # Axis Value (format 3) for Reg which does support linkedValues
  if has_bold:
    inst = {
      "name": "Regular",
      "value": 400,
      "flags": 0x2,
      "linkedValue": 700
    }
    results.append(inst)
  return results


def update_nametable(ttfont):
  """
  - Add nameID 25
  - Update fvar instance names and add fvar instance postscript names
  """
  is_italic = font_is_italic(ttfont)
  has_mac_names = font_has_mac_names(ttfont)

  # Add nameID 25
  # https://docs.microsoft.com/en-us/typography/opentype/spec/name#name-ids
  vf_ps_name = _add_nameid_25(ttfont, is_italic, has_mac_names)

  nametable = ttfont['name']
  instances = ttfont["fvar"].instances

  print("%d instances of %s:" % (len(instances), "Italic" if is_italic else "Roman"))

  # find opsz max
  opsz_val_max = 0.0
  for instance in instances:
    opsz_val = instance.coordinates["opsz"]
    if opsz_val_max == 0.0 or opsz_val > opsz_val_max:
      opsz_val_max = opsz_val

  # Update fvar instances
  i = 0
  for inst in instances:
    inst_name = nametable.getName(inst.subfamilyNameID, 3, 1, 1033).toUnicode()
    print("instance %2d" % i, inst_name)
    i += 1

    # Update instance subfamilyNameID
    if is_italic:
      inst_name = inst_name.strip()
      inst_name = inst_name.replace("Regular Italic", "Italic")
      inst_name = inst_name.replace("Italic", "").strip()
      inst_name = inst_name + " Italic"
      ttfont['name'].setName(inst_name, inst.subfamilyNameID, 3, 1, 0x409)
    if has_mac_names:
      ttfont['name'].setName(inst_name, inst.subfamilyNameID, 1, 0, 0)

    # Add instance psName
    ps_name = vf_ps_name + remove_whitespace(inst_name)
    ps_name_id = ttfont['name'].addName(ps_name)
    inst.postscriptNameID = ps_name_id


def _add_nameid_25(ttfont, is_italic, has_mac_names):
  name = ttfont['name'].getName(16, 3, 1, 1033) or \
    ttfont['name'].getName(1, 3, 1, 1033).toUnicode()
  # if is_italic:
  #   name = f"{name}Italic"
  # else:
  #   name = f"{name}Roman"
  # ttfont['name'].setName(name, 25, 3, 1, 1033)
  if is_italic:
    name = f"{name}Italic"
    ttfont['name'].setName(name, 25, 3, 1, 1033)
  if has_mac_names:
    ttfont['name'].setName(name, 25, 1, 0, 0)
  return name


def main():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=__doc__
  )
  parser.add_argument("fonts", nargs="+", help=(
      "Paths to font files. Fonts must be part of the same family."
    )
  )
  args = parser.parse_args()
  paths = args.fonts

  # This monstrosity exists so we don't break the v1 api.
  italic_font = None
  if len(paths) > 2:
    raise Exception(
      "Can only add STAT tables to a max of two fonts. "
      "Run gftools fix-vf-meta --help for usage instructions"
    )
  elif len(paths) == 2:
    if "Italic" in paths[0]:
      tmp = paths[0]
      paths[0] = paths[1]
      paths[1] = tmp
    elif "Italic" not in paths[1]:
      raise Exception("No Italic font found!")
    roman_font = TTFont(paths[0])
    italic_font = TTFont(paths[1])
  else:
    roman_font = TTFont(paths[0])

  update_nametable(roman_font)
  if italic_font:
    update_nametable(italic_font)

  build_stat(roman_font, italic_font)

  roman_font.save(paths[0] + "-fixed.ttf")
  if italic_font:
    italic_font.save(paths[1] + "-fixed.ttf")

  # roman_font.save(paths[0])
  # if italic_font:
  #   italic_font.save(paths[1])


if __name__ == "__main__":
  main()
