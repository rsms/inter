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

#include "deflate.h"

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#include "blocksplitter.h"
#include "squeeze.h"
#include "symbols.h"
#include "tree.h"

/*
bp = bitpointer, always in range [0, 7].
The outsize is number of necessary bytes to encode the bits.
Given the value of bp and the amount of bytes, the amount of bits represented
is not simply bytesize * 8 + bp because even representing one bit requires a
whole byte. It is: (bp == 0) ? (bytesize * 8) : ((bytesize - 1) * 8 + bp)
*/
static void AddBit(int bit,
                   unsigned char* bp, unsigned char** out, size_t* outsize) {
  if (*bp == 0) ZOPFLI_APPEND_DATA(0, out, outsize);
  (*out)[*outsize - 1] |= bit << *bp;
  *bp = (*bp + 1) & 7;
}

static void AddBits(unsigned symbol, unsigned length,
                    unsigned char* bp, unsigned char** out, size_t* outsize) {
  /* TODO(lode): make more efficient (add more bits at once). */
  unsigned i;
  for (i = 0; i < length; i++) {
    unsigned bit = (symbol >> i) & 1;
    if (*bp == 0) ZOPFLI_APPEND_DATA(0, out, outsize);
    (*out)[*outsize - 1] |= bit << *bp;
    *bp = (*bp + 1) & 7;
  }
}

/*
Adds bits, like AddBits, but the order is inverted. The deflate specification
uses both orders in one standard.
*/
static void AddHuffmanBits(unsigned symbol, unsigned length,
                           unsigned char* bp, unsigned char** out,
                           size_t* outsize) {
  /* TODO(lode): make more efficient (add more bits at once). */
  unsigned i;
  for (i = 0; i < length; i++) {
    unsigned bit = (symbol >> (length - i - 1)) & 1;
    if (*bp == 0) ZOPFLI_APPEND_DATA(0, out, outsize);
    (*out)[*outsize - 1] |= bit << *bp;
    *bp = (*bp + 1) & 7;
  }
}

/*
Ensures there are at least 2 distance codes to support buggy decoders.
Zlib 1.2.1 and below have a bug where it fails if there isn't at least 1
distance code (with length > 0), even though it's valid according to the
deflate spec to have 0 distance codes. On top of that, some mobile phones
require at least two distance codes. To support these decoders too (but
potentially at the cost of a few bytes), add dummy code lengths of 1.
References to this bug can be found in the changelog of
Zlib 1.2.2 and here: http://www.jonof.id.au/forum/index.php?topic=515.0.

d_lengths: the 32 lengths of the distance codes.
*/
static void PatchDistanceCodesForBuggyDecoders(unsigned* d_lengths) {
#if 0
  int num_dist_codes = 0; /* Amount of non-zero distance codes */
  int i;
  for (i = 0; i < 30 /* Ignore the two unused codes from the spec */; i++) {
    if (d_lengths[i]) num_dist_codes++;
    if (num_dist_codes >= 2) return; /* Two or more codes is fine. */
  }

  if (num_dist_codes == 0) {
    d_lengths[0] = d_lengths[1] = 1;
  } else if (num_dist_codes == 1) {
    d_lengths[d_lengths[0] ? 1 : 0] = 1;
  }
#endif
}

