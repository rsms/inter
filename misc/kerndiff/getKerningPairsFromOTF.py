#!/usr/bin/env python
#
# Copyright (c) 2013-2016 Adobe Systems Incorporated. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE. import sys import os import itertools

from __future__ import print_function
import os
import sys
from fontTools import ttLib

__doc__ = '''\

Prints all possible kerning pairs within font.
Supports RTL kerning.

Usage:
------
python getKerningPairsFromOTF.py <path to font file>

'''

kKernFeatureTag = 'kern'
kGPOStableName = 'GPOS'
finalList = []


class myLeftClass:
    def __init__(self):
        self.glyphs = []
        self.class1Record = 0


class myRightClass:
    def __init__(self):
        self.glyphs = []
        self.class2Record = 0


def collectUniqueKernLookupListIndexes(featureRecord):
    uniqueKernLookupIndexList = []
    for featRecItem in featureRecord:
        # print(featRecItem.FeatureTag)
        # GPOS feature tags (e.g. kern, mark, mkmk, size) of each ScriptRecord
        if featRecItem.FeatureTag == kKernFeatureTag:
            feature = featRecItem.Feature

            for featLookupItem in feature.LookupListIndex:
                if featLookupItem not in uniqueKernLookupIndexList:
                    uniqueKernLookupIndexList.append(featLookupItem)

    return uniqueKernLookupIndexList


