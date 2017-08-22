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
The cache that speeds up ZopfliFindLongestMatch of lz77.c.
*/

#ifndef ZOPFLI_CACHE_H_
#define ZOPFLI_CACHE_H_

#include "util.h"

#ifdef ZOPFLI_LONGEST_MATCH_CACHE

/*
Cache used by ZopfliFindLongestMatch to remember previously found length/dist
values.
This is needed because the squeeze runs will ask these values multiple times for
the same position.
Uses large amounts of memory, since it has to remember the distance belonging
to every possible shorter-than-the-best length (the so called "sublen" array).
*/
typedef struct ZopfliLongestMatchCache {
  unsigned short* length;
  unsigned short* dist;
  unsigned char* sublen;
} ZopfliLongestMatchCache;

/* Initializes the ZopfliLongestMatchCache. */
void ZopfliInitCache(size_t blocksize, ZopfliLongestMatchCache* lmc);

/* Frees up the memory of the ZopfliLongestMatchCache. */
void ZopfliCleanCache(ZopfliLongestMatchCache* lmc);

/* Stores sublen array in the cache. */
void ZopfliSublenToCache(const unsigned short* sublen,
                         size_t pos, size_t length,
                         ZopfliLongestMatchCache* lmc);

/* Extracts sublen array from the cache. */
void ZopfliCacheToSublen(const ZopfliLongestMatchCache* lmc,
                         size_t pos, size_t length,
                         unsigned short* sublen);
/* Returns the length up to which could be stored in the cache. */
unsigned ZopfliMaxCachedSublen(const ZopfliLongestMatchCache* lmc,
                               size_t pos, size_t length);

#endif  /* ZOPFLI_LONGEST_MATCH_CACHE */

#endif  /* ZOPFLI_CACHE_H_ */
