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

#include "lz77.h"
#include "symbols.h"
#include "util.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

void ZopfliInitLZ77Store(const unsigned char* data, ZopfliLZ77Store* store) {
  store->size = 0;
  store->litlens = 0;
  store->dists = 0;
  store->pos = 0;
  store->data = data;
  store->ll_symbol = 0;
  store->d_symbol = 0;
  store->ll_counts = 0;
  store->d_counts = 0;
}

void ZopfliCleanLZ77Store(ZopfliLZ77Store* store) {
  free(store->litlens);
  free(store->dists);
  free(store->pos);
  free(store->ll_symbol);
  free(store->d_symbol);
  free(store->ll_counts);
  free(store->d_counts);
}

static size_t CeilDiv(size_t a, size_t b) {
  return (a + b - 1) / b;
}

void ZopfliCopyLZ77Store(
    const ZopfliLZ77Store* source, ZopfliLZ77Store* dest) {
  size_t i;
  size_t llsize = ZOPFLI_NUM_LL * CeilDiv(source->size, ZOPFLI_NUM_LL);
  size_t dsize = ZOPFLI_NUM_D * CeilDiv(source->size, ZOPFLI_NUM_D);
  ZopfliCleanLZ77Store(dest);
  ZopfliInitLZ77Store(source->data, dest);
  dest->litlens =
      (unsigned short*)malloc(sizeof(*dest->litlens) * source->size);
  dest->dists = (unsigned short*)malloc(sizeof(*dest->dists) * source->size);
  dest->pos = (size_t*)malloc(sizeof(*dest->pos) * source->size);
  dest->ll_symbol =
      (unsigned short*)malloc(sizeof(*dest->ll_symbol) * source->size);
  dest->d_symbol =
      (unsigned short*)malloc(sizeof(*dest->d_symbol) * source->size);
  dest->ll_counts = (size_t*)malloc(sizeof(*dest->ll_counts) * llsize);
  dest->d_counts = (size_t*)malloc(sizeof(*dest->d_counts) * dsize);

  /* Allocation failed. */
  if (!dest->litlens || !dest->dists) exit(-1);
  if (!dest->pos) exit(-1);
  if (!dest->ll_symbol || !dest->d_symbol) exit(-1);
  if (!dest->ll_counts || !dest->d_counts) exit(-1);

  dest->size = source->size;
  for (i = 0; i < source->size; i++) {
    dest->litlens[i] = source->litlens[i];
    dest->dists[i] = source->dists[i];
    dest->pos[i] = source->pos[i];
    dest->ll_symbol[i] = source->ll_symbol[i];
    dest->d_symbol[i] = source->d_symbol[i];
  }
  for (i = 0; i < llsize; i++) {
    dest->ll_counts[i] = source->ll_counts[i];
  }
  for (i = 0; i < dsize; i++) {
    dest->d_counts[i] = source->d_counts[i];
  }
}

