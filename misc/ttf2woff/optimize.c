/*
 *	Copyright (C) 2013 Jan Bobrowski <jb@wizard.ae.krakow.pl>
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License
 *	version 2 as published by the Free Software Foundation.
 */

#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include "ttf2woff.h"

struct table *find_table(struct ttf *ttf, char tag[4])
{
	u32 tg = g32((u8*)tag);
	int i;
	for(i=0; i<ttf->ntables; i++)
		if(ttf->tables[i].tag == tg)
			return &ttf->tables[i];
	return 0;
}

static void replace_table(struct table *t, u8 *p, int l)
{
	if(t->free_buf)
		t->buf.ptr = my_free(t->buf.ptr);
	t->free_buf = 1;
	t->modified = 1;
	t->buf.ptr = p;
	t->buf.len = l;
}

static void optimized(struct table *t, struct buf new)
{
	if(g.verbose)
		echo("Optimized %s table: %u > %u (%d bytes)", t->name, t->buf.len, new.len, new.len-t->buf.len);
	replace_table(t, new.ptr, new.len);
}

static void optimize_loca(struct ttf *ttf)
{
	struct table *head, *loca, *glyf;
	struct buf new;
	int i,n;

	head = find_table(ttf, "head");
	loca = find_table(ttf, "loca");
	glyf = find_table(ttf, "glyf");

	if(!head || !loca || !glyf)
		return;

	if(head->buf.len<54 || g16(head->buf.ptr+50)!=1)
		return;

	if(loca->buf.len&3 || loca->buf.len<4)
		return;

	// we have 32-bit loca table

	if(glyf->buf.len != g32(loca->buf.ptr+loca->buf.len-4))
		return;

	if(glyf->buf.len >= 1<<16)
		return;

	n = loca->buf.len>>2;
	new.len = 2*n;
	new.ptr = my_alloc(new.len);
	for(i=0;i<n;i++) {
		u32 o = g32(loca->buf.ptr+4*i);
		if(o&1) {
			echo("Bad offset in loca");
			my_free(new.ptr);
			return;
		}
		p16(new.ptr+2*i, o>>1);
	}

	optimized(loca, new);

	p16(head->buf.ptr+50, 0);
	head->modified = 1;
}

static int overlap(struct buf a, struct buf b)
{
	int o = a.len<b.len ? a.len : b.len;
	while(o) {
		if(memcmp(a.len-o+a.ptr, b.ptr, o)==0)
			break;
		o--;
	}
	return o;
}

static u8 *bufbuf(struct buf a, struct buf b)
{
	u8 *p=a.ptr, *e=a.ptr+a.len-b.len;
	while(p<=e) {
		if(memcmp(p,b.ptr,b.len)==0)
			return p;
		p++;
	}
	return 0;
}

static int name_cmp_len(const void *va, const void *vb) {
	struct buf a = *(struct buf*)va;
	struct buf b = *(struct buf*)vb;
	int d = a.len - b.len;
	if(!d) d = memcmp(a.ptr, b.ptr, a.len);
	return d;
}