/*
Encodes the Huffman tree and returns how many bits its encoding takes. If out
is a null pointer, only returns the size and runs faster.
*/
static size_t EncodeTree(const unsigned* ll_lengths,
                         const unsigned* d_lengths,
                         int use_16, int use_17, int use_18,
                         unsigned char* bp,
                         unsigned char** out, size_t* outsize) {
  unsigned lld_total;  /* Total amount of literal, length, distance codes. */
  /* Runlength encoded version of lengths of litlen and dist trees. */
  unsigned* rle = 0;
  unsigned* rle_bits = 0;  /* Extra bits for rle values 16, 17 and 18. */
  size_t rle_size = 0;  /* Size of rle array. */
  size_t rle_bits_size = 0;  /* Should have same value as rle_size. */
  unsigned hlit = 29;  /* 286 - 257 */
  unsigned hdist = 29;  /* 32 - 1, but gzip does not like hdist > 29.*/
  unsigned hclen;
  unsigned hlit2;
  size_t i, j;
  size_t clcounts[19];
  unsigned clcl[19];  /* Code length code lengths. */
  unsigned clsymbols[19];
  /* The order in which code length code lengths are encoded as per deflate. */
  static const unsigned order[19] = {
    16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15
  };
  int size_only = !out;
  size_t result_size = 0;

  for(i = 0; i < 19; i++) clcounts[i] = 0;

  /* Trim zeros. */
  while (hlit > 0 && ll_lengths[257 + hlit - 1] == 0) hlit--;
  while (hdist > 0 && d_lengths[1 + hdist - 1] == 0) hdist--;
  hlit2 = hlit + 257;

  lld_total = hlit2 + hdist + 1;

  for (i = 0; i < lld_total; i++) {
    /* This is an encoding of a huffman tree, so now the length is a symbol */
    unsigned char symbol = i < hlit2 ? ll_lengths[i] : d_lengths[i - hlit2];
    unsigned count = 1;
    if(use_16 || (symbol == 0 && (use_17 || use_18))) {
      for (j = i + 1; j < lld_total && symbol ==
          (j < hlit2 ? ll_lengths[j] : d_lengths[j - hlit2]); j++) {
        count++;
      }
    }
    i += count - 1;

    /* Repetitions of zeroes */
    if (symbol == 0 && count >= 3) {
      if (use_18) {
        while (count >= 11) {
          unsigned count2 = count > 138 ? 138 : count;
          if (!size_only) {
            ZOPFLI_APPEND_DATA(18, &rle, &rle_size);
            ZOPFLI_APPEND_DATA(count2 - 11, &rle_bits, &rle_bits_size);
          }
          clcounts[18]++;
          count -= count2;
        }
      }
      if (use_17) {
        while (count >= 3) {
          unsigned count2 = count > 10 ? 10 : count;
          if (!size_only) {
            ZOPFLI_APPEND_DATA(17, &rle, &rle_size);
            ZOPFLI_APPEND_DATA(count2 - 3, &rle_bits, &rle_bits_size);
          }
          clcounts[17]++;
          count -= count2;
        }
      }
    }

    /* Repetitions of any symbol */
    if (use_16 && count >= 4) {
      count--;  /* Since the first one is hardcoded. */
      clcounts[symbol]++;
      if (!size_only) {
        ZOPFLI_APPEND_DATA(symbol, &rle, &rle_size);
        ZOPFLI_APPEND_DATA(0, &rle_bits, &rle_bits_size);
      }
      while (count >= 3) {
        unsigned count2 = count > 6 ? 6 : count;
        if (!size_only) {
          ZOPFLI_APPEND_DATA(16, &rle, &rle_size);
          ZOPFLI_APPEND_DATA(count2 - 3, &rle_bits, &rle_bits_size);
        }
        clcounts[16]++;
        count -= count2;
      }
    }

    /* No or insufficient repetition */
    clcounts[symbol] += count;
    while (count > 0) {
      if (!size_only) {
        ZOPFLI_APPEND_DATA(symbol, &rle, &rle_size);
        ZOPFLI_APPEND_DATA(0, &rle_bits, &rle_bits_size);
      }
      count--;
    }
  }

  ZopfliCalculateBitLengths(clcounts, 19, 7, clcl);
  if (!size_only) ZopfliLengthsToSymbols(clcl, 19, 7, clsymbols);

  hclen = 15;
  /* Trim zeros. */
  while (hclen > 0 && clcounts[order[hclen + 4 - 1]] == 0) hclen--;

  if (!size_only) {
    AddBits(hlit, 5, bp, out, outsize);
    AddBits(hdist, 5, bp, out, outsize);
    AddBits(hclen, 4, bp, out, outsize);

    for (i = 0; i < hclen + 4; i++) {
      AddBits(clcl[order[i]], 3, bp, out, outsize);
    }

    for (i = 0; i < rle_size; i++) {
      unsigned symbol = clsymbols[rle[i]];
      AddHuffmanBits(symbol, clcl[rle[i]], bp, out, outsize);
      /* Extra bits. */
      if (rle[i] == 16) AddBits(rle_bits[i], 2, bp, out, outsize);
      else if (rle[i] == 17) AddBits(rle_bits[i], 3, bp, out, outsize);
      else if (rle[i] == 18) AddBits(rle_bits[i], 7, bp, out, outsize);
    }
  }

  result_size += 14;  /* hlit, hdist, hclen bits */
  result_size += (hclen + 4) * 3;  /* clcl bits */
  for(i = 0; i < 19; i++) {
    result_size += clcl[i] * clcounts[i];
  }
  /* Extra bits. */
  result_size += clcounts[16] * 2;
  result_size += clcounts[17] * 3;
  result_size += clcounts[18] * 7;

  /* Note: in case of "size_only" these are null pointers so no effect. */
  free(rle);
  free(rle_bits);

  return result_size;
}

