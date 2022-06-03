# List all targets with 'make list'
SRCDIR   := $(abspath $(lastword $(MAKEFILE_LIST))/..)
FONTDIR  := build/fonts
UFODIR   := build/ufo
BIN      := $(SRCDIR)/build/venv/bin
VENV     := build/venv/bin/activate
VERSION  := $(shell cat version.txt)
MAKEFILE := $(lastword $(MAKEFILE_LIST))

export PATH := $(BIN):$(PATH)

default: all

# ---------------------------------------------------------------------------------
# intermediate sources

$(UFODIR)/%.glyphs: src/%.glyphspackage | $(UFODIR) venv
	. $(VENV) ; build/venv/bin/glyphspkg -o $(dir $@) $^

# features
src/features: $(wildcard src/features/*)
	@touch "$@"
	@true
$(UFODIR)/features: src/features
	@mkdir -p $(UFODIR)
	@rm -f $(UFODIR)/features
	@ln -s ../../src/features $(UFODIR)/features

# designspace
$(UFODIR)/Inter-roman.designspace: $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; python misc/tools/subset-designspace.py $^ $@
$(UFODIR)/Inter-italic.designspace: $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; python misc/tools/subset-designspace.py $^ $@
$(UFODIR)/%.designspace: $(UFODIR)/%.glyphs $(UFODIR)/features | venv
	. $(VENV) ; fontmake -o ufo -g $< --designspace-path $@ \
		--master-dir $(UFODIR) --instance-dir $(UFODIR)
	. $(VENV) ; python misc/tools/postprocess-designspace.py $@

# master UFOs are byproducts of building Inter.designspace
$(UFODIR)/Inter-Black.ufo:       $(UFODIR)/Inter.designspace
	touch $@
$(UFODIR)/Inter-BlackItalic.ufo: $(UFODIR)/Inter.designspace
	touch $@
$(UFODIR)/Inter-Regular.ufo:     $(UFODIR)/Inter.designspace
	touch $@
$(UFODIR)/Inter-Italic.ufo:      $(UFODIR)/Inter.designspace
	touch $@
$(UFODIR)/Inter-Thin.ufo:        $(UFODIR)/Inter.designspace
	touch $@
$(UFODIR)/Inter-ThinItalic.ufo:  $(UFODIR)/Inter.designspace
	touch $@

# instance UFOs are generated on demand
$(UFODIR)/Inter-Light.ufo:            $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Light"
$(UFODIR)/Inter-LightItalic.ufo:      $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Light Italic"
$(UFODIR)/Inter-ExtraLight.ufo:       $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Extra Light"
$(UFODIR)/Inter-ExtraLightItalic.ufo: $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Extra Light Italic"
$(UFODIR)/Inter-Medium.ufo:           $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Medium"
$(UFODIR)/Inter-MediumItalic.ufo:     $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Medium Italic"
$(UFODIR)/Inter-SemiBold.ufo:         $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Semi Bold"
$(UFODIR)/Inter-SemiBoldItalic.ufo:   $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Semi Bold Italic"
$(UFODIR)/Inter-Bold.ufo:             $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Bold"
$(UFODIR)/Inter-BoldItalic.ufo:       $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Bold Italic"
$(UFODIR)/Inter-ExtraBold.ufo:        $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Extra Bold"
$(UFODIR)/Inter-ExtraBoldItalic.ufo:  $(UFODIR)/Inter.designspace | venv
	. $(VENV) ; fontmake -o ufo -m $< --output-path $@ -i "Inter Extra Bold Italic"

# make sure intermediate files are not rm'd by make
.PRECIOUS: \
	$(UFODIR)/Inter-Black.ufo \
	$(UFODIR)/Inter-BlackItalic.ufo \
	$(UFODIR)/Inter-Regular.ufo \
	$(UFODIR)/Inter-Italic.ufo \
	$(UFODIR)/Inter-Thin.ufo \
	$(UFODIR)/Inter-ThinItalic.ufo \
	$(UFODIR)/Inter-Light.ufo \
	$(UFODIR)/Inter-LightItalic.ufo \
	$(UFODIR)/Inter-ExtraLight.ufo \
	$(UFODIR)/Inter-ExtraLightItalic.ufo \
	$(UFODIR)/Inter-Medium.ufo \
	$(UFODIR)/Inter-MediumItalic.ufo \
	$(UFODIR)/Inter-SemiBold.ufo \
	$(UFODIR)/Inter-SemiBoldItalic.ufo \
	$(UFODIR)/Inter-Bold.ufo \
	$(UFODIR)/Inter-BoldItalic.ufo \
	$(UFODIR)/Inter-ExtraBold.ufo \
	$(UFODIR)/Inter-ExtraBoldItalic.ufo \
	$(UFODIR)/Inter.glyphs \
	$(UFODIR)/Inter.designspace \
	$(UFODIR)/Inter-roman.designspace \
	$(UFODIR)/Inter-italic.designspace

# ---------------------------------------------------------------------------------
# products

$(FONTDIR)/static/%.otf: $(UFODIR)/%.ufo | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o otf --output-path $@ \
		--overlaps-backend pathops --production-names

$(FONTDIR)/static/%.ttf: $(UFODIR)/%.ufo | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o ttf --output-path $@ \
		--overlaps-backend pathops --production-names

$(FONTDIR)/static-hinted/%.ttf: $(FONTDIR)/static/%.ttf | $(FONTDIR)/static-hinted venv
	. $(VENV) ; python $(PWD)/build/venv/lib/python/site-packages/ttfautohint \
		--no-info "$<" "$@"

$(FONTDIR)/var/Inter-V.var.ttf: $(FONTDIR)/var/Inter.var.ttf venv
	. $(VENV) ; python misc/tools/rename.py --family "Inter V" -o $@ $<

$(FONTDIR)/var/%.var.ttf: $(UFODIR)/%.designspace | $(FONTDIR)/var venv
	. $(VENV) ; fontmake -o variable -m $< --output-path $@ \
		--overlaps-backend pathops --production-names
	. $(VENV) ; python misc/tools/postprocess-vf.py $@
	. $(VENV) ; gftools fix-unwanted-tables -t MVAR $@

$(FONTDIR)/var/%.var.otf: $(UFODIR)/%.designspace | $(FONTDIR)/var venv
	. $(VENV) ; fontmake -o variable-cff2 -m $< --output-path $@ \
		--overlaps-backend pathops --production-names

%.woff2: %.ttf | venv
	. $(VENV) ; misc/tools/woff2 compress -o "$@" "$<"

$(FONTDIR)/static:
	mkdir -p $@
$(FONTDIR)/static-hinted:
	mkdir -p $@
$(FONTDIR)/var:
	mkdir -p $@
$(UFODIR):
	mkdir -p $@

static_otf: \
	$(FONTDIR)/static/Inter-Black.otf \
	$(FONTDIR)/static/Inter-BlackItalic.otf \
	$(FONTDIR)/static/Inter-Regular.otf \
	$(FONTDIR)/static/Inter-Italic.otf \
	$(FONTDIR)/static/Inter-Thin.otf \
	$(FONTDIR)/static/Inter-ThinItalic.otf \
	$(FONTDIR)/static/Inter-Light.otf \
	$(FONTDIR)/static/Inter-LightItalic.otf \
	$(FONTDIR)/static/Inter-ExtraLight.otf \
	$(FONTDIR)/static/Inter-ExtraLightItalic.otf \
	$(FONTDIR)/static/Inter-Medium.otf \
	$(FONTDIR)/static/Inter-MediumItalic.otf \
	$(FONTDIR)/static/Inter-SemiBold.otf \
	$(FONTDIR)/static/Inter-SemiBoldItalic.otf \
	$(FONTDIR)/static/Inter-Bold.otf \
	$(FONTDIR)/static/Inter-BoldItalic.otf \
	$(FONTDIR)/static/Inter-ExtraBold.otf \
	$(FONTDIR)/static/Inter-ExtraBoldItalic.otf

static_ttf: \
	$(FONTDIR)/static/Inter-Black.ttf \
	$(FONTDIR)/static/Inter-BlackItalic.ttf \
	$(FONTDIR)/static/Inter-Regular.ttf \
	$(FONTDIR)/static/Inter-Italic.ttf \
	$(FONTDIR)/static/Inter-Thin.ttf \
	$(FONTDIR)/static/Inter-ThinItalic.ttf \
	$(FONTDIR)/static/Inter-Light.ttf \
	$(FONTDIR)/static/Inter-LightItalic.ttf \
	$(FONTDIR)/static/Inter-ExtraLight.ttf \
	$(FONTDIR)/static/Inter-ExtraLightItalic.ttf \
	$(FONTDIR)/static/Inter-Medium.ttf \
	$(FONTDIR)/static/Inter-MediumItalic.ttf \
	$(FONTDIR)/static/Inter-SemiBold.ttf \
	$(FONTDIR)/static/Inter-SemiBoldItalic.ttf \
	$(FONTDIR)/static/Inter-Bold.ttf \
	$(FONTDIR)/static/Inter-BoldItalic.ttf \
	$(FONTDIR)/static/Inter-ExtraBold.ttf \
	$(FONTDIR)/static/Inter-ExtraBoldItalic.ttf

static_ttf_hinted: \
	$(FONTDIR)/static-hinted/Inter-Black.ttf \
	$(FONTDIR)/static-hinted/Inter-BlackItalic.ttf \
	$(FONTDIR)/static-hinted/Inter-Regular.ttf \
	$(FONTDIR)/static-hinted/Inter-Italic.ttf \
	$(FONTDIR)/static-hinted/Inter-Thin.ttf \
	$(FONTDIR)/static-hinted/Inter-ThinItalic.ttf \
	$(FONTDIR)/static-hinted/Inter-Light.ttf \
	$(FONTDIR)/static-hinted/Inter-LightItalic.ttf \
	$(FONTDIR)/static-hinted/Inter-ExtraLight.ttf \
	$(FONTDIR)/static-hinted/Inter-ExtraLightItalic.ttf \
	$(FONTDIR)/static-hinted/Inter-Medium.ttf \
	$(FONTDIR)/static-hinted/Inter-MediumItalic.ttf \
	$(FONTDIR)/static-hinted/Inter-SemiBold.ttf \
	$(FONTDIR)/static-hinted/Inter-SemiBoldItalic.ttf \
	$(FONTDIR)/static-hinted/Inter-Bold.ttf \
	$(FONTDIR)/static-hinted/Inter-BoldItalic.ttf \
	$(FONTDIR)/static-hinted/Inter-ExtraBold.ttf \
	$(FONTDIR)/static-hinted/Inter-ExtraBoldItalic.ttf

static_web: \
	$(FONTDIR)/static/Inter-Black.woff2 \
	$(FONTDIR)/static/Inter-BlackItalic.woff2 \
	$(FONTDIR)/static/Inter-Regular.woff2 \
	$(FONTDIR)/static/Inter-Italic.woff2 \
	$(FONTDIR)/static/Inter-Thin.woff2 \
	$(FONTDIR)/static/Inter-ThinItalic.woff2 \
	$(FONTDIR)/static/Inter-Light.woff2 \
	$(FONTDIR)/static/Inter-LightItalic.woff2 \
	$(FONTDIR)/static/Inter-ExtraLight.woff2 \
	$(FONTDIR)/static/Inter-ExtraLightItalic.woff2 \
	$(FONTDIR)/static/Inter-Medium.woff2 \
	$(FONTDIR)/static/Inter-MediumItalic.woff2 \
	$(FONTDIR)/static/Inter-SemiBold.woff2 \
	$(FONTDIR)/static/Inter-SemiBoldItalic.woff2 \
	$(FONTDIR)/static/Inter-Bold.woff2 \
	$(FONTDIR)/static/Inter-BoldItalic.woff2 \
	$(FONTDIR)/static/Inter-ExtraBold.woff2 \
	$(FONTDIR)/static/Inter-ExtraBoldItalic.woff2

static_web_hinted: \
	$(FONTDIR)/static-hinted/Inter-Black.woff2 \
	$(FONTDIR)/static-hinted/Inter-BlackItalic.woff2 \
	$(FONTDIR)/static-hinted/Inter-Regular.woff2 \
	$(FONTDIR)/static-hinted/Inter-Italic.woff2 \
	$(FONTDIR)/static-hinted/Inter-Thin.woff2 \
	$(FONTDIR)/static-hinted/Inter-ThinItalic.woff2 \
	$(FONTDIR)/static-hinted/Inter-Light.woff2 \
	$(FONTDIR)/static-hinted/Inter-LightItalic.woff2 \
	$(FONTDIR)/static-hinted/Inter-ExtraLight.woff2 \
	$(FONTDIR)/static-hinted/Inter-ExtraLightItalic.woff2 \
	$(FONTDIR)/static-hinted/Inter-Medium.woff2 \
	$(FONTDIR)/static-hinted/Inter-MediumItalic.woff2 \
	$(FONTDIR)/static-hinted/Inter-SemiBold.woff2 \
	$(FONTDIR)/static-hinted/Inter-SemiBoldItalic.woff2 \
	$(FONTDIR)/static-hinted/Inter-Bold.woff2 \
	$(FONTDIR)/static-hinted/Inter-BoldItalic.woff2 \
	$(FONTDIR)/static-hinted/Inter-ExtraBold.woff2 \
	$(FONTDIR)/static-hinted/Inter-ExtraBoldItalic.woff2

var: \
	$(FONTDIR)/var/Inter.var.ttf \
	$(FONTDIR)/var/Inter-V.var.ttf

var_no_slnt_axis: | venv \
	  $(FONTDIR)/var/Inter-roman.var.ttf \
	  $(FONTDIR)/var/Inter-italic.var.ttf
	. $(VENV) ; python misc/tools/postprocess-single-axis-vfs.py $^

var_web: $(FONTDIR)/var/Inter.var.woff2

var_web_all: var_web \
	$(FONTDIR)/var/Inter-V.var.woff2 \
	$(FONTDIR)/var/Inter-roman.var.woff2 \
	$(FONTDIR)/var/Inter-italic.var.woff2

web: var_web_all static_web

all:        static_otf static_ttf static_ttf_hinted static_web static_web_hinted \
            var var_web_all var_no_slnt_axis

.PHONY: all static_otf static_ttf static_ttf_hinted static_web static_web_hinted \
            var var_web var_web_all var_no_slnt_axis web

# ---------------------------------------------------------------------------------
# testing

test: build/fontbakery-report-var.txt \
      build/fontbakery-report-static.txt

# FBAKE_ARGS are common args for all fontbakery targets
FBAKE_ARGS := check-universal \
              --no-colors \
              --no-progress \
              --loglevel WARN \
              --succinct \
              --full-lists \
              -j \
              -x com.google.fonts/check/family/win_ascent_and_descent

build/fontbakery-report-var.txt: $(FONTDIR)/var/Inter.var.ttf | venv
	@echo "fontbakery Inter.var.ttf > $(@) ..."
	@. $(VENV) ; fontbakery \
		$(FBAKE_ARGS) -x com.google.fonts/check/STAT_strings \
		$^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)

build/fontbakery-report-static.txt: $(wildcard $(FONTDIR)/static/Inter-*.otf) | venv
	@echo "fontbakery static/Inter-*.otf > $(@) ..."
	@. $(VENV) ; fontbakery \
		$(FBAKE_ARGS) -x com.google.fonts/check/family/underline_thickness \
		$^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)

.PHONY: test

# ---------------------------------------------------------------------------------
# zip

zip: all
	bash misc/makezip2.sh -reveal-in-finder \
		"build/release/Inter-$(VERSION)-$(shell git rev-parse --short=10 HEAD).zip"

zip_opsz_beta: $(FONTDIR)/var/Inter-V.var.ttf $(FONTDIR)/var/Inter-V.var.woff2
	mkdir -p build/release
	zip -j -q -X \
	"build/release/Inter-opsz-beta-$(VERSION)-$(shell git rev-parse --short=10 HEAD).zip" \
	$^

.PHONY: zip zip_opsz_beta

# ---------------------------------------------------------------------------------
# distribution
# - preflight checks for existing version archive and dirty git state.
# - step1 rebuilds from scratch, since font version & ID is based on git hash.
# - step2 runs tests, then makes a zip archive and updates the website (docs/ dir.)

DIST_ZIP = build/release/Inter-${VERSION}.zip

dist: dist_preflight
	@# rebuild since font version & ID is based on git hash
	$(MAKE) -f $(MAKEFILE) -j$(nproc) dist_step1
	$(MAKE) -f $(MAKEFILE) -j$(nproc) dist_step2
	$(MAKE) -f $(MAKEFILE) dist_postflight

dist_preflight:
	@echo "——————————————————————————————————————————————————————————————————"
	@echo "Creating distribution for version ${VERSION}"
	@echo "——————————————————————————————————————————————————————————————————"
	@# check for existing version archive
	@if [ -f "${DIST_ZIP}" ]; then \
		echo "${DIST_ZIP} already exists. Bump version or rm zip file to continue." >&2; \
		exit 1; \
	fi
	@# check for uncommitted changes
	@git status --short | grep -qv '??' && (\
		echo "Warning: uncommitted changes:" >&2; git status --short | grep -v '??' ;\
		[ -t 1 ] || exit 1 ; \
		printf "Press ENTER to continue or ^C to cancel " ; read X) || true
	@#

dist_step1: clean
	$(MAKE) -f $(MAKEFILE) -j$(nproc) all

dist_step2: test
	$(MAKE) -f $(MAKEFILE) -j$(nproc) dist_zip dist_docs

dist_zip: | venv
	. $(VENV) ; python misc/tools/patch-version.py misc/dist/inter.css
	bash misc/makezip2.sh -reveal-in-finder "$(DIST_ZIP)"

dist_docs:
	$(MAKE) -C docs -j$(nproc) dist

dist_postflight:
	@echo "——————————————————————————————————————————————————————————————————"
	@echo ""
	@echo "Next steps:"
	@echo ""
	@echo "1) Commit & push changes"
	@echo ""
	@echo "2) Create new release with ${DIST_ZIP} at"
	@echo "   https://github.com/rsms/inter/releases/new?tag=v${VERSION}"
	@echo ""
	@echo "3) Bump version in version.txt (to the next future version)"
	@echo "   and commit & push changes"
	@echo ""
	@echo "——————————————————————————————————————————————————————————————————"

.PHONY: dist dist_preflight dist_step1 dist_step2 dist_zip dist_docs dist_postflight


# ---------------------------------------------------------------------------------
# install

INSTALLDIR := $(HOME)/Library/Fonts/Inter

install: install_var \
  $(INSTALLDIR)/Inter-Black.otf \
  $(INSTALLDIR)/Inter-BlackItalic.otf \
  $(INSTALLDIR)/Inter-Regular.otf \
  $(INSTALLDIR)/Inter-Italic.otf \
  $(INSTALLDIR)/Inter-Thin.otf \
  $(INSTALLDIR)/Inter-ThinItalic.otf \
  $(INSTALLDIR)/Inter-Light.otf \
  $(INSTALLDIR)/Inter-LightItalic.otf \
  $(INSTALLDIR)/Inter-ExtraLight.otf \
  $(INSTALLDIR)/Inter-ExtraLightItalic.otf \
  $(INSTALLDIR)/Inter-Medium.otf \
  $(INSTALLDIR)/Inter-MediumItalic.otf \
  $(INSTALLDIR)/Inter-SemiBold.otf \
  $(INSTALLDIR)/Inter-SemiBoldItalic.otf \
  $(INSTALLDIR)/Inter-Bold.otf \
  $(INSTALLDIR)/Inter-BoldItalic.otf \
  $(INSTALLDIR)/Inter-ExtraBold.otf \
  $(INSTALLDIR)/Inter-ExtraBoldItalic.otf

install_var: $(INSTALLDIR)/Inter-V.var.ttf

$(INSTALLDIR)/%.otf: $(FONTDIR)/static/%.otf | $(INSTALLDIR)
	cp -a $^ $@

$(INSTALLDIR)/%.var.ttf: $(FONTDIR)/var/%.var.ttf | $(INSTALLDIR)
	cp -a $^ $@

$(INSTALLDIR):
	mkdir -p $@

.PHONY: install install_var

# ---------------------------------------------------------------------------------
# misc

clean:
	rm -rf build/tmp build/fonts build/ufo build/googlefonts

docs:
	$(MAKE) -C docs serve

# update_ucd downloads the latest Unicode data (Nothing depends on this target)
ucd_version := 12.1.0
update_ucd:
	@echo "# Unicode $(ucd_version)" > misc/UnicodeData.txt
	curl '-#' "https://www.unicode.org/Public/$(ucd_version)/ucd/UnicodeData.txt" \
	>> misc/UnicodeData.txt

.PHONY: clean docs update_ucd

# ---------------------------------------------------------------------------------
# list make targets
#
# We copy the Makefile (first in MAKEFILE_LIST) and disable the include to only list
# primary targets, avoiding the generated targets.
list:
	@mkdir -p build/etc \
	&& cat $(MAKEFILE) \
	 | sed 's/include /#include /g' > build/etc/Makefile-list \
	&& $(MAKE) -pRrq -f build/etc/Makefile-list : 2>/dev/null \
	 | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' \
	 | sort \
	 | egrep -v -e '^_|/' \
	 | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

.PHONY: list

# ---------------------------------------------------------------------------------
# initialize toolchain

venv: build/venv/config.stamp

build/venv/config.stamp: requirements.txt
	@mkdir -p build
	test -d build/venv || python3 -m venv build/venv
	. $(VENV) ; pip install -Ur requirements.txt
	touch $@

reset: clean
	rm -rf build/venv

.PHONY: venv reset
