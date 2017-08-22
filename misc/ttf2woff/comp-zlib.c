/*
 *	Copyright (C) 2013 Jan Bobrowski <jb@wizard.ae.krakow.pl>
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License
 *	version 2 as published by the Free Software Foundation.
 */

#include <stdlib.h>
#include <zlib.h>
#include "ttf2woff.h"

char *copression_by = "zlib";

int zlib_compress(struct buf *out, struct buf *inp)
{
	u8 *b;
	int v;
	uLongf len;

	len = inp->len;
	b = my_alloc(inp->len);

	v = compress2(b,&len, inp->ptr,inp->len, 9);

	if(v==Z_OK && REALLY_SMALLER(len, inp->len)) {
		out->ptr = b;
		out->len = len;
		return 1;
	} else {
		my_free(b);
		return 0;
	}
}