static void AddDynamicTree(const unsigned* ll_lengths,
                           const unsigned* d_lengths,
                           unsigned char* bp,
                           unsigned char** out, size_t* outsize) {
  int i;
  int best = 0;
  size_t bestsize = 0;

  for(i = 0; i < 8; i++) {
    size_t size = EncodeTree(ll_lengths, d_lengths,
                             i & 1, i & 2, i & 4,
                             0, 0, 0);
    if (bestsize == 0 || size < bestsize) {
      bestsize = size;
      best = i;
    }
  }

  EncodeTree(ll_lengths, d_lengths,
             best & 1, best & 2, best & 4,
             bp, out, outsize);
}

/*
Gives the exact size of the tree, in bits, as it will be encoded in DEFLATE.
*/
static size_t CalculateTreeSize(const unsigned* ll_lengths,
                                const unsigned* d_lengths) {
  size_t result = 0;
  int i;

  for(i = 0; i < 8; i++) {
    size_t size = EncodeTree(ll_lengths, d_lengths,
                             i & 1, i & 2, i & 4,
                             0, 0, 0);
    if (result == 0 || size < result) result = size;
  }

  return result;
}

/*
Adds all lit/len and dist codes from the lists as huffman symbols. Does not add
end code 256. expected_data_size is the uncompressed block size, used for
assert, but you can set it to 0 to not do the assertion.
*/
static void AddLZ77Data(const ZopfliLZ77Store* lz77,
                        size_t lstart, size_t lend,
                        size_t expected_data_size,
                        const unsigned* ll_symbols, const unsigned* ll_lengths,
                        const unsigned* d_symbols, const unsigned* d_lengths,
                        unsigned char* bp,
                        unsigned char** out, size_t* outsize) {
  size_t testlength = 0;
  size_t i;

  for (i = lstart; i < lend; i++) {
    unsigned dist = lz77->dists[i];
    unsigned litlen = lz77->litlens[i];
    if (dist == 0) {
      assert(litlen < 256);
      assert(ll_lengths[litlen] > 0);
      AddHuffmanBits(ll_symbols[litlen], ll_lengths[litlen], bp, out, outsize);
      testlength++;
    } else {
      unsigned lls = ZopfliGetLengthSymbol(litlen);
      unsigned ds = ZopfliGetDistSymbol(dist);
      assert(litlen >= 3 && litlen <= 288);
      assert(ll_lengths[lls] > 0);
      assert(d_lengths[ds] > 0);
      AddHuffmanBits(ll_symbols[lls], ll_lengths[lls], bp, out, outsize);
      AddBits(ZopfliGetLengthExtraBitsValue(litlen),
              ZopfliGetLengthExtraBits(litlen),
              bp, out, outsize);
      AddHuffmanBits(d_symbols[ds], d_lengths[ds], bp, out, outsize);
      AddBits(ZopfliGetDistExtraBitsValue(dist),
              ZopfliGetDistExtraBits(dist),
              bp, out, outsize);
      testlength += litlen;
    }
  }
  assert(expected_data_size == 0 || testlength == expected_data_size);
}

static void GetFixedTree(unsigned* ll_lengths, unsigned* d_lengths) {
  size_t i;
  for (i = 0; i < 144; i++) ll_lengths[i] = 8;
  for (i = 144; i < 256; i++) ll_lengths[i] = 9;
  for (i = 256; i < 280; i++) ll_lengths[i] = 7;
  for (i = 280; i < 288; i++) ll_lengths[i] = 8;
  for (i = 0; i < 32; i++) d_lengths[i] = 5;
}

/*
Same as CalculateBlockSymbolSize, but for block size smaller than histogram
size.
*/
static size_t CalculateBlockSymbolSizeSmall(const unsigned* ll_lengths,
                                            const unsigned* d_lengths,
                                            const ZopfliLZ77Store* lz77,
                                            size_t lstart, size_t lend) {
  size_t result = 0;
  size_t i;
  for (i = lstart; i < lend; i++) {
    assert(i < lz77->size);
    assert(lz77->litlens[i] < 259);
    if (lz77->dists[i] == 0) {
      result += ll_lengths[lz77->litlens[i]];
    } else {
      int ll_symbol = ZopfliGetLengthSymbol(lz77->litlens[i]);
      int d_symbol = ZopfliGetDistSymbol(lz77->dists[i]);
      result += ll_lengths[ll_symbol];
      result += d_lengths[d_symbol];
      result += ZopfliGetLengthSymbolExtraBits(ll_symbol);
      result += ZopfliGetDistSymbolExtraBits(d_symbol);
    }
  }
  result += ll_lengths[256]; /*end symbol*/
  return result;
}

