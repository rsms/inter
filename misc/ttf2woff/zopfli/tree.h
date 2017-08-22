/*
Copyright 2011 Google Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: lode.vandevenne@gmail.com (Lode Vandevenne)
Author: jyrki.alakuijala@gmail.com (Jyrki Alakuijala)
*/

/*
Utilities for creating and using Huffman trees.
*/

#ifndef ZOPFLI_TREE_H_
#define ZOPFLI_TREE_H_

#include <string.h>

/*
Calculates the bitlengths for the Huffman tree, based on the counts of each
symbol.
*/
void ZopfliCalculateBitLengths(const size_t* count, size_t n, int maxbits,
                               unsigned *bitlengths);

/*
Converts a series of Huffman tree bitlengths, to the bit values of the symbols.
*/
void ZopfliLengthsToSymbols(const unsigned* lengths, size_t n, unsigned maxbits,
                            unsigned* symbols);

/*
Calculates the entropy of each symbol, based on the counts of each symbol. The
result is similar to the result of ZopfliCalculateBitLengths, but with the
actual theoritical bit lengths according to the entropy. Since the resulting
values are fractional, they cannot be used to encode the tree specified by
DEFLATE.
*/
void ZopfliCalculateEntropy(const size_t* count, size_t n, double* bitlengths);

#endif  /* ZOPFLI_TREE_H_ */
