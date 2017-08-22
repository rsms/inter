/*
 *	Copyright (C) 2013 Jan Bobrowski <jb@wizard.ae.krakow.pl>
 *
 *	This program is free software; you can redistribute it and/or
 *	modify it under the terms of the GNU General Public License
 *	version 2 as published by the Free Software Foundation.
 */

#include <stdlib.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <getopt.h>
#include <stdio.h>
#include <stdarg.h>
#include <strings.h>
#include <errno.h>
#include "ttf2woff.h"

#ifndef O_BINARY
#define O_BINARY 0
#endif

struct flags g;

void echo(char *f, ...)
{
	FILE *o = g.stdout_used ? stderr : stdout;
	va_list va;
	va_start(va, f);
	vfprintf(o, f, va);
	va_end(va);
	fputc('\n',o);
}

void *my_alloc(size_t sz)
{
	void *p = malloc(sz);
	if(!p) errx(1,"Out of memory");
	return p;
}

void *my_free(void *p)
{
	free(p);
	return 0;
}

void *my_realloc(void *p, size_t sz)
{
	p = realloc(p, sz);
	if(!p) errx(1,"Out of memory");
	return p;
}

static struct buf read_file(char *path)
{
	struct buf file = {0};
	int v, fd = 0;

	if(path[0]!='-' || path[1]) {
		fd = open(path, O_RDONLY|O_BINARY);
		if(fd<0)
			err(1, "%s", path);
	}

	{
		struct stat st;
		if(fstat(fd, &st) < 0)
			err(1, "fstat");
		file.len = st.st_size;
	}

	if(file.len) {
		file.ptr = malloc(file.len);
		v = read(fd, file.ptr, file.len);
		if(v < file.len) {
			if(v<0) err(1, "read");
			errx(1, "Truncated");
		}
	} else {
		size_t alen = 0;
		file.ptr = 0;
		for(;;) {
			if(file.len == alen) {
				if(alen > 64<<20)
					errx(1,"Too much data - aborting");
				alen += 1<<16;
				file.ptr = my_realloc(file.ptr, alen);
			}
			v = read(fd, file.ptr+file.len, alen-file.len);
			if(v<=0) {
				if(v) err(1, "read");
				break;
			}
			file.len += v;
		}
	}
	if(fd) close(fd);

	return file;
}

static int open_temporary(char *pt, char **pnm)
{
	int l = strlen(pt);
	char *nm = malloc(l+5);
	char *p = nm + l;
	int i, fd;

	memcpy(nm, pt, l);
	*p++ = '.';
	for(i=0;;) {
		sprintf(p, "%d", i);
		fd = open(nm, O_WRONLY|O_TRUNC|O_CREAT|O_BINARY|O_EXCL, 0666);
		if(fd>=0)
			break;
		if(errno!=EEXIST)
			err(1, "%s", nm);
		if(++i>999)
			errx(1, "Can't create temporary file");
	}
	*pnm = nm;
	return fd;
}

void alloc_tables(struct ttf *ttf)
{
	int sz = ttf->ntables*sizeof *ttf->tables;
	ttf->tables = my_alloc(sz);
	memset(ttf->tables, 0, sz);
}

void name_table(struct table *t) {
	char *d = t->name;
	int i;
	for(i=24; i>=0; i-=8) {
		char c = t->tag>>i;
		if(c>' ' && c<127)
			*d++ = c;
	}
	*d = 0;
}

static u32 calc_csum(u8 *p, size_t n)
{
	u32 s=0;
	if(n) for(;;) {
		s += p[0]<<24;
		if(!--n) break;
		s += p[1]<<16;
		if(!--n) break;
		s += p[2]<<8;
		if(!--n) break;
		s += p[3];
		if(!--n) break;
		p += 4;
	}
	return s;
}

enum {
	tag_head = 0x68656164,
	tag_DSIG = 0x44534947
};