/*
Same as CalculateBlockSymbolSize, but with the histogram provided by the caller.
*/
static size_t CalculateBlockSymbolSizeGivenCounts(const size_t* ll_counts,
                                                  const size_t* d_counts,
                                                  const unsigned* ll_lengths,
                                                  const unsigned* d_lengths,
                                                  const ZopfliLZ77Store* lz77,
                                                  size_t lstart, size_t lend) {
  size_t result = 0;
  size_t i;
  if (lstart + ZOPFLI_NUM_LL * 3 > lend) {
    return CalculateBlockSymbolSizeSmall(
        ll_lengths, d_lengths, lz77, lstart, lend);
  } else {
    for (i = 0; i < 256; i++) {
      result += ll_lengths[i] * ll_counts[i];
    }
    for (i = 257; i < 286; i++) {
      result += ll_lengths[i] * ll_counts[i];
      result += ZopfliGetLengthSymbolExtraBits(i) * ll_counts[i];
    }
    for (i = 0; i < 30; i++) {
      result += d_lengths[i] * d_counts[i];
      result += ZopfliGetDistSymbolExtraBits(i) * d_counts[i];
    }
    result += ll_lengths[256]; /*end symbol*/
    return result;
  }
}

/*
Calculates size of the part after the header and tree of an LZ77 block, in bits.
*/
static size_t CalculateBlockSymbolSize(const unsigned* ll_lengths,
                                       const unsigned* d_lengths,
                                       const ZopfliLZ77Store* lz77,
                                       size_t lstart, size_t lend) {
  if (lstart + ZOPFLI_NUM_LL * 3 > lend) {
    return CalculateBlockSymbolSizeSmall(
        ll_lengths, d_lengths, lz77, lstart, lend);
  } else {
    size_t ll_counts[ZOPFLI_NUM_LL];
    size_t d_counts[ZOPFLI_NUM_D];
    ZopfliLZ77GetHistogram(lz77, lstart, lend, ll_counts, d_counts);
    return CalculateBlockSymbolSizeGivenCounts(
        ll_counts, d_counts, ll_lengths, d_lengths, lz77, lstart, lend);
  }
}

static size_t AbsDiff(size_t x, size_t y) {
  if (x > y)
    return x - y;
  else
    return y - x;
}

/*
Changes the population counts in a way that the consequent Huffman tree
compression, especially its rle-part, will be more likely to compress this data
more efficiently. length contains the size of the histogram.
*/
void OptimizeHuffmanForRle(int length, size_t* counts) {
  int i, k, stride;
  size_t symbol, sum, limit;
  int* good_for_rle;

  /* 1) We don't want to touch the trailing zeros. We may break the
  rules of the format by adding more data in the distance codes. */
  for (; length >= 0; --length) {
    if (length == 0) {
      return;
    }
    if (counts[length - 1] != 0) {
      /* Now counts[0..length - 1] does not have trailing zeros. */
      break;
    }
  }
  /* 2) Let's mark all population counts that already can be encoded
  with an rle code.*/
  good_for_rle = (int*)malloc(length * sizeof(int));
  for (i = 0; i < length; ++i) good_for_rle[i] = 0;

  /* Let's not spoil any of the existing good rle codes.
  Mark any seq of 0's that is longer than 5 as a good_for_rle.
  Mark any seq of non-0's that is longer than 7 as a good_for_rle.*/
  symbol = counts[0];
  stride = 0;
  for (i = 0; i < length + 1; ++i) {
    if (i == length || counts[i] != symbol) {
      if ((symbol == 0 && stride >= 5) || (symbol != 0 && stride >= 7)) {
        for (k = 0; k < stride; ++k) {
          good_for_rle[i - k - 1] = 1;
        }
      }
      stride = 1;
      if (i != length) {
        symbol = counts[i];
      }
    } else {
      ++stride;
    }
  }

  /* 3) Let's replace those population counts that lead to more rle codes. */
  stride = 0;
  limit = counts[0];
  sum = 0;
  for (i = 0; i < length + 1; ++i) {
    if (i == length || good_for_rle[i]
        /* Heuristic for selecting the stride ranges to collapse. */
        || AbsDiff(counts[i], limit) >= 4) {
      if (stride >= 4 || (stride >= 3 && sum == 0)) {
        /* The stride must end, collapse what we have, if we have enough (4). */
        int count = (sum + stride / 2) / stride;
        if (count < 1) count = 1;
        if (sum == 0) {
          /* Don't make an all zeros stride to be upgraded to ones. */
          count = 0;
        }
        for (k = 0; k < stride; ++k) {
          /* We don't want to change value at counts[i],
          that is already belonging to the next stride. Thus - 1. */
          counts[i - k - 1] = count;
        }
      }
      stride = 0;
      sum = 0;
      if (i < length - 3) {
        /* All interesting strides have a count of at least 4,
        at least when non-zeros. */
        limit = (counts[i] + counts[i + 1] +
                 counts[i + 2] + counts[i + 3] + 2) / 4;
      } else if (i < length) {
        limit = counts[i];
      } else {
        limit = 0;
      }
    }
    ++stride;
    if (i != length) {
      sum += counts[i];
    }
  }

  free(good_for_rle);
}

