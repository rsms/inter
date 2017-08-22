#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdarg.h>

static void er(int s, int e, char *f, va_list *va)
{
//	fprintf(stderr, "%s: ", getexecname());
	if(f) vfprintf(stderr, f, *va);
	va_end(*va);
	if(e >= 0) fprintf(stderr, ": %s", strerror(e));
	putc('\n', stderr);
	if(s >= 0) exit(s);
}

void err(int s, char *f, ...)
{
	va_list va;
	va_start(va, f);
	er(s, errno, f, &va);
}

void errx(int s, char *f, ...)
{
	va_list va;
	va_start(va, f);
	er(s, -1, f, &va);
}

void warn(char *f, ...)
{
	va_list va;
	va_start(va, f);
	er(-1, errno, f, &va);
}

void warnx(char *f, ...)
{
	va_list va;
	va_start(va, f);
	er(-1, -1, f, &va);
}
