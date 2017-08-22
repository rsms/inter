# gmake

NAME = ttf2woff
VERSION = 0.14
BINDIR = /usr/local/bin
PKG=$(NAME)-$(VERSION)
FILES_TTF2WOFF := Makefile ttf2woff.c ttf2woff.h genwoff.c genttf.c readttf.c  readttc.c readwoff.c optimize.c \
  comp-zlib.c comp-zopfli.c compat.c ttf2woff.rc zopfli.diff
FILES_ZOPFLI := zopfli.h symbols.h \
  $(patsubst %,%.h,zlib_container deflate lz77 blocksplitter squeeze hash cache tree util katajainen) \
  $(patsubst %,%.c,zlib_container deflate lz77 blocksplitter squeeze hash cache tree util katajainen)
FILES += $(FILES_TTF2WOFF) $(addprefix zopfli/,$(FILES_ZOPFLI))

ZOPFLI = 1

OBJ := ttf2woff.o readttf.o readttc.o readwoff.o genwoff.o genttf.o optimize.o
ifeq ($(ZOPFLI),)
OBJ += comp-zlib.o
else
OBJ += comp-zopfli.o
LDFLAGS += -lm
endif

CFLAGS ?= -O2 -g
LDFLAGS += -lz

# eg. make WIN32=1 CC=mingw32-gcc RC=mingw32-windres
ifdef WIN32
EXE = .exe
CFLAGS += -DNO_ERRWARN
OBJ += compat.o rc.o
endif

ttf2woff$(EXE): $(OBJ)
	$(CC) -o $@ $(OBJ) $(LDFLAGS)

ttf2woff.o: ttf2woff.c ttf2woff.h Makefile
	$(CC) $(CFLAGS) -DVERSION=$(VERSION) -c ttf2woff.c

comp-zopfli.o: comp-zopfli.c ttf2woff.h $(addprefix zopfli/,$(FILES_ZOPFLI))
	$(CC) $(CFLAGS) -c comp-zopfli.c

rc.o: ttf2woff.rc Makefile
	$(RC) $(DEF) -DVERNUMS=`echo $(VERSION) | sed 's/\\./,/g; s/[^0-9,]//g'` -DVERSION=$(VERSION) -o $@ ttf2woff.rc

install: ttf2woff
	install -s $< $(BINDIR)

clean:
	rm -f ttf2woff $(addsuffix .o,$(basename $(filter %.c,$(FILES_TTF2WOFF))))

dist:
	ln -s . $(PKG)
	tar czf $(PKG).tar.gz --group=root --owner=root $(addprefix $(PKG)/, $(FILES)); \
	rm $(PKG)

.PHONY: install clean dist zopfli zopfli.diff


# git://github.com/google/zopfli.git
ZOPFLI_SRC = zopfli-src
zopfli: $(addprefix $(ZOPFLI_SRC)/src/zopfli/,$(FILES_ZOPFLI))
	@install -d zopfli
	cp -pf $^ zopfli
	patch -p3 -dzopfli <zopfli.diff

zopfli.diff:
	diff -u --minimal $(ZOPFLI_SRC)/src/zopfli zopfli >$@; true
