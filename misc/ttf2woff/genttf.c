/*
 *	Copyright (C) 2013 Jan Bobrowski <jb@wizard.ae.krakow.pl>
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License
 *	version 2 as published by the Free Software Foundation.
 */

#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <assert.h>
#include "ttf2woff.h"

u8 *put_ttf_header(u8 buf[12], struct ttf *ttf)
{
	u8 *p = buf;
	int n = ttf->ntables;
	p = p32(p, ttf->flavor);
	p = p16(p, n);
	while(n & n-1) n &= n-1;
	p = p16(p, n<<4);
	p = p16(p, ffs(n)-1);
	p = p16(p, ttf->ntables-n << 4);
	return p;
}

void gen_ttf(struct buf *out, struct ttf *ttf)
{
	unsigned sfnt_size;
	u8 *buf, *p;
	int i;

	sfnt_size = 12 + 16*ttf->ntables;
	for(i=0; i<ttf->ntables; i++) {
		struct table *t = ttf->tab_pos[i];
		t->pos = sfnt_size; // remember offset in output file
		sfnt_size += t->buf.len+3 & ~3;
	}

	buf = my_alloc(sfnt_size);
	p = put_ttf_header(buf, ttf);

	for(i=0; i<ttf->ntables; i++) {
		struct table *t = &ttf->tables[i];
		p = p32(p, t->tag);
		p = p32(p, t->csum);
		p = p32(p, t->pos);
		p = p32(p, t->buf.len);
	}

	for(i=0; i<ttf->ntables; i++) {
		struct table *t = ttf->tab_pos[i];
		unsigned sz = t->buf.len;
		p = append(p, t->buf.ptr, sz);
		while(sz&3) *p++=0, sz++;
	}

	assert(p == buf+sfnt_size);

	out->ptr = buf;
	out->len = sfnt_size;
}