/*
Appends the length and distance to the LZ77 arrays of the ZopfliLZ77Store.
context must be a ZopfliLZ77Store*.
*/
void ZopfliStoreLitLenDist(unsigned short length, unsigned short dist,
                           size_t pos, ZopfliLZ77Store* store) {
  size_t i;
  /* Needed for using ZOPFLI_APPEND_DATA multiple times. */
  size_t origsize = store->size;
  size_t llstart = ZOPFLI_NUM_LL * (origsize / ZOPFLI_NUM_LL);
  size_t dstart = ZOPFLI_NUM_D * (origsize / ZOPFLI_NUM_D);

  /* Everytime the index wraps around, a new cumulative histogram is made: we're
  keeping one histogram value per LZ77 symbol rather than a full histogram for
  each to save memory. */
  if (origsize % ZOPFLI_NUM_LL == 0) {
    size_t llsize = origsize;
    for (i = 0; i < ZOPFLI_NUM_LL; i++) {
      ZOPFLI_APPEND_DATA(
          origsize == 0 ? 0 : store->ll_counts[origsize - ZOPFLI_NUM_LL + i],
          &store->ll_counts, &llsize);
    }
  }
  if (origsize % ZOPFLI_NUM_D == 0) {
    size_t dsize = origsize;
    for (i = 0; i < ZOPFLI_NUM_D; i++) {
      ZOPFLI_APPEND_DATA(
          origsize == 0 ? 0 : store->d_counts[origsize - ZOPFLI_NUM_D + i],
          &store->d_counts, &dsize);
    }
  }

  ZOPFLI_APPEND_DATA(length, &store->litlens, &store->size);
  store->size = origsize;
  ZOPFLI_APPEND_DATA(dist, &store->dists, &store->size);
  store->size = origsize;
  ZOPFLI_APPEND_DATA(pos, &store->pos, &store->size);
  assert(length < 259);

  if (dist == 0) {
    store->size = origsize;
    ZOPFLI_APPEND_DATA(length, &store->ll_symbol, &store->size);
    store->size = origsize;
    ZOPFLI_APPEND_DATA(0, &store->d_symbol, &store->size);
    store->ll_counts[llstart + length]++;
  } else {
    store->size = origsize;
    ZOPFLI_APPEND_DATA(ZopfliGetLengthSymbol(length),
                       &store->ll_symbol, &store->size);
    store->size = origsize;
    ZOPFLI_APPEND_DATA(ZopfliGetDistSymbol(dist),
                       &store->d_symbol, &store->size);
    store->ll_counts[llstart + ZopfliGetLengthSymbol(length)]++;
    store->d_counts[dstart + ZopfliGetDistSymbol(dist)]++;
  }
}

void ZopfliAppendLZ77Store(const ZopfliLZ77Store* store,
                           ZopfliLZ77Store* target) {
  size_t i;
  for (i = 0; i < store->size; i++) {
    ZopfliStoreLitLenDist(store->litlens[i], store->dists[i],
                          store->pos[i], target);
  }
}

size_t ZopfliLZ77GetByteRange(const ZopfliLZ77Store* lz77,
                              size_t lstart, size_t lend) {
  size_t l = lend - 1;
  if (lstart == lend) return 0;
  return lz77->pos[l] + ((lz77->dists[l] == 0) ?
      1 : lz77->litlens[l]) - lz77->pos[lstart];
}

static void ZopfliLZ77GetHistogramAt(const ZopfliLZ77Store* lz77, size_t lpos,
                                     size_t* ll_counts, size_t* d_counts) {
  /* The real histogram is created by using the histogram for this chunk, but
  all superfluous values of this chunk subtracted. */
  size_t llpos = ZOPFLI_NUM_LL * (lpos / ZOPFLI_NUM_LL);
  size_t dpos = ZOPFLI_NUM_D * (lpos / ZOPFLI_NUM_D);
  size_t i;
  for (i = 0; i < ZOPFLI_NUM_LL; i++) {
    ll_counts[i] = lz77->ll_counts[llpos + i];
  }
  for (i = lpos + 1; i < llpos + ZOPFLI_NUM_LL && i < lz77->size; i++) {
    ll_counts[lz77->ll_symbol[i]]--;
  }
  for (i = 0; i < ZOPFLI_NUM_D; i++) {
    d_counts[i] = lz77->d_counts[dpos + i];
  }
  for (i = lpos + 1; i < dpos + ZOPFLI_NUM_D && i < lz77->size; i++) {
    if (lz77->dists[i] != 0) d_counts[lz77->d_symbol[i]]--;
  }
}