/*
Tries out OptimizeHuffmanForRle for this block, if the result is smaller,
uses it, otherwise keeps the original. Returns size of encoded tree and data in
bits, not including the 3-bit block header.
*/
static double TryOptimizeHuffmanForRle(
    const ZopfliLZ77Store* lz77, size_t lstart, size_t lend,
    const size_t* ll_counts, const size_t* d_counts,
    unsigned* ll_lengths, unsigned* d_lengths) {
  size_t ll_counts2[ZOPFLI_NUM_LL];
  size_t d_counts2[ZOPFLI_NUM_D];
  unsigned ll_lengths2[ZOPFLI_NUM_LL];
  unsigned d_lengths2[ZOPFLI_NUM_D];
  double treesize;
  double datasize;
  double treesize2;
  double datasize2;

  treesize = CalculateTreeSize(ll_lengths, d_lengths);
  datasize = CalculateBlockSymbolSizeGivenCounts(ll_counts, d_counts,
      ll_lengths, d_lengths, lz77, lstart, lend);

  memcpy(ll_counts2, ll_counts, sizeof(ll_counts2));
  memcpy(d_counts2, d_counts, sizeof(d_counts2));
  OptimizeHuffmanForRle(ZOPFLI_NUM_LL, ll_counts2);
  OptimizeHuffmanForRle(ZOPFLI_NUM_D, d_counts2);
  ZopfliCalculateBitLengths(ll_counts2, ZOPFLI_NUM_LL, 15, ll_lengths2);
  ZopfliCalculateBitLengths(d_counts2, ZOPFLI_NUM_D, 15, d_lengths2);
  PatchDistanceCodesForBuggyDecoders(d_lengths2);

  treesize2 = CalculateTreeSize(ll_lengths2, d_lengths2);
  datasize2 = CalculateBlockSymbolSizeGivenCounts(ll_counts, d_counts,
      ll_lengths2, d_lengths2, lz77, lstart, lend);

  if (treesize2 + datasize2 < treesize + datasize) {
    memcpy(ll_lengths, ll_lengths2, sizeof(ll_lengths2));
    memcpy(d_lengths, d_lengths2, sizeof(d_lengths2));
    return treesize2 + datasize2;
  }
  return treesize + datasize;
}

/*
Calculates the bit lengths for the symbols for dynamic blocks. Chooses bit
lengths that give the smallest size of tree encoding + encoding of all the
symbols to have smallest output size. This are not necessarily the ideal Huffman
bit lengths. Returns size of encoded tree and data in bits, not including the
3-bit block header.
*/
static double GetDynamicLengths(const ZopfliLZ77Store* lz77,
                                size_t lstart, size_t lend,
                                unsigned* ll_lengths, unsigned* d_lengths) {
  size_t ll_counts[ZOPFLI_NUM_LL];
  size_t d_counts[ZOPFLI_NUM_D];

  ZopfliLZ77GetHistogram(lz77, lstart, lend, ll_counts, d_counts);
  ll_counts[256] = 1;  /* End symbol. */
  ZopfliCalculateBitLengths(ll_counts, ZOPFLI_NUM_LL, 15, ll_lengths);
  ZopfliCalculateBitLengths(d_counts, ZOPFLI_NUM_D, 15, d_lengths);
  PatchDistanceCodesForBuggyDecoders(d_lengths);
  return TryOptimizeHuffmanForRle(
      lz77, lstart, lend, ll_counts, d_counts, ll_lengths, d_lengths);
}

double ZopfliCalculateBlockSize(const ZopfliLZ77Store* lz77,
                                size_t lstart, size_t lend, int btype) {
  unsigned ll_lengths[ZOPFLI_NUM_LL];
  unsigned d_lengths[ZOPFLI_NUM_D];

  double result = 3; /* bfinal and btype bits */

  if (btype == 0) {
    size_t length = ZopfliLZ77GetByteRange(lz77, lstart, lend);
    size_t rem = length % 65535;
    size_t blocks = length / 65535 + (rem ? 1 : 0);
    /* An uncompressed block must actually be split into multiple blocks if it's
       larger than 65535 bytes long. Eeach block header is 5 bytes: 3 bits,
       padding, LEN and NLEN (potential less padding for first one ignored). */
    return blocks * 5 * 8 + length * 8;
  } if (btype == 1) {
    GetFixedTree(ll_lengths, d_lengths);
    result += CalculateBlockSymbolSize(
        ll_lengths, d_lengths, lz77, lstart, lend);
  } else {
    result += GetDynamicLengths(lz77, lstart, lend, ll_lengths, d_lengths);
  }

  return result;
}