class OTFKernReader(object):

    def __init__(self, fontPath):
        self.font = ttLib.TTFont(fontPath)
        self.kerningPairs = {}
        self.singlePairs = {}
        self.classPairs = {}
        self.pairPosList = []
        self.allLeftClasses = {}
        self.allRightClasses = {}

        if kGPOStableName not in self.font:
            print("The font has no %s table" % kGPOStableName, file=sys.stderr)
            self.goodbye()

        else:
            self.analyzeFont()
            self.findKerningLookups()
            self.getPairPos()
            self.getSinglePairs()
            self.getClassPairs()

    def goodbye(self):
        print('The fun ends here.', file=sys.stderr)
        return

    def analyzeFont(self):
        self.gposTable = self.font[kGPOStableName].table

        'ScriptList:'
        self.scriptList = self.gposTable.ScriptList
        'FeatureList:'
        self.featureList = self.gposTable.FeatureList

        self.featureCount = self.featureList.FeatureCount
        self.featureRecord = self.featureList.FeatureRecord

        self.uniqueKernLookupIndexList = collectUniqueKernLookupListIndexes(self.featureRecord)

    def findKerningLookups(self):
        if not len(self.uniqueKernLookupIndexList):
            print("The font has no %s feature." % kKernFeatureTag, file=sys.stderr)
            self.goodbye()

        'LookupList:'
        self.lookupList = self.gposTable.LookupList
        self.lookups = []
        for kernLookupIndex in sorted(self.uniqueKernLookupIndexList):
            lookup = self.lookupList.Lookup[kernLookupIndex]

            # Confirm this is a GPOS LookupType 2; or
            # using an extension table (GPOS LookupType 9):

            '''
            Lookup types:
            1   Single adjustment           Adjust position of a single glyph
            2   Pair adjustment             Adjust position of a pair of glyphs
            3   Cursive attachment          Attach cursive glyphs
            4   MarkToBase attachment       Attach a combining mark to a base glyph
            5   MarkToLigature attachment   Attach a combining mark to a ligature
            6   MarkToMark attachment       Attach a combining mark to another mark
            7   Context positioning         Position one or more glyphs in context
            8   Chained Context positioning Position one or more glyphs in chained context
            9   Extension positioning       Extension mechanism for other positionings
            10+ Reserved for future use
            '''

            if lookup.LookupType not in [2, 9]:
                print('''
                Info: GPOS LookupType %s found.
                This type is neither a pair adjustment positioning lookup (GPOS LookupType 2),
                nor using an extension table (GPOS LookupType 9), which are the only ones supported.
                ''' % lookup.LookupType, file=sys.stderr)
                continue
            self.lookups.append(lookup)


    def getPairPos(self):
        for lookup in self.lookups:
            for subtableItem in lookup.SubTable:

                if subtableItem.LookupType == 9:  # extension table
                    if subtableItem.ExtensionLookupType == 8:  # contextual
                        print('Contextual Kerning not (yet?) supported.', file=sys.stderr)
                        continue
                    elif subtableItem.ExtensionLookupType == 2:
                        subtableItem = subtableItem.ExtSubTable


                # if subtableItem.Coverage.Format not in [1, 2]:  # previous fontTools
                if subtableItem.Format not in [1, 2]:
                    print("WARNING: Coverage format %d is not yet supported." % subtableItem.Coverage.Format, file=sys.stderr)

                if subtableItem.ValueFormat1 not in [0, 4, 5]:
                    print("WARNING: ValueFormat1 format %d is not yet supported." % subtableItem.ValueFormat1, file=sys.stderr)

                if subtableItem.ValueFormat2 not in [0]:
                    print("WARNING: ValueFormat2 format %d is not yet supported." % subtableItem.ValueFormat2, file=sys.stderr)


                self.pairPosList.append(subtableItem)

                # Each glyph in this list will have a corresponding PairSet
                # which will contain all the second glyphs and the kerning
                # value in the form of PairValueRecord(s)
                # self.firstGlyphsList.extend(subtableItem.Coverage.glyphs)


    def getSinglePairs(self):
        for pairPos in self.pairPosList:
            if pairPos.Format == 1:
                # single pair adjustment

                firstGlyphsList = pairPos.Coverage.glyphs

                # This iteration is done by index so we have a way
                # to reference the firstGlyphsList:
                for pairSetIndex, pairSetInstance in enumerate(pairPos.PairSet):
                    for pairValueRecordItem in pairPos.PairSet[pairSetIndex].PairValueRecord:
                        secondGlyph = pairValueRecordItem.SecondGlyph
                        valueFormat = pairPos.ValueFormat1

                        if valueFormat == 5:  # RTL kerning
                            kernValue = "<%d 0 %d 0>" % (
                                pairValueRecordItem.Value1.XPlacement,
                                pairValueRecordItem.Value1.XAdvance)
                        elif valueFormat == 0:  # RTL pair with value <0 0 0 0>
                            kernValue = "<0 0 0 0>"
                        elif valueFormat == 4:  # LTR kerning
                            kernValue = pairValueRecordItem.Value1.XAdvance
                        else:
                            print("\tValueFormat1 = %d" % valueFormat, file=sys.stdout)
                            continue  # skip the rest

                        self.kerningPairs[(firstGlyphsList[pairSetIndex], secondGlyph)] = kernValue
                        self.singlePairs[(firstGlyphsList[pairSetIndex], secondGlyph)] = kernValue

    def getClassPairs(self):
        for loop, pairPos in enumerate(self.pairPosList):
            if pairPos.Format == 2:

                leftClasses = {}
                rightClasses = {}

                # Find left class with the Class1Record index="0".
                # This first class is mixed into the "Coverage" table
                # (e.g. all left glyphs) and has no class="X" property
                # that is why we have to find the glyphs in that way.

                lg0 = myLeftClass()

                # list of all glyphs kerned to the left of a pair:
                allLeftGlyphs = pairPos.Coverage.glyphs
                # list of all glyphs contained within left-sided kerning classes:
                # allLeftClassGlyphs = pairPos.ClassDef1.classDefs.keys()

                singleGlyphs = []
                classGlyphs = []

                for gName, classID in pairPos.ClassDef1.classDefs.items():
                    if classID == 0:
                        singleGlyphs.append(gName)
                    else:
                        classGlyphs.append(gName)

                # lg0.glyphs =  list(set(allLeftGlyphs) - set(allLeftClassGlyphs)) # coverage glyphs minus glyphs in a class (including class 0)
                lg0.glyphs = list(set(allLeftGlyphs) - set(classGlyphs))  # coverage glyphs minus glyphs in real class (without class 0)

                lg0.glyphs.sort()
                leftClasses[lg0.class1Record] = lg0
                className = "class_%s_%s" % (loop, lg0.class1Record)
                self.allLeftClasses[className] = lg0.glyphs

                # Find all the remaining left classes:
                for leftGlyph in pairPos.ClassDef1.classDefs:
                    class1Record = pairPos.ClassDef1.classDefs[leftGlyph]

                    if class1Record != 0:  # this was the crucial line.
                        lg = myLeftClass()
                        lg.class1Record = class1Record
                        leftClasses.setdefault(class1Record, lg).glyphs.append(leftGlyph)
                        self.allLeftClasses.setdefault("class_%s_%s" % (loop, lg.class1Record), lg.glyphs)

                # Same for the right classes:
                for rightGlyph in pairPos.ClassDef2.classDefs:
                    class2Record = pairPos.ClassDef2.classDefs[rightGlyph]
                    rg = myRightClass()
                    rg.class2Record = class2Record
                    rightClasses.setdefault(class2Record, rg).glyphs.append(rightGlyph)
                    self.allRightClasses.setdefault("class_%s_%s" % (loop, rg.class2Record), rg.glyphs)

                for record_l in leftClasses:
                    for record_r in rightClasses:
                        if pairPos.Class1Record[record_l].Class2Record[record_r]:
                            valueFormat = pairPos.ValueFormat1

                            if valueFormat in [4, 5]:
                                kernValue = pairPos.Class1Record[record_l].Class2Record[record_r].Value1.XAdvance
                            elif valueFormat == 0:
                                # valueFormat zero is caused by a value of <0 0 0 0> on a class-class pair; skip these
                                continue
                            else:
                                print("\tValueFormat1 = %d" % valueFormat, file=sys.stdout)
                                continue  # skip the rest

                            if kernValue != 0:
                                leftClassName = 'class_%s_%s'  % (loop, leftClasses[record_l].class1Record)
                                rightClassName = 'class_%s_%s' % (loop, rightClasses[record_r].class2Record)

                                self.classPairs[(leftClassName, rightClassName)] = kernValue

                                for l in leftClasses[record_l].glyphs:
                                    for r in rightClasses[record_r].glyphs:
                                        if (l, r) in self.kerningPairs:
                                            # if the kerning pair has already been assigned in pair-to-pair kerning
                                            continue
                                        else:
                                            if valueFormat == 5: # RTL kerning
                                                kernValue = "<%d 0 %d 0>" % (pairPos.Class1Record[record_l].Class2Record[record_r].Value1.XPlacement, pairPos.Class1Record[record_l].Class2Record[record_r].Value1.XAdvance)


                                            self.kerningPairs[(l, r)] = kernValue

                        else:
                            print('ERROR', file=sys.stderr)


if __name__ == "__main__":

    if len(sys.argv) == 2:
        assumedFontPath = sys.argv[1]
        if os.path.exists(assumedFontPath) and os.path.splitext(assumedFontPath)[1].lower() in ['.otf', '.ttf']:
            fontPath = sys.argv[1]
            f = OTFKernReader(fontPath)

            finalList = []
            for pair, value in f.kerningPairs.items():
                finalList.append('/%s /%s %s' % ( pair[0], pair[1], value ))

            finalList.sort()

            output = '\n'.join(sorted(finalList))
            print(output, file=sys.stdout)

            # print('\nTotal number of kerning pairs:', file=sys.stdout)
            # print(len(f.kerningPairs), file=sys.stdout)
            # for i in sorted(f.allLeftClasses):
            #     print(i, f.allLeftClasses[i], file=sys.stdout)

        else:
            print('That is not a valid font.', file=sys.stderr)
    else:
        print('Please provide a font.', file=sys.stderr)