void ZopfliLZ77GetHistogram(const ZopfliLZ77Store* lz77,
                           size_t lstart, size_t lend,
                           size_t* ll_counts, size_t* d_counts) {
  size_t i;
  if (lstart + ZOPFLI_NUM_LL * 3 > lend) {
    memset(ll_counts, 0, sizeof(*ll_counts) * ZOPFLI_NUM_LL);
    memset(d_counts, 0, sizeof(*d_counts) * ZOPFLI_NUM_D);
    for (i = lstart; i < lend; i++) {
      ll_counts[lz77->ll_symbol[i]]++;
      if (lz77->dists[i] != 0) d_counts[lz77->d_symbol[i]]++;
    }
  } else {
    /* Subtract the cumulative histograms at the end and the start to get the
    histogram for this range. */
    ZopfliLZ77GetHistogramAt(lz77, lend - 1, ll_counts, d_counts);
    if (lstart > 0) {
      size_t ll_counts2[ZOPFLI_NUM_LL];
      size_t d_counts2[ZOPFLI_NUM_D];
      ZopfliLZ77GetHistogramAt(lz77, lstart - 1, ll_counts2, d_counts2);

      for (i = 0; i < ZOPFLI_NUM_LL; i++) {
        ll_counts[i] -= ll_counts2[i];
      }
      for (i = 0; i < ZOPFLI_NUM_D; i++) {
        d_counts[i] -= d_counts2[i];
      }
    }
  }
}

void ZopfliInitBlockState(const ZopfliOptions* options,
                          size_t blockstart, size_t blockend, int add_lmc,
                          ZopfliBlockState* s) {
  s->options = options;
  s->blockstart = blockstart;
  s->blockend = blockend;
#ifdef ZOPFLI_LONGEST_MATCH_CACHE
  if (add_lmc) {
    s->lmc = (ZopfliLongestMatchCache*)malloc(sizeof(ZopfliLongestMatchCache));
    ZopfliInitCache(blockend - blockstart, s->lmc);
  } else {
    s->lmc = 0;
  }
#endif
}

void ZopfliCleanBlockState(ZopfliBlockState* s) {
#ifdef ZOPFLI_LONGEST_MATCH_CACHE
  if (s->lmc) {
    ZopfliCleanCache(s->lmc);
    free(s->lmc);
  }
#endif
}

/*
Gets a score of the length given the distance. Typically, the score of the
length is the length itself, but if the distance is very long, decrease the
score of the length a bit to make up for the fact that long distances use large
amounts of extra bits.

This is not an accurate score, it is a heuristic only for the greedy LZ77
implementation. More accurate cost models are employed later. Making this
heuristic more accurate may hurt rather than improve compression.

The two direct uses of this heuristic are:
-avoid using a length of 3 in combination with a long distance. This only has
 an effect if length == 3.
-make a slightly better choice between the two options of the lazy matching.

Indirectly, this affects:
-the block split points if the default of block splitting first is used, in a
 rather unpredictable way
-the first zopfli run, so it affects the chance of the first run being closer
 to the optimal output
*/
static int GetLengthScore(int length, int distance) {
  /*
  At 1024, the distance uses 9+ extra bits and this seems to be the sweet spot
  on tested files.
  */
  return distance > 1024 ? length - 1 : length;
}

void ZopfliVerifyLenDist(const unsigned char* data, size_t datasize, size_t pos,
                         unsigned short dist, unsigned short length) {

  /* TODO(lode): make this only run in a debug compile, it's for assert only. */
  size_t i;

  assert(pos + length <= datasize);
  for (i = 0; i < length; i++) {
    if (data[pos - dist + i] != data[pos + i]) {
      assert(data[pos - dist + i] == data[pos + i]);
      break;
    }
  }
}

/*
Finds how long the match of scan and match is. Can be used to find how many
bytes starting from scan, and from match, are equal. Returns the last byte
after scan, which is still equal to the correspondinb byte after match.
scan is the position to compare
match is the earlier position to compare.
end is the last possible byte, beyond which to stop looking.
safe_end is a few (8) bytes before end, for comparing multiple bytes at once.
*/
static const unsigned char* GetMatch(const unsigned char* scan,
                                     const unsigned char* match,
                                     const unsigned char* end,
                                     const unsigned char* safe_end) {

  if (sizeof(size_t) == 8) {
    /* 8 checks at once per array bounds check (size_t is 64-bit). */
    while (scan < safe_end && *((size_t*)scan) == *((size_t*)match)) {
      scan += 8;
      match += 8;
    }
  } else if (sizeof(unsigned int) == 4) {
    /* 4 checks at once per array bounds check (unsigned int is 32-bit). */
    while (scan < safe_end
        && *((unsigned int*)scan) == *((unsigned int*)match)) {
      scan += 4;
      match += 4;
    }
  } else {
    /* do 8 checks at once per array bounds check. */
    while (scan < safe_end && *scan == *match && *++scan == *++match
          && *++scan == *++match && *++scan == *++match
          && *++scan == *++match && *++scan == *++match
          && *++scan == *++match && *++scan == *++match) {
      scan++; match++;
    }
  }

  /* The remaining few bytes. */
  while (scan != end && *scan == *match) {
    scan++; match++;
  }

  return scan;
}