static void recalc_checksums(struct ttf *ttf)
{
	u8 h[12];
	u32 font_csum, off;
	int i, modified;
	struct table *head = 0;
	struct table *DSIG = 0;

	modified = ttf->modified;
	for(i=0; i<ttf->ntables; i++) {
		struct table *t = ttf->tab_pos[i];
		u8 *p = t->buf.ptr;
		u32 csum;

		if(t->tag == tag_DSIG && t->buf.len>8)
			DSIG = t;

		if(t->tag != tag_head)
			csum = calc_csum(p, t->buf.len);
		else {
			head = t;
			csum = calc_csum(p, 8);
			csum += calc_csum(p+12, t->buf.len-12);
		}
		modified |= t->modified;
		if(csum != t->csum) {
			modified = 1;
			t->csum = csum;
			if(!t->modified)
				echo("Corrected checksum of table %s", t->name);
		}
	}

	if(modified && DSIG) {
remove_signature:
		if(DSIG->free_buf)
			free(DSIG->buf.ptr);
		DSIG->buf.len = 8;
		DSIG->buf.ptr = (u8*)"\0\0\0\1\0\0\0"; // empty DSIG
		DSIG->free_buf = 0;
		DSIG->csum = calc_csum(DSIG->buf.ptr, DSIG->buf.len);
		DSIG = 0;
		if(g.verbose)
			echo("Digital signature removed");
	}

	put_ttf_header(h, ttf);
	font_csum = calc_csum(h, 12);

	off = 12 + 16*ttf->ntables;
	for(i=0; i<ttf->ntables; i++) {
		struct table *t = ttf->tab_pos[i];
		font_csum += t->tag + t->csum + off + t->buf.len;
		font_csum += t->csum;
		off += t->buf.len+3 & ~3;
	}

	if(!head || head->buf.len<16)
		errx(1, "No head table");

	{
		u8 *p = head->buf.ptr + 8;
		font_csum = 0xB1B0AFBA - font_csum;
		if(font_csum != g32(p)) {
			if(DSIG)
				goto remove_signature;
			p32(p, font_csum);
			if(!modified)
				echo("Corrected checkSumAdjustment");
		}
	}
}

static int usage(FILE *f, int y)
{
	if(!y) {
		fprintf(f, "usage:"
		 "\tttf2woff [-v] font.ttf [font.woff]\n"
		 "\tttf2woff [-v] font.woff [font.ttf]\n"
		 "\tttf2woff [-v] -i font\n"
		 "\tttf2woff -h\n");
	} else {
		fprintf(f,"TTF2WOFF "STR(VERSION)" by Jan Bobrowski\n"
		 "usage:\n"
		 " ttf2woff [-v] [-O|-S] [-t type] [-X table]... [-m file] [-p file] [-u font] input [output]\n"
		 " ttf2woff -i [-v] [-O|-S] [-X table]... [-m file] [-p file] file\n"
		 " ttf2woff -l input\n"
		 "  -v      be verbose\n"
		 "  -i      in place modification\n"
		 "  -O      optimize (default unless signed)\n"
		 "  -S      don't optimize\n"
		 "  -t fmt  output format: woff, ttf\n"
		 "  -u num  font number in collection (TTC), 0-based\n"
		 "  -m xml  metadata\n"
		 "  -p priv private data\n"
		 "  -X tag  remove table\n"
		 "  -l      list tables\n"
		 "Use `-' to indicate standard input/output.\n"
		 "Skip output for dry run.\n"
		 "Compressor: %s.\n",
		 copression_by);
	}
	return 1;
}

static int type_by_name(char *s)
{
	if(strcasecmp(s,"TTF")==0 || strcasecmp(s,"OTF")==0) return fmt_TTF;
	if(strcasecmp(s,"WOFF")==0) return fmt_WOFF;
	return fmt_UNKNOWN;
}

static int cmp_tab_pos(const void *a, const void *b) {
	return (*(struct table**)a)->pos - (*(struct table**)b)->pos;
}