double ZopfliCalculateBlockSizeAutoType(const ZopfliLZ77Store* lz77,
                                        size_t lstart, size_t lend) {
  double uncompressedcost = ZopfliCalculateBlockSize(lz77, lstart, lend, 0);
  /* Don't do the expensive fixed cost calculation for larger blocks that are
     unlikely to use it. */
  double fixedcost = (lz77->size > 1000) ?
      uncompressedcost : ZopfliCalculateBlockSize(lz77, lstart, lend, 1);
  double dyncost = ZopfliCalculateBlockSize(lz77, lstart, lend, 2);
  return (uncompressedcost < fixedcost && uncompressedcost < dyncost)
      ? uncompressedcost
      : (fixedcost < dyncost ? fixedcost : dyncost);
}

/* Since an uncompressed block can be max 65535 in size, it actually adds
multible blocks if needed. */
static void AddNonCompressedBlock(const ZopfliOptions* options, int final,
                                  const unsigned char* in, size_t instart,
                                  size_t inend,
                                  unsigned char* bp,
                                  unsigned char** out, size_t* outsize) {
  size_t pos = instart;
  (void)options;
  for (;;) {
    size_t i;
    unsigned short blocksize = 65535;
    unsigned short nlen;
    int currentfinal;

    if (pos + blocksize > inend) blocksize = inend - pos;
    currentfinal = pos + blocksize >= inend;

    nlen = ~blocksize;

    AddBit(final && currentfinal, bp, out, outsize);
    /* BTYPE 00 */
    AddBit(0, bp, out, outsize);
    AddBit(0, bp, out, outsize);

    /* Any bits of input up to the next byte boundary are ignored. */
    *bp = 0;

    ZOPFLI_APPEND_DATA(blocksize % 256, out, outsize);
    ZOPFLI_APPEND_DATA((blocksize / 256) % 256, out, outsize);
    ZOPFLI_APPEND_DATA(nlen % 256, out, outsize);
    ZOPFLI_APPEND_DATA((nlen / 256) % 256, out, outsize);

    for (i = 0; i < blocksize; i++) {
      ZOPFLI_APPEND_DATA(in[pos + i], out, outsize);
    }

    if (currentfinal) break;
    pos += blocksize;
  }
}

/*
Adds a deflate block with the given LZ77 data to the output.
options: global program options
btype: the block type, must be 1 or 2
final: whether to set the "final" bit on this block, must be the last block
litlens: literal/length array of the LZ77 data, in the same format as in
    ZopfliLZ77Store.
dists: distance array of the LZ77 data, in the same format as in
    ZopfliLZ77Store.
lstart: where to start in the LZ77 data
lend: where to end in the LZ77 data (not inclusive)
expected_data_size: the uncompressed block size, used for assert, but you can
  set it to 0 to not do the assertion.
bp: output bit pointer
out: dynamic output array to append to
outsize: dynamic output array size
*/
static void AddLZ77Block(const ZopfliOptions* options, int btype, int final,
                         const ZopfliLZ77Store* lz77,
                         size_t lstart, size_t lend,
                         size_t expected_data_size,
                         unsigned char* bp,
                         unsigned char** out, size_t* outsize) {
  unsigned ll_lengths[ZOPFLI_NUM_LL];
  unsigned d_lengths[ZOPFLI_NUM_D];
  unsigned ll_symbols[ZOPFLI_NUM_LL];
  unsigned d_symbols[ZOPFLI_NUM_D];
  size_t detect_block_size = *outsize;
  size_t compressed_size;
  size_t uncompressed_size = 0;
  size_t i;
  if (btype == 0) {
    size_t length = ZopfliLZ77GetByteRange(lz77, lstart, lend);
    size_t pos = lstart == lend ? 0 : lz77->pos[lstart];
    size_t end = pos + length;
    AddNonCompressedBlock(options, final,
                          lz77->data, pos, end, bp, out, outsize);
    return;
  }

  AddBit(final, bp, out, outsize);
  AddBit(btype & 1, bp, out, outsize);
  AddBit((btype & 2) >> 1, bp, out, outsize);

  if (btype == 1) {
    /* Fixed block. */
    GetFixedTree(ll_lengths, d_lengths);
  } else {
    /* Dynamic block. */
    unsigned detect_tree_size;
    assert(btype == 2);

    GetDynamicLengths(lz77, lstart, lend, ll_lengths, d_lengths);

    detect_tree_size = *outsize;
    AddDynamicTree(ll_lengths, d_lengths, bp, out, outsize);
    if (options->verbose) {
      fprintf(stderr, "treesize: %d\n", (int)(*outsize - detect_tree_size));
    }
  }

  ZopfliLengthsToSymbols(ll_lengths, ZOPFLI_NUM_LL, 15, ll_symbols);
  ZopfliLengthsToSymbols(d_lengths, ZOPFLI_NUM_D, 15, d_symbols);

  detect_block_size = *outsize;
  AddLZ77Data(lz77, lstart, lend, expected_data_size,
              ll_symbols, ll_lengths, d_symbols, d_lengths,
              bp, out, outsize);
  /* End symbol. */
  AddHuffmanBits(ll_symbols[256], ll_lengths[256], bp, out, outsize);

  for (i = lstart; i < lend; i++) {
    uncompressed_size += lz77->dists[i] == 0 ? 1 : lz77->litlens[i];
  }
  compressed_size = *outsize - detect_block_size;
  if (options->verbose) {
    fprintf(stderr, "compressed block size: %d (%dk) (unc: %d)\n",
           (int)compressed_size, (int)(compressed_size / 1024),
           (int)(uncompressed_size));
  }
}