#ifdef ZOPFLI_LONGEST_MATCH_CACHE
/*
Gets distance, length and sublen values from the cache if possible.
Returns 1 if it got the values from the cache, 0 if not.
Updates the limit value to a smaller one if possible with more limited
information from the cache.
*/
static int TryGetFromLongestMatchCache(ZopfliBlockState* s,
    size_t pos, size_t* limit,
    unsigned short* sublen, unsigned short* distance, unsigned short* length) {
  /* The LMC cache starts at the beginning of the block rather than the
     beginning of the whole array. */
  size_t lmcpos = pos - s->blockstart;

  /* Length > 0 and dist 0 is invalid combination, which indicates on purpose
     that this cache value is not filled in yet. */
  unsigned char cache_available = s->lmc && (s->lmc->length[lmcpos] == 0 ||
      s->lmc->dist[lmcpos] != 0);
  unsigned char limit_ok_for_cache = cache_available &&
      (*limit == ZOPFLI_MAX_MATCH || s->lmc->length[lmcpos] <= *limit ||
      (sublen && ZopfliMaxCachedSublen(s->lmc,
          lmcpos, s->lmc->length[lmcpos]) >= *limit));

  if (s->lmc && limit_ok_for_cache && cache_available) {
    if (!sublen || s->lmc->length[lmcpos]
        <= ZopfliMaxCachedSublen(s->lmc, lmcpos, s->lmc->length[lmcpos])) {
      *length = s->lmc->length[lmcpos];
      if (*length > *limit) *length = *limit;
      if (sublen) {
        ZopfliCacheToSublen(s->lmc, lmcpos, *length, sublen);
        *distance = sublen[*length];
        if (*limit == ZOPFLI_MAX_MATCH && *length >= ZOPFLI_MIN_MATCH) {
          assert(sublen[*length] == s->lmc->dist[lmcpos]);
        }
      } else {
        *distance = s->lmc->dist[lmcpos];
      }
      return 1;
    }
    /* Can't use much of the cache, since the "sublens" need to be calculated,
       but at  least we already know when to stop. */
    *limit = s->lmc->length[lmcpos];
  }

  return 0;
}

/*
Stores the found sublen, distance and length in the longest match cache, if
possible.
*/
static void StoreInLongestMatchCache(ZopfliBlockState* s,
    size_t pos, size_t limit,
    const unsigned short* sublen,
    unsigned short distance, unsigned short length) {
  /* The LMC cache starts at the beginning of the block rather than the
     beginning of the whole array. */
  size_t lmcpos = pos - s->blockstart;

  /* Length > 0 and dist 0 is invalid combination, which indicates on purpose
     that this cache value is not filled in yet. */
  unsigned char cache_available = s->lmc && (s->lmc->length[lmcpos] == 0 ||
      s->lmc->dist[lmcpos] != 0);

  if (s->lmc && limit == ZOPFLI_MAX_MATCH && sublen && !cache_available) {
    assert(s->lmc->length[lmcpos] == 1 && s->lmc->dist[lmcpos] == 0);
    s->lmc->dist[lmcpos] = length < ZOPFLI_MIN_MATCH ? 0 : distance;
    s->lmc->length[lmcpos] = length < ZOPFLI_MIN_MATCH ? 0 : length;
    assert(!(s->lmc->length[lmcpos] == 1 && s->lmc->dist[lmcpos] == 0));
    ZopfliSublenToCache(sublen, lmcpos, length, s->lmc);
  }
}
#endif