int main(int argc, char *argv[])
{
	struct ttf ttf = {0};
	char *iname, *itype_name, *oname, *otype_name, *mname=0, *pname=0;
	struct buf input, output;
	struct buf xtab = {0};
	int i, v, itype, fontn;

	g.otype = fmt_UNKNOWN;
	g.dryrun = 1; // no output
	g.mayoptim = 1;
	fontn = 0;

	for(;;) switch(getopt(argc, argv, "vt:u:SOX:lm:p:ihV")) {
	case 'v': g.verbose = 1; break;
	case 'l': g.listonly = 1; break;
	case 'i': g.inplace = 1; break;
	case 't':
		v = type_by_name(optarg);
		if(v==fmt_UNKNOWN)
			errx(1, "Unsupported font type: %s", optarg);
		g.otype = v;
		break;
	case 'u':
		fontn = atoi(optarg);
		break;
	case 'S':
		g.mayoptim = g.optimize = 0;
		break;
	case 'O':
		g.mayoptim = g.optimize = 1;
		break;
	case 'X':
		v = strlen(optarg) + 1;
		xtab.ptr = my_realloc(xtab.ptr, xtab.len+v);
		strcpy(xtab.ptr+xtab.len, optarg);
		xtab.len += v;
		break;
	case 'm': mname = optarg; break;
	case 'p': pname = optarg; break;
	case '?':
		if(optopt!='?')
			break;
	case 'h': return usage(stdout,1);
	case 'V': printf(STR(VERSION)"\n"); return 0;
	case -1: goto gotopt;
	}
gotopt:

	if(optind==argc)
		return usage(stderr,0);

	iname = argv[optind++];
	oname = 0;

	if(g.inplace) {
		if(iname[0]=='-' && !iname[1])
			errx(1, "-i is not compatible with -");
		g.dryrun = 0;
		if(optind < argc)
			warnx("Too many args");
	}

	if(optind < argc) {
		g.dryrun = 0;
		oname = argv[optind++];
		if(optind < argc)
			warnx("Too many args");
		if(oname[0]=='-' && !oname[1]) {
			oname = 0;
			g.stdout_used = 1;
		} else if(g.otype==fmt_UNKNOWN) {
			char *p = strrchr(oname, '.');
			if(p)
				g.otype = type_by_name(p+1);
		}
	}

	input = read_file(iname);

	if(input.len < 28)
		errx(1,"File too short");

	itype = fmt_UNKNOWN;
	if(g32(input.ptr) == g32("wOFF")) {
		read_woff(&ttf, input.ptr, input.len);
		itype_name = "WOFF";
		itype = fmt_WOFF;
	} else if(g32(input.ptr) == g32("ttcf")) {
		if(g.inplace)
			errx(1, "Can't optimize collection");
		read_ttc(&ttf, input.ptr, input.len, fontn);
		itype_name = "TTC";
	} else if(g32(input.ptr) == g32("wOF2")) {
		errx(1, "WOFF2 is not supported");
	} else {
		read_ttf(&ttf, input.ptr, input.len, 0);
		itype_name = "TTF";
		itype = fmt_TTF;
	}

	if(g.inplace)
		g.otype = itype;

	if(g.otype==fmt_UNKNOWN || g.otype==fmt_WOFF) {
		g.otype = fmt_WOFF;
		if(mname)
			ttf.woff_meta = read_file(mname);
		if(pname)
			ttf.woff_priv = read_file(pname);
	}

	// all read

	if(xtab.len) {
		char *p=xtab.ptr, *e=p+xtab.len;
		for(; p<e; p=strchr(p,0)+1) {
			struct table *t;
			struct buf *b;
			if(strcmp(p,"metadata")==0) {
				b = &ttf.woff_meta;
rm_meta:
				if(b->len) {
					b->len = 0;
					ttf.modified_meta = 1;
				}
				continue;
			}
			if(strcmp(p,"private")==0) {
				b = &ttf.woff_priv;
				goto rm_meta;
			}
			for(i=0; i<ttf.ntables; i++) {
				t = &ttf.tables[i];
				if(strcmp(t->name, p)==0)
					goto rm_tab;
			}
			echo("Table %s not found", p);
			if(0) {
rm_tab:
				memmove(t, t+1, (char*)(ttf.tables+ttf.ntables) - (char*)(t+1));
				ttf.ntables--;
				ttf.modified = 1;
				if(g.verbose)
					echo("Table %s removed", p);
			}
		}
		free(xtab.ptr);
	}

	ttf.tab_pos = malloc(ttf.ntables * sizeof *ttf.tab_pos);
	for(i=0; i<ttf.ntables; i++)
		ttf.tab_pos[i] = &ttf.tables[i];
	qsort(ttf.tab_pos, ttf.ntables, sizeof *ttf.tab_pos, cmp_tab_pos);

	if(g.listonly) {
		unsigned size = 12 + 16*ttf.ntables;
		for(i=0; i<ttf.ntables; i++) {
			struct table *t = ttf.tab_pos[i];
			size += t->buf.len;
			echo("%-4s %6u", t->name, t->buf.len);
		}
		echo("%-4s %6u", "", size);
		return 0;
	}

	if(!ttf.modified) {
		struct table *t = find_table(&ttf, "DSIG");
		if(t && t->buf.len>8)
			g.mayoptim = g.optimize;
	}

	if(g.mayoptim)
		optimize(&ttf);

	recalc_checksums(&ttf);

	switch(g.otype) {
	case fmt_TTF:
		gen_ttf(&output, &ttf);
		otype_name = "TTF";
		break;
	case fmt_WOFF:
		gen_woff(&output, &ttf);
		otype_name = "WOFF";
		break;
	}

	if(g.verbose || g.dryrun)
		echo("input: %s %u bytes, output: %s %u bytes (%.1f%%)",
		 itype_name, input.len, otype_name, output.len, 100.*output.len/input.len);

	if(g.dryrun)
		return 0;

	if(g.inplace && !ttf.modified && !ttf.modified_meta) {
		if(output.len >= input.len) {
			if(g.verbose)
				echo("Not modified");
			return 0;
		}
	}

	{
		u8 *p=output.ptr, *e=p+output.len;
		int fd = 1;

		if(g.inplace)
			fd = open_temporary(iname, &oname);
		else if(oname) {
			fd = open(oname, O_WRONLY|O_TRUNC|O_CREAT|O_BINARY, 0666);
			if(fd<0) err(1, "%s", oname);
		}

		do {
			v = write(fd, p, e-p);
			if(v<=0) {
				if(v) err(1, "write");
				errx(1, "Short write");
			}
			p += v;
		} while(p < e);

		close(fd);
	}

	if(g.inplace) {
#ifdef WIN32
		unlink(iname);
#endif
		v = rename(oname, iname);
		if(v<0) {
			warn("Rename %s to %s", oname, iname);
			unlink(oname);
			return 1;
		}
//		free(oname);
	}

	return 0;
}
