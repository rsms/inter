SRCDIR  := $(abspath $(lastword $(MAKEFILE_LIST))/../..)
FONTDIR := ../build/fonts
BIN     := $(SRCDIR)/build/venv/bin
VENV    := ../build/venv/bin/activate
Q = $(if $(filter 1,$(V) $(VERBOSE)),,@)  # make V=1 for verbose mode
export PATH := $(BIN):$(PATH)

HTTP_SERVER_BIND_ADDR ?= 127.0.0.1

default:
	@echo "Please specify a target: build, serve, dist" >&2

build: .ruby-bundle
	rm -rf _site
	bundle exec jekyll build

build-tmp: .ruby-bundle
	rm -rf _site-tmp
	bundle exec jekyll build --disable-disk-cache -b /tmp/inter-v4-website -d _site-tmp

serve: .ruby-bundle
	$(Q)( sleep 3 && \
		rm -f _site/lab/fonts && \
		ln -s ../../../build/fonts _site/lab/fonts ) &
	@#
	@# need to delete generated content so that jekyll, being a little dumb,
	@# can manage to copy the font files into there again.
	@# Why not a symlink you ask? Jekyll traverses it and copies the content.
	@# In the past we tried to work around this by periodically removing the
	@# copied font files and re-creating the symlink, but it was a frail process.
	@# For live testing with fonts, you'll instead want to use docs/lab/serve.py
	$(Q)rm -rf _site
	$(Q)bundle exec jekyll serve -b '' --watch \
		--config _config.yml,_config-dev.yml \
	  --host $(HTTP_SERVER_BIND_ADDR) --port 3002 \
	  --livereload --livereload-port 30002

serve-pub:
	exec $(MAKE) HTTP_SERVER_BIND_ADDR=0.0.0.0 serve

optimize-images:
	$(Q)for f in $$(find . -type f -name \*.png); do \
		echo optipng "$$f"; \
		optipng -quiet "$$f" & \
	done ; \
	wait

.ruby-bundle: Gemfile Gemfile.lock
	@if ! (command -v bundle >/dev/null && command -v jekyll >/dev/null); then \
	  echo "Please install Ruby bundle and jekyll: gem install bundler jekyll" >&2; \
	  exit 1; \
	fi
	bundle update
	bundle install
	touch .ruby-bundle

# -----------------------------------------------------------------------

dist: info lab/index.html
info: fonts _data/fontinfo.json lab/glyphinfo.json
fonts: font-files/Inter-Regular.woff2

FONTS_SRC := \
	$(FONTDIR)/static/Inter-Black.woff2 \
	$(FONTDIR)/static/Inter-BlackItalic.woff2 \
	$(FONTDIR)/static/Inter-Bold.woff2 \
	$(FONTDIR)/static/Inter-BoldItalic.woff2 \
	$(FONTDIR)/static/Inter-ExtraBold.woff2 \
	$(FONTDIR)/static/Inter-ExtraBoldItalic.woff2 \
	$(FONTDIR)/static/Inter-ExtraLight.woff2 \
	$(FONTDIR)/static/Inter-ExtraLightItalic.woff2 \
	$(FONTDIR)/static/Inter-Italic.woff2 \
	$(FONTDIR)/static/Inter-Light.woff2 \
	$(FONTDIR)/static/Inter-LightItalic.woff2 \
	$(FONTDIR)/static/Inter-Medium.woff2 \
	$(FONTDIR)/static/Inter-MediumItalic.woff2 \
	$(FONTDIR)/static/Inter-Regular.woff2 \
	$(FONTDIR)/static/Inter-SemiBold.woff2 \
	$(FONTDIR)/static/Inter-SemiBoldItalic.woff2 \
	$(FONTDIR)/static/Inter-Thin.woff2 \
	$(FONTDIR)/static/Inter-ThinItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Black.woff2 \
	$(FONTDIR)/static/InterDisplay-BlackItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Bold.woff2 \
	$(FONTDIR)/static/InterDisplay-BoldItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraBold.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraBoldItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraLight.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraLightItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Italic.woff2 \
	$(FONTDIR)/static/InterDisplay-Light.woff2 \
	$(FONTDIR)/static/InterDisplay-LightItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Medium.woff2 \
	$(FONTDIR)/static/InterDisplay-MediumItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Regular.woff2 \
	$(FONTDIR)/static/InterDisplay-SemiBold.woff2 \
	$(FONTDIR)/static/InterDisplay-SemiBoldItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Thin.woff2 \
	$(FONTDIR)/static/InterDisplay-ThinItalic.woff2 \
  $(FONTDIR)/var/InterVariable.woff2 \
  $(FONTDIR)/var/InterVariable-Italic.woff2 \
  $(FONTDIR)/var/InterVariable.ttf

font-files/Inter-Regular.woff2: $(FONTS_SRC)
	rm -rf font-files/Inter*
	mkdir -p font-files
	cp -a $^ font-files/
	$(Q)touch $@

$(FONTS_SRC):
	@echo "Missing fonts in $(FONTDIR)" >&2
	@echo "Did you forget to 'make web' in the repository root?" >&2
	@exit 1

lab/index.html: ../version.txt ../misc/tools/patch-version.py
	. $(VENV); python ../misc/tools/patch-version.py $@

_data/fontinfo.json: ../misc/tools/fontinfo.py
_data/fontinfo.json: font-files/Inter-Regular.woff2
	. $(VENV); python ../misc/tools/fontinfo.py -pretty $< > $@

lab/glyphinfo.json: ../misc/tools/gen-glyphinfo.py ../misc/UnicodeData.txt
lab/glyphinfo.json: ../build/ufo/Inter-Regular.ufo
	. $(VENV); python ../misc/tools/gen-glyphinfo.py -ucd ../misc/UnicodeData.txt $< > $@
../build/ufo/Inter-Regular.ufo: $(wildcard ../build/ufo/Inter-Regular.ufo/*.plist)
	touch $@

.PHONY: default build build-tmp serve serve-pub dist info fonts