void ZopfliFindLongestMatch(ZopfliBlockState* s, const ZopfliHash* h,
    const unsigned char* array,
    size_t pos, size_t size, size_t limit,
    unsigned short* sublen, unsigned short* distance, unsigned short* length) {
  unsigned short hpos = pos & ZOPFLI_WINDOW_MASK, p, pp;
  unsigned short bestdist = 0;
  unsigned short bestlength = 1;
  const unsigned char* scan;
  const unsigned char* match;
  const unsigned char* arrayend;
  const unsigned char* arrayend_safe;
#if ZOPFLI_MAX_CHAIN_HITS < ZOPFLI_WINDOW_SIZE
  int chain_counter = ZOPFLI_MAX_CHAIN_HITS;  /* For quitting early. */
#endif

  unsigned dist = 0;  /* Not unsigned short on purpose. */

  int* hhead = h->head;
  unsigned short* hprev = h->prev;
  int* hhashval = h->hashval;
  int hval = h->val;

#ifdef ZOPFLI_LONGEST_MATCH_CACHE
  if (TryGetFromLongestMatchCache(s, pos, &limit, sublen, distance, length)) {
    assert(pos + *length <= size);
    return;
  }
#endif

  assert(limit <= ZOPFLI_MAX_MATCH);
  assert(limit >= ZOPFLI_MIN_MATCH);
  assert(pos < size);

  if (size - pos < ZOPFLI_MIN_MATCH) {
    /* The rest of the code assumes there are at least ZOPFLI_MIN_MATCH bytes to
       try. */
    *length = 0;
    *distance = 0;
    return;
  }

  if (pos + limit > size) {
    limit = size - pos;
  }
  arrayend = &array[pos] + limit;
  arrayend_safe = arrayend - 8;

  assert(hval < 65536);

  pp = hhead[hval];  /* During the whole loop, p == hprev[pp]. */
  p = hprev[pp];

  assert(pp == hpos);

  dist = p < pp ? pp - p : ((ZOPFLI_WINDOW_SIZE - p) + pp);

  /* Go through all distances. */
  while (dist < ZOPFLI_WINDOW_SIZE) {
    unsigned short currentlength = 0;

    assert(p < ZOPFLI_WINDOW_SIZE);
    assert(p == hprev[pp]);
    assert(hhashval[p] == hval);

    if (dist > 0) {
      assert(pos < size);
      assert(dist <= pos);
      scan = &array[pos];
      match = &array[pos - dist];

      /* Testing the byte at position bestlength first, goes slightly faster. */
      if (pos + bestlength >= size
          || *(scan + bestlength) == *(match + bestlength)) {

#ifdef ZOPFLI_HASH_SAME
        unsigned short same0 = h->same[pos & ZOPFLI_WINDOW_MASK];
        if (same0 > 2 && *scan == *match) {
          unsigned short same1 = h->same[(pos - dist) & ZOPFLI_WINDOW_MASK];
          unsigned short same = same0 < same1 ? same0 : same1;
          if (same > limit) same = limit;
          scan += same;
          match += same;
        }
#endif
        scan = GetMatch(scan, match, arrayend, arrayend_safe);
        currentlength = scan - &array[pos];  /* The found length. */
      }

      if (currentlength > bestlength) {
        if (sublen) {
          unsigned short j;
          for (j = bestlength + 1; j <= currentlength; j++) {
            sublen[j] = dist;
          }
        }
        bestdist = dist;
        bestlength = currentlength;
        if (currentlength >= limit) break;
      }
    }


#ifdef ZOPFLI_HASH_SAME_HASH
    /* Switch to the other hash once this will be more efficient. */
    if (hhead != h->head2 && bestlength >= h->same[hpos] &&
        h->val2 == h->hashval2[p]) {
      /* Now use the hash that encodes the length and first byte. */
      hhead = h->head2;
      hprev = h->prev2;
      hhashval = h->hashval2;
      hval = h->val2;
    }
#endif

    pp = p;
    p = hprev[p];
    if (p == pp) break;  /* Uninited prev value. */

    dist += p < pp ? pp - p : ((ZOPFLI_WINDOW_SIZE - p) + pp);

#if ZOPFLI_MAX_CHAIN_HITS < ZOPFLI_WINDOW_SIZE
    chain_counter--;
    if (chain_counter <= 0) break;
#endif
  }

#ifdef ZOPFLI_LONGEST_MATCH_CACHE
  StoreInLongestMatchCache(s, pos, limit, sublen, bestdist, bestlength);
#endif

  assert(bestlength <= limit);

  *distance = bestdist;
  *length = bestlength;
  assert(pos + *length <= size);
}