static void AddLZ77BlockAutoType(const ZopfliOptions* options, int final,
                                 const ZopfliLZ77Store* lz77,
                                 size_t lstart, size_t lend,
                                 size_t expected_data_size,
                                 unsigned char* bp,
                                 unsigned char** out, size_t* outsize) {
  double uncompressedcost = ZopfliCalculateBlockSize(lz77, lstart, lend, 0);
  double fixedcost = ZopfliCalculateBlockSize(lz77, lstart, lend, 1);
  double dyncost = ZopfliCalculateBlockSize(lz77, lstart, lend, 2);

  /* Whether to perform the expensive calculation of creating an optimal block
  with fixed huffman tree to check if smaller. Only do this for small blocks or
  blocks which already are pretty good with fixed huffman tree. */
  int expensivefixed = (lz77->size < 1000) || fixedcost <= dyncost * 1.1;

  ZopfliLZ77Store fixedstore;
  if (lstart == lend) {
    /* Smallest empty block is represented by fixed block */
    AddBits(final, 1, bp, out, outsize);
    AddBits(1, 2, bp, out, outsize);  /* btype 01 */
    AddBits(0, 7, bp, out, outsize);  /* end symbol has code 0000000 */
    return;
  }
  ZopfliInitLZ77Store(lz77->data, &fixedstore);
  if (expensivefixed) {
    /* Recalculate the LZ77 with ZopfliLZ77OptimalFixed */
    size_t instart = lz77->pos[lstart];
    size_t inend = instart + ZopfliLZ77GetByteRange(lz77, lstart, lend);

    ZopfliBlockState s;
    ZopfliInitBlockState(options, instart, inend, 1, &s);
    ZopfliLZ77OptimalFixed(&s, lz77->data, instart, inend, &fixedstore);
    fixedcost = ZopfliCalculateBlockSize(&fixedstore, 0, fixedstore.size, 1);
    ZopfliCleanBlockState(&s);
  }

  if (uncompressedcost < fixedcost && uncompressedcost < dyncost) {
    AddLZ77Block(options, 0, final, lz77, lstart, lend,
                 expected_data_size, bp, out, outsize);
  } else if (fixedcost < dyncost) {
    if (expensivefixed) {
      AddLZ77Block(options, 1, final, &fixedstore, 0, fixedstore.size,
                   expected_data_size, bp, out, outsize);
    } else {
      AddLZ77Block(options, 1, final, lz77, lstart, lend,
                   expected_data_size, bp, out, outsize);
    }
  } else {
    AddLZ77Block(options, 2, final, lz77, lstart, lend,
                 expected_data_size, bp, out, outsize);
  }

  ZopfliCleanLZ77Store(&fixedstore);
}

