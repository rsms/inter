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
Functions to choose good boundaries for block splitting. Deflate allows encoding
the data in multiple blocks, with a separate Huffman tree for each block. The
Huffman tree itself requires some bytes to encode, so by choosing certain
blocks, you can either hurt, or enhance compression. These functions choose good
ones that enhance it.
*/

#ifndef ZOPFLI_BLOCKSPLITTER_H_
#define ZOPFLI_BLOCKSPLITTER_H_

#include <stdlib.h>

#include "lz77.h"
#include "zopfli.h"


/*
Does blocksplitting on LZ77 data.
The output splitpoints are indices in the LZ77 data.
maxblocks: set a limit to the amount of blocks. Set to 0 to mean no limit.
*/
void ZopfliBlockSplitLZ77(const ZopfliOptions* options,
                          const ZopfliLZ77Store* lz77, size_t maxblocks,
                          size_t** splitpoints, size_t* npoints);

/*
Does blocksplitting on uncompressed data.
The output splitpoints are indices in the uncompressed bytes.

options: general program options.
in: uncompressed input data
instart: where to start splitting
inend: where to end splitting (not inclusive)
maxblocks: maximum amount of blocks to split into, or 0 for no limit
splitpoints: dynamic array to put the resulting split point coordinates into.
  The coordinates are indices in the input array.
npoints: pointer to amount of splitpoints, for the dynamic array. The amount of
  blocks is the amount of splitpoitns + 1.
*/
void ZopfliBlockSplit(const ZopfliOptions* options,
                      const unsigned char* in, size_t instart, size_t inend,
                      size_t maxblocks, size_t** splitpoints, size_t* npoints);

/*
Divides the input into equal blocks, does not even take LZ77 lengths into
account.
*/
void ZopfliBlockSplitSimple(const unsigned char* in,
                            size_t instart, size_t inend,
                            size_t blocksize,
                            size_t** splitpoints, size_t* npoints);

#endif  /* ZOPFLI_BLOCKSPLITTER_H_ */