void ZopfliLZ77Greedy(ZopfliBlockState* s, const unsigned char* in,
                      size_t instart, size_t inend,
                      ZopfliLZ77Store* store, ZopfliHash* h) {
  size_t i = 0, j;
  unsigned short leng;
  unsigned short dist;
  int lengthscore;
  size_t windowstart = instart > ZOPFLI_WINDOW_SIZE
      ? instart - ZOPFLI_WINDOW_SIZE : 0;
  unsigned short dummysublen[259];

#ifdef ZOPFLI_LAZY_MATCHING
  /* Lazy matching. */
  unsigned prev_length = 0;
  unsigned prev_match = 0;
  int prevlengthscore;
  int match_available = 0;
#endif

  if (instart == inend) return;

  ZopfliResetHash(ZOPFLI_WINDOW_SIZE, h);
  ZopfliWarmupHash(in, windowstart, inend, h);
  for (i = windowstart; i < instart; i++) {
    ZopfliUpdateHash(in, i, inend, h);
  }

  for (i = instart; i < inend; i++) {
    ZopfliUpdateHash(in, i, inend, h);

    ZopfliFindLongestMatch(s, h, in, i, inend, ZOPFLI_MAX_MATCH, dummysublen,
                           &dist, &leng);
    lengthscore = GetLengthScore(leng, dist);

#ifdef ZOPFLI_LAZY_MATCHING
    /* Lazy matching. */
    prevlengthscore = GetLengthScore(prev_length, prev_match);
    if (match_available) {
      match_available = 0;
      if (lengthscore > prevlengthscore + 1) {
        ZopfliStoreLitLenDist(in[i - 1], 0, i - 1, store);
        if (lengthscore >= ZOPFLI_MIN_MATCH && leng < ZOPFLI_MAX_MATCH) {
          match_available = 1;
          prev_length = leng;
          prev_match = dist;
          continue;
        }
      } else {
        /* Add previous to output. */
        leng = prev_length;
        dist = prev_match;
        lengthscore = prevlengthscore;
        /* Add to output. */
        ZopfliVerifyLenDist(in, inend, i - 1, dist, leng);
        ZopfliStoreLitLenDist(leng, dist, i - 1, store);
        for (j = 2; j < leng; j++) {
          assert(i < inend);
          i++;
          ZopfliUpdateHash(in, i, inend, h);
        }
        continue;
      }
    }
    else if (lengthscore >= ZOPFLI_MIN_MATCH && leng < ZOPFLI_MAX_MATCH) {
      match_available = 1;
      prev_length = leng;
      prev_match = dist;
      continue;
    }
    /* End of lazy matching. */
#endif

    /* Add to output. */
    if (lengthscore >= ZOPFLI_MIN_MATCH) {
      ZopfliVerifyLenDist(in, inend, i, dist, leng);
      ZopfliStoreLitLenDist(leng, dist, i, store);
    } else {
      leng = 1;
      ZopfliStoreLitLenDist(in[i], 0, i, store);
    }
    for (j = 1; j < leng; j++) {
      assert(i < inend);
      i++;
      ZopfliUpdateHash(in, i, inend, h);
    }
  }
}
