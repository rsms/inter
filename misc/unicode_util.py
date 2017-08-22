#!/usr/bin/env python
# encoding: utf8

class MainCategories:
  Letter = 'Letter'
  Mark = 'Mark'
  Number = 'Number'
  Punctuation = 'Punctuation'
  Symbol = 'Symbol'
  Separator = 'Separator'
  Control = 'Control'
  Format = 'Format'
  Surrogate = 'Surrogate'
  PrivateUse = 'Private_Use'
  Unassigned = 'Unassigned'
  Other = 'Other'

GeneralCategories = {
  'Lu': ('Uppercase_Letter', MainCategories.Letter),
  'Ll': ('Lowercase_Letter', MainCategories.Letter),
  'Lt': ('Titlecase_Letter', MainCategories.Letter),
  'LC': ('Cased_Letter', MainCategories.Letter),
  'Lm': ('Modifier_Letter', MainCategories.Letter),
  'Lo': ('Other_Letter', MainCategories.Letter),
  'L':  ('Letter', MainCategories.Letter),
  'Mn': ('Nonspacing_Mark', MainCategories.Mark),
  'Mc': ('Spacing_Mark', MainCategories.Mark),
  'Me': ('Enclosing_Mark', MainCategories.Mark),
  'M':  ('Mark', MainCategories.Mark),
  'Nd': ('Decimal_Number', MainCategories.Number),
  'Nl': ('Letter_Number', MainCategories.Number),
  'No': ('Other_Number', MainCategories.Number),
  'N':  ('Number', MainCategories.Number),
  'Pc': ('Connector_Punctuation', MainCategories.Punctuation),
  'Pd': ('Dash_Punctuation', MainCategories.Punctuation),
  'Ps': ('Open_Punctuation', MainCategories.Punctuation),
  'Pe': ('Close_Punctuation', MainCategories.Punctuation),
  'Pi': ('Initial_Punctuation', MainCategories.Punctuation),
  'Pf': ('Final_Punctuation', MainCategories.Punctuation),
  'Po': ('Other_Punctuation', MainCategories.Punctuation),
  'P':  ('Punctuation', MainCategories.Punctuation),
  'Sm': ('Math_Symbol', MainCategories.Symbol),
  'Sc': ('Currency_Symbol', MainCategories.Symbol),
  'Sk': ('Modifier_Symbol', MainCategories.Symbol),
  'So': ('Other_Symbol', MainCategories.Symbol),
  'S':  ('Symbol', MainCategories.Symbol),
  'Zs': ('Space_Separator', MainCategories.Separator),
  'Zl': ('Line_Separator', MainCategories.Separator),
  'Zp': ('Paragraph_Separator', MainCategories.Separator),
  'Z':  ('Separator', MainCategories.Separator),
  'Cc': ('Control', MainCategories.Control),
  'Cf': ('Format', MainCategories.Format),
  'Cs': ('Surrogate', MainCategories.Surrogate),
  'Co': ('Private_Use', MainCategories.PrivateUse),
  'Cn': ('Unassigned', MainCategories.Unassigned),
  'C':  ('Other', MainCategories.Other),
}


class Codepoint:
  def __init__(self, v):
    self.codePoint = int(v[0], 16)
    self.name = v[1]

    self.category = v[2]
    c = GeneralCategories.get(self.category, ('', MainCategories.Other))
    self.categoryName = c[0]
    self.mainCategory = c[1]

    self.decDigitValue = v[6]
    self.numValue = v[8]

  def isLetter(self): return self.mainCategory is MainCategories.Letter
  def isMark(self): return self.mainCategory is MainCategories.Mark
  def isNumber(self): return self.mainCategory is MainCategories.Number
  def isPunctuation(self): return self.mainCategory is MainCategories.Punctuation
  def isSymbol(self): return self.mainCategory is MainCategories.Symbol
  def isSeparator(self): return self.mainCategory is MainCategories.Separator
  def isControl(self): return self.mainCategory is MainCategories.Control
  def isFormat(self): return self.mainCategory is MainCategories.Format
  def isSurrogate(self): return self.mainCategory is MainCategories.Surrogate
  def isPrivateUse(self): return self.mainCategory is MainCategories.PrivateUse
  def isUnassigned(self): return self.mainCategory is MainCategories.Unassigned
  def isOther(self): return self.mainCategory is MainCategories.Other


# http://www.unicode.org/Public/UCD/latest/ucd/UnicodeData.txt
def parseUnicodeDataFile(ucdFile):  # { codepoint:int => Codepoint() }
  ucd = {}
  with open(ucdFile, 'r') as f:
    for line in f:
      # See http://unicode.org/reports/tr44/#UnicodeData.txt for fields
      # e.g. "001D;<control>;Cc;0;B;;;;;N;INFORMATION SEPARATOR THREE;;;;"
      if len(line) == 0 or line.startswith('#'):
        continue
      v = line.split(';')
      if len(v) < 10:
        continue
      try:
        cp = Codepoint(v)
        ucd[cp.codePoint] = cp
      except:
        pass
  return ucd
