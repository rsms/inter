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

#ifndef ZOPFLI_ZOPFLI_H_
#define ZOPFLI_ZOPFLI_H_

#include <stddef.h>
#include <stdlib.h> /* for size_t */

#ifdef __cplusplus
extern "C" {
#endif

/*
Options used throughout the program.
*/
typedef struct ZopfliOptions {
  /* Whether to print output */
  int verbose;

  /* Whether to print more detailed output */
  int verbose_more;

  /*
  Maximum amount of times to rerun forward and backward pass to optimize LZ77
  compression cost. Good values: 10, 15 for small files, 5 for files over
  several MB in size or it will be too slow.
  */
  int numiterations;

  /*
  If true, splits the data in multiple deflate blocks with optimal choice
  for the block boundaries. Block splitting gives better compression. Default:
  true (1).
  */
  int blocksplitting;

  /*
  No longer used, left for compatibility.
  */
  int blocksplittinglast;

  /*
  Maximum amount of blocks to split into (0 for unlimited, but this can give
  extreme results that hurt compression on some files). Default value: 15.
  */
  int blocksplittingmax;
} ZopfliOptions;

/* Initializes options with default values. */
void ZopfliInitOptions(ZopfliOptions* options);

/* Output format */
typedef enum {
  ZOPFLI_FORMAT_GZIP,
  ZOPFLI_FORMAT_ZLIB,
  ZOPFLI_FORMAT_DEFLATE
} ZopfliFormat;

/*
Compresses according to the given output format and appends the result to the
output.

options: global program options
output_type: the output format to use
out: pointer to the dynamic output array to which the result is appended. Must
  be freed after use
outsize: pointer to the dynamic output array size
*/
void ZopfliCompress(const ZopfliOptions* options, ZopfliFormat output_type,
                    const unsigned char* in, size_t insize,
                    unsigned char** out, size_t* outsize);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  /* ZOPFLI_ZOPFLI_H_ */