static void optimize_name(struct ttf *ttf)
{
	struct table *name = find_table(ttf, "name");
	struct buf str, new;
	struct buf *ent;
	u8 *p;
	int count,n,i;

	if(!name || name->buf.len<6+2*12+1 || g16(name->buf.ptr))
		return;

	n = g16(name->buf.ptr+4); // stringOffset
	if(name->buf.len < n)
		goto corrupted;

	str.ptr = name->buf.ptr+n;
	str.len = name->buf.len-n;

	count = g16(name->buf.ptr+2);
	if(name->buf.len < 6+12*count) {
corrupted:
		echo("Name table corrupted");
		return;
	}

	n = count;
	ent = my_alloc(n * sizeof *ent);

	p = name->buf.ptr+6;
	for(i=0; i<n; i++) {
		unsigned l = g16(p+8);
		unsigned o = g16(p+10);
		if(o+l > str.len) {
			echo("Bad string location in name table");
			my_free(ent);
			return;
		}
		if(l) {
			ent[i].ptr = str.ptr + o;
			ent[i].len = l;
		}
		p += 12;
	}

	qsort(ent, n, sizeof *ent, name_cmp_len);

	for(;;) {
		int j,mo,mi,mj;
		struct buf a, b, c;

		mo = 0;
		for(j=0;j<n;j++) for(i=1;i<n;i++) if(i!=j) {
			int o;
			a = ent[i];
			b = ent[j];
			if(bufbuf(a,b))
				goto remove_b;
			o = overlap(a,b);
			if(o > mo) {
				mo = o;
				mi = i;
				mj = j;
			}
		}
		if(!mo)
			break;

		a = ent[mi];
		b = ent[mj];
		c.len = a.len + b.len - mo;
		c.ptr = my_alloc(c.len);
		p = append(c.ptr, a.ptr, a.len);
		append(p, b.ptr+mo, b.len-mo);
		if(a.ptr<str.ptr || a.ptr>=str.ptr+str.len)
			my_free(a.ptr);

		i = mi<mj ? mi : mj;
		j = mi<mj ? mj : mi;
		ent[i] = c;

remove_b:
		if(b.ptr<str.ptr || b.ptr>=str.ptr+str.len)
			my_free(b.ptr);
		n--;
		while(j < n) ent[j]=ent[j+1], j++;
	}

	{
		int sz = 6 + 12*count;
		for(i=0;i<n;i++)
			sz += ent[i].len;

		if(sz >= name->buf.len) {
			my_free(ent);
			return;
		}

		new.len = sz;
		new.ptr = my_alloc(sz);

		p = new.ptr + 6 + 12*count;
		for(i=0;i<n;i++) {
			struct buf a = ent[i];
			memcpy(p,a.ptr,a.len); p+=a.len;
			if(a.ptr<str.ptr || a.ptr>=str.ptr+str.len)
				my_free(a.ptr);
		}
		assert(p == new.ptr+new.len);
	}

	my_free(ent);

	memcpy(new.ptr, name->buf.ptr, 6+12*count);
	p16(new.ptr+4,6+12*count);

	{
		struct buf newstr;

		newstr.ptr = new.ptr + 6+12*count;
		newstr.len = new.len - 6+12*count;

		p = new.ptr + 6 + 10;
		for(i=0;i<count;i++) {
			struct buf a = {str.ptr+g16(p), g16(p-2)};
			u8 *s = bufbuf(newstr, a);
			assert(s);
			p16(p, s-newstr.ptr);
			p += 12;
		}
	}

#ifndef NDEBUG
	for(i=0; i<count; i++) {
		u8 *p0 = name->buf.ptr;
		u8 *p1 = new.ptr;
		p0 += g16(p0+4) + g16(p0+6+12*i+10);
		p1 += g16(p1+4) + g16(p1+6+12*i+10);
		assert(!memcmp(p0,p1,g16(new.ptr+6+12*i+8)));
	}
#endif

	optimized(name, new);
}

static void optimize_hmtx(struct ttf *ttf)
{
	struct table *hhea, *hmtx;
	struct buf buf;
	u8 *p, *q;
	int nlhm,adv,n;

	hhea = find_table(ttf, "hhea");
	hmtx = find_table(ttf, "hmtx");

	if(!hhea || !hmtx || hhea->buf.len < 36 || g32(hhea->buf.ptr)!=0x10000)
		return;

	nlhm = g16(hhea->buf.ptr + 34);
	buf = hmtx->buf;

	if(!nlhm || buf.len&1 || buf.len < 4*nlhm) {
		return;
	}

	if(nlhm<2)
		return;

	p = buf.ptr + 4*(nlhm-1);
	adv = g16(p);

	for(n=nlhm; n>1; n--) {
		p -= 4;
		if(adv != g16(p))
			break;
	}
	if(n < nlhm) {
		struct buf new;
		int i, nent = (buf.len>>1) - nlhm;

		new.len = 2*nent + 2*n;
		new.ptr = my_alloc(new.len);
		p = append(new.ptr, buf.ptr, n<<2);
		q = buf.ptr + (n<<2);
		for(i=n; i<nlhm; i++) {
			p = p16(p, g16(q+2));
			q += 4;
		}
		p = append(p, q, buf.ptr+buf.len-q);
		assert(p == new.ptr+new.len);

		optimized(hmtx, new);

		p16(hhea->buf.ptr+34, n);
		hhea->modified = 1;
	}
}

void optimize(struct ttf *ttf)
{
	optimize_loca(ttf);
	optimize_name(ttf);
	optimize_hmtx(ttf);
}
