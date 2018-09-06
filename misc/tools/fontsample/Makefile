sources = fontsample.mm

CC = clang
CXX = clang
LD = clang

XFLAGS    := -Wall -g -fno-common
CFLAGS    += -std=c11
CXXFLAGS  += -std=c++11 -stdlib=libc++ -fno-rtti -fno-exceptions
LDFLAGS   += -lc++

#flags release and debug targets (e.g. make DEBUG=1)
ifeq ($(strip $(DEBUG)),1)
	XFLAGS += -O0
# else
# 	XFLAGS += -Os -DNDEBUG
endif

libs := -lobjc
frameworks := -framework Foundation \
              -framework CoreText \
              -framework CoreServices \
              -framework CoreGraphics \
              -framework ImageIO

c_flags   = $(CFLAGS) $(XFLAGS) -MMD -fobjc-arc
cxx_flags = $(CXXFLAGS) $(XFLAGS) -MMD -fobjc-arc
ld_flags  = $(LDFLAGS) $(libs) $(frameworks)

objects := $(sources:%.c=%.o)
objects := $(objects:%.cc=%.o)
objects := $(objects:%.mm=%.o)

fontsample: $(objects)
	$(LD) $(ld_flags) -o $@ $^

%.o: %.mm
	$(CXX) $(cxx_flags) -c $<

clean:
	rm -f *.o

all: fontsample
.PHONY: all clean
