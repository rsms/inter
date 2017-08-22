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
The squeeze functions do enhanced LZ77 compression by optimal parsing with a
cost model, rather than greedily choosing the longest length or using a single
step of lazy matching like regular implementations.

Since the cost model is based on the Huffman tree that can only be calculated
after the LZ77 data is generated, there is a chicken and egg problem, and
multiple runs are done with updated cost models to converge to a better
solution.
*/

#ifndef ZOPFLI_SQUEEZE_H_
#define ZOPFLI_SQUEEZE_H_

#include "lz77.h"

/*
Calculates lit/len and dist pairs for given data.
If instart is larger than 0, it uses values before instart as starting
dictionary.
*/
void ZopfliLZ77Optimal(ZopfliBlockState *s,
                       const unsigned char* in, size_t instart, size_t inend,
                       int numiterations,
                       ZopfliLZ77Store* store);

/*
Does the same as ZopfliLZ77Optimal, but optimized for the fixed tree of the
deflate standard.
The fixed tree never gives the best compression. But this gives the best
possible LZ77 encoding possible with the fixed tree.
This does not create or output any fixed tree, only LZ77 data optimized for
using with a fixed tree.
If instart is larger than 0, it uses values before instart as starting
dictionary.
*/
void ZopfliLZ77OptimalFixed(ZopfliBlockState *s,
                            const unsigned char* in,
                            size_t instart, size_t inend,
                            ZopfliLZ77Store* store);

#endif  /* ZOPFLI_SQUEEZE_H_ */
