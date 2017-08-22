/*
Copyright 2013 Google Inc. All Rights Reserved.

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

#ifndef ZOPFLI_ZLIB_H_
#define ZOPFLI_ZLIB_H_

/*
Functions to compress according to the Zlib specification.
*/

#include "zopfli.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
Compresses according to the zlib specification and append the compressed
result to the output.

options: global program options
out: pointer to the dynamic output array to which the result is appended. Must
  be freed after use.
outsize: pointer to the dynamic output array size.
*/
void ZopfliZlibCompress(const ZopfliOptions* options,
                        const unsigned char* in, size_t insize,
                        unsigned char** out, size_t* outsize);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  /* ZOPFLI_ZLIB_H_ */
