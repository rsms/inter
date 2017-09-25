# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from ufo2ft.kernFeatureWriter import KernFeatureWriter
from ufo2ft.makeotfParts import FeatureOTFCompiler


class RobotoFeatureCompiler(FeatureOTFCompiler):
    def precompile(self):
        self.overwriteFeatures = True

    def setupAnchorPairs(self):
        self.anchorPairs = [
            ["top", "_marktop"],
            ["bottom", "_markbottom"],
            ["top_dd", "_marktop_dd"],
            ["bottom_dd", "_markbottom_dd"],
            ["rhotichook", "_markrhotichook"],
            ["top0315", "_marktop0315"],
        ]

        self.mkmkAnchorPairs = [
            ["mkmktop", "_marktop"],
            ["mkmkbottom_acc", "_markbottom"],

            # By providing a pair with accent anchor _bottom and no base anchor,
            # we designate all glyphs with _bottom as accents (so that they will
            # be used as base glyphs for mkmk features) without generating any
            # positioning rules actually using this anchor (which is instead
            # used to generate composite glyphs). This is all for consistency
            # with older roboto versions.
            ["", "_bottom"],
        ]

        self.ligaAnchorPairs = []


class RobotoKernWriter(KernFeatureWriter):
    leftFeaClassRe = r"@_(.+)_L$"
    rightFeaClassRe = r"@_(.+)_R$"
