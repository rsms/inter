SRCDIR  := $(abspath $(lastword $(MAKEFILE_LIST))/../..)
BIN     := $(SRCDIR)/build/venv/bin
FONTDIR := ../build/fonts
export PATH := $(BIN):$(PATH)

default:
	@echo "Please specify a target: build, serve or dist" >&2

build:
	rm -rf _site
	bundle exec jekyll build

serve:
	./_scripts/serve.sh

# -----------------------------------------------------------------------

dist: fonts info
	$(BIN)/python3 ../misc/tools/patch-version.py lab/index.html

info: _data/fontinfo.json \
      lab/glyphinfo.json \
      glyphs/metrics.json

fonts:
	rm -rf font-files
	mkdir font-files
	cp -a $(FONTDIR)/static/*.woff2 \
	      $(FONTDIR)/static/*.otf \
	      $(FONTDIR)/var/Inter.var.* \
	      $(FONTDIR)/var/Inter-roman.var.* \
	      $(FONTDIR)/var/Inter-italic.var.* \
	      font-files/

_data/fontinfo.json: ../misc/tools/fontinfo.py font-files/Inter-Regular.otf
	$(BIN)/python3 ../misc/tools/fontinfo.py -pretty $< > _data/fontinfo.json

lab/glyphinfo.json: ../misc/tools/gen-glyphinfo.py \
                    ../build/ufo/Inter-Regular.ufo \
                    ../misc/UnicodeData.txt
	$(BIN)/python3 ../misc/tools/gen-glyphinfo.py \
		-ucd ../misc/UnicodeData.txt ../build/ufo/Inter-Regular.ufo > $@

glyphs/metrics.json: ../misc/tools/gen-metrics-and-svgs.py \
                     ../build/ufo/Inter-Regular.ufo
	$(BIN)/python3 ../misc/tools/gen-metrics-and-svgs.py ../build/ufo/Inter-Regular.ufo

font-files/Inter-Regular.otf: fonts

.PHONY: default build serve dist info fonts
