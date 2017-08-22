/*
 *	Copyright (C) 2013 Jan Bobrowski <jb@wizard.ae.krakow.pl>
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License
 *	version 2 as published by the Free Software Foundation.
 */

#include <stdlib.h>
#include "ttf2woff.h"

#include "zopfli/zlib_container.c"
#include "zopfli/deflate.c"
#include "zopfli/lz77.c"
#include "zopfli/blocksplitter.c"
#include "zopfli/squeeze.c"
#include "zopfli/hash.c"
#include "zopfli/cache.c"
#include "zopfli/tree.c"
#include "zopfli/util.c"
#include "zopfli/katajainen.c"

#define adler32 zlib_adler32
#include <zlib.h>

char *copression_by = "zopfli";

int zlib_compress(struct buf *out, struct buf *inp)
{
	ZopfliOptions opt = {0};
	u8 *b=0;
	size_t sz=0;

	opt.numiterations = 15;
	ZopfliZlibCompress(&opt, inp->ptr, inp->len, &b, &sz);

	if(REALLY_SMALLER(sz, inp->len)) {

		/* Trust, but verify */
		uLong tmpl = inp->len;
		Bytef *tmpb = my_alloc(inp->len);
		int v = uncompress(tmpb, &tmpl, b, sz);
		if(v!=Z_OK || tmpl!=inp->len)
			errx(3,"Zopfli error");
		my_free(tmpb);

		out->ptr = b;
		out->len = sz;
		return 1;
	} else {
		free(b);
		return 0;
	}
}
