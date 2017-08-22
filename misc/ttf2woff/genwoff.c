/*
 *	Copyright (C) 2013 Jan Bobrowski <jb@wizard.ae.krakow.pl>
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License
 *	version 2 as published by the Free Software Foundation.
 */

#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "ttf2woff.h"

#define MIN_COMPR 16

void gen_woff(struct buf *out, struct ttf *ttf)
{
	unsigned woff_size, sfnt_size;
	struct buf meta_comp={0};
	u32 meta_off, priv_off;
	u8 *buf, *p;
	int i;

	woff_size = 44 + 20*ttf->ntables;
	sfnt_size = 12 + 16*ttf->ntables;
	for(i=0; i<ttf->ntables; i++) {
		struct table *t = ttf->tab_pos[i];
		t->pos = woff_size; // remember offset in output file
		t->zbuf = t->buf;
		if(t->buf.len >= MIN_COMPR)
			zlib_compress(&t->zbuf, &t->buf);
		sfnt_size += t->buf.len+3 & ~3;
		woff_size += t->zbuf.len+3 & ~3;
	}

	meta_off = 0;
	if(ttf->woff_meta.len >= MIN_COMPR) {
		meta_comp = ttf->woff_meta;
		zlib_compress(&meta_comp, &ttf->woff_meta);
		meta_off = woff_size;
		woff_size += meta_comp.len;
	}

	priv_off = 0;
	if(ttf->woff_priv.len) {
		priv_off = woff_size;
		woff_size += ttf->woff_priv.len;
	}

	buf = my_alloc(woff_size);

	p32(buf, 0x774F4646);
	p32(buf+4, ttf->flavor);
	p32(buf+8, woff_size);
	p16(buf+12, ttf->ntables);
	p16(buf+14, 0);
	p32(buf+16, sfnt_size);
	p32(buf+20, 0); // version ?
	p32(buf+24, meta_off);
	p32(buf+28, meta_comp.len); // meta len
	p32(buf+32, ttf->woff_meta.len); // meta orig len
	p32(buf+36, priv_off);
	p32(buf+40, ttf->woff_priv.len);

	p = buf + 44;
	for(i=0; i<ttf->ntables; i++) {
		struct table *t = &ttf->tables[i];
		p32(p, t->tag);
		p32(p+4, t->pos);
		p32(p+8, t->zbuf.len);
		p32(p+12, t->buf.len);
		p32(p+16, t->csum);
		p += 20;
	}

	for(i=0; i<ttf->ntables; i++) {
		struct table *t = ttf->tab_pos[i];
		u32 sz = t->zbuf.len;
		p = append(p, t->zbuf.ptr, sz);
		while(sz&3) *p++=0, sz++;
//		if(t->zbuf.ptr != t->buf.ptr)
//			my_free(t->zbuf.ptr);
	}

	if(meta_comp.len)
		p = append(p, meta_comp.ptr, meta_comp.len);

	if(ttf->woff_priv.len)
		p = append(p, ttf->woff_priv.ptr, ttf->woff_priv.len);

	assert(p == buf+woff_size);

	out->ptr = buf;
	out->len = woff_size;
}