/*
Deflate a part, to allow ZopfliDeflate() to use multiple master blocks if
needed.
It is possible to call this function multiple times in a row, shifting
instart and inend to next bytes of the data. If instart is larger than 0, then
previous bytes are used as the initial dictionary for LZ77.
This function will usually output multiple deflate blocks. If final is 1, then
the final bit will be set on the last block.
*/
void ZopfliDeflatePart(const ZopfliOptions* options, int btype, int final,
                       const unsigned char* in, size_t instart, size_t inend,
                       unsigned char* bp, unsigned char** out,
                       size_t* outsize) {
  size_t i;
  /* byte coordinates rather than lz77 index */
  size_t* splitpoints_uncompressed = 0;
  size_t npoints = 0;
  size_t* splitpoints = 0;
  double totalcost = 0;
  ZopfliLZ77Store lz77;

  /* If btype=2 is specified, it tries all block types. If a lesser btype is
  given, then however it forces that one. Neither of the lesser types needs
  block splitting as they have no dynamic huffman trees. */
  if (btype == 0) {
    AddNonCompressedBlock(options, final, in, instart, inend, bp, out, outsize);
    return;
  } else if (btype == 1) {
    ZopfliLZ77Store store;
    ZopfliBlockState s;
    ZopfliInitLZ77Store(in, &store);
    ZopfliInitBlockState(options, instart, inend, 1, &s);

    ZopfliLZ77OptimalFixed(&s, in, instart, inend, &store);
    AddLZ77Block(options, btype, final, &store, 0, store.size, 0,
                 bp, out, outsize);

    ZopfliCleanBlockState(&s);
    ZopfliCleanLZ77Store(&store);
    return;
  }


  if (options->blocksplitting) {
    ZopfliBlockSplit(options, in, instart, inend,
                     options->blocksplittingmax,
                     &splitpoints_uncompressed, &npoints);
    splitpoints = (size_t*)malloc(sizeof(*splitpoints) * npoints);
  }

  ZopfliInitLZ77Store(in, &lz77);

  for (i = 0; i <= npoints; i++) {
    size_t start = i == 0 ? instart : splitpoints_uncompressed[i - 1];
    size_t end = i == npoints ? inend : splitpoints_uncompressed[i];
    ZopfliBlockState s;
    ZopfliLZ77Store store;
    ZopfliInitLZ77Store(in, &store);
    ZopfliInitBlockState(options, start, end, 1, &s);
    ZopfliLZ77Optimal(&s, in, start, end, options->numiterations, &store);
    totalcost += ZopfliCalculateBlockSizeAutoType(&store, 0, store.size);

    ZopfliAppendLZ77Store(&store, &lz77);
    if (i < npoints) splitpoints[i] = lz77.size;

    ZopfliCleanBlockState(&s);
    ZopfliCleanLZ77Store(&store);
  }

  /* Second block splitting attempt */
  if (options->blocksplitting && npoints > 1) {
    size_t* splitpoints2 = 0;
    size_t npoints2 = 0;
    double totalcost2 = 0;

    ZopfliBlockSplitLZ77(options, &lz77,
                         options->blocksplittingmax, &splitpoints2, &npoints2);

    for (i = 0; i <= npoints2; i++) {
      size_t start = i == 0 ? 0 : splitpoints2[i - 1];
      size_t end = i == npoints2 ? lz77.size : splitpoints2[i];
      totalcost2 += ZopfliCalculateBlockSizeAutoType(&lz77, start, end);
    }

    if (totalcost2 < totalcost) {
      free(splitpoints);
      splitpoints = splitpoints2;
      npoints = npoints2;
    } else {
      free(splitpoints2);
    }
  }

  for (i = 0; i <= npoints; i++) {
    size_t start = i == 0 ? 0 : splitpoints[i - 1];
    size_t end = i == npoints ? lz77.size : splitpoints[i];
    AddLZ77BlockAutoType(options, i == npoints && final,
                         &lz77, start, end, 0,
                         bp, out, outsize);
  }

  ZopfliCleanLZ77Store(&lz77);
  free(splitpoints);
  free(splitpoints_uncompressed);
}

void ZopfliDeflate(const ZopfliOptions* options, int btype, int final,
                   const unsigned char* in, size_t insize,
                   unsigned char* bp, unsigned char** out, size_t* outsize) {
 size_t offset = *outsize;
#if ZOPFLI_MASTER_BLOCK_SIZE == 0
  ZopfliDeflatePart(options, btype, final, in, 0, insize, bp, out, outsize);
#else
  size_t i = 0;
  do {
    int masterfinal = (i + ZOPFLI_MASTER_BLOCK_SIZE >= insize);
    int final2 = final && masterfinal;
    size_t size = masterfinal ? insize - i : ZOPFLI_MASTER_BLOCK_SIZE;
    ZopfliDeflatePart(options, btype, final2,
                      in, i, i + size, bp, out, outsize);
    i += size;
  } while (i < insize);
#endif
  if (options->verbose) {
    fprintf(stderr,
            "Original Size: %lu, Deflate: %lu, Compression: %f%% Removed\n",
            (unsigned long)insize, (unsigned long)(*outsize - offset),
            100.0 * (double)(insize - (*outsize - offset)) / (double)insize);
  }
}
