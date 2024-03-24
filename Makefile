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

# arguments to fontmake
FM_ARGS :=
ifndef DEBUG
	FM_ARGS += --verbose WARNING
endif

# ---------------------------------------------------------------------------------
# intermediate sources

$(UFODIR)/%.glyphs: src/%.glyphspackage | $(UFODIR) venv
	. $(VENV) ; build/venv/bin/glyphspkg -o $(dir $@) $^

# features
build/features_data: $(UFODIR)/features $(wildcard src/features/*)
	touch "$@"
$(UFODIR)/features:
	@mkdir -p $(UFODIR)
	@rm -f $(UFODIR)/features
	@ln -s ../../src/features $(UFODIR)/features

# designspace & master UFOs
$(UFODIR)/%.var.designspace: $(UFODIR)/%.designspace misc/tools/gen-var-designspace.py | venv
	. $(VENV) ; python misc/tools/gen-var-designspace.py $< $@

$(UFODIR)/%.designspace: $(UFODIR)/%.glyphs $(UFODIR)/features misc/tools/postprocess-designspace.py | venv
	. $(VENV) ; fontmake $(FM_ARGS) -o ufo -g $< --designspace-path $@ \
		  --master-dir $(UFODIR) --instance-dir $(UFODIR)
	. $(VENV) ; python misc/tools/postprocess-designspace.py $@

# instance UFOs from designspace
$(UFODIR)/Inter%Italic.ufo: $(UFODIR)/Inter-Italic.designspace misc/tools/gen-instance-ufo.sh | venv
	. $(VENV) ; bash misc/tools/gen-instance-ufo.sh $< $@
$(UFODIR)/Inter%.ufo: $(UFODIR)/Inter-Roman.designspace misc/tools/gen-instance-ufo.sh | venv
	. $(VENV) ; bash misc/tools/gen-instance-ufo.sh $< $@

# designspace & master UFOs (for editing)
build/ufo-editable/%.designspace: $(UFODIR)/%.glyphs $(UFODIR)/features misc/tools/postprocess-designspace.py | venv
	@mkdir -p $(dir $@)
	. $(VENV) ; fontmake $(FM_ARGS) -o ufo -g $< --designspace-path $@ \
		  --master-dir $(dir $@) --instance-dir $(dir $@)
	. $(VENV) ; python misc/tools/postprocess-designspace.py --editable $@

# instance UFOs from designspace (for editing)
build/ufo-editable/Inter%Italic.ufo: build/ufo-editable/Inter-Italic.designspace misc/tools/gen-instance-ufo.sh | venv
	. $(VENV) ; bash misc/tools/gen-instance-ufo.sh $< $@
build/ufo-editable/Inter%.ufo: build/ufo-editable/Inter-Roman.designspace misc/tools/gen-instance-ufo.sh | venv
	. $(VENV) ; bash misc/tools/gen-instance-ufo.sh $< $@

editable-ufos: build/ufo-editable/.ok
	@echo "Editable designspace & UFOs can be found here:"
	@echo "  $(PWD)/build/ufo-editable"

build/ufo-editable/.ok: build/ufo-editable/Inter-Roman.designspace build/ufo-editable/Inter-Italic.designspace
	@rm -f build/ufo-editable/features
	@ln -s ../../src/features build/ufo-editable/features
	$(MAKE) \
		build/ufo-editable/Inter-Light.ufo \
		build/ufo-editable/Inter-ExtraLight.ufo \
		build/ufo-editable/Inter-Medium.ufo \
		build/ufo-editable/Inter-SemiBold.ufo \
		build/ufo-editable/Inter-Bold.ufo \
		build/ufo-editable/Inter-ExtraBold.ufo \
		\
		build/ufo-editable/Inter-LightItalic.ufo \
		build/ufo-editable/Inter-ExtraLightItalic.ufo \
		build/ufo-editable/Inter-MediumItalic.ufo \
		build/ufo-editable/Inter-SemiBoldItalic.ufo \
		build/ufo-editable/Inter-BoldItalic.ufo \
		build/ufo-editable/Inter-ExtraBoldItalic.ufo \
		\
		build/ufo-editable/InterDisplay-Light.ufo \
		build/ufo-editable/InterDisplay-ExtraLight.ufo \
		build/ufo-editable/InterDisplay-Medium.ufo \
		build/ufo-editable/InterDisplay-SemiBold.ufo \
		build/ufo-editable/InterDisplay-Bold.ufo \
		build/ufo-editable/InterDisplay-ExtraBold.ufo \
		\
		build/ufo-editable/InterDisplay-LightItalic.ufo \
		build/ufo-editable/InterDisplay-ExtraLightItalic.ufo \
		build/ufo-editable/InterDisplay-MediumItalic.ufo \
		build/ufo-editable/InterDisplay-SemiBoldItalic.ufo \
		build/ufo-editable/InterDisplay-BoldItalic.ufo \
		build/ufo-editable/InterDisplay-ExtraBoldItalic.ufo
	@touch $@
	@echo ""

# make sure intermediate files are not rm'd by make
.PRECIOUS: \
	$(UFODIR)/Inter-Black.ufo \
	$(UFODIR)/Inter-Regular.ufo \
	$(UFODIR)/Inter-Thin.ufo \
	$(UFODIR)/Inter-Light.ufo \
	$(UFODIR)/Inter-ExtraLight.ufo \
	$(UFODIR)/Inter-Medium.ufo \
	$(UFODIR)/Inter-SemiBold.ufo \
	$(UFODIR)/Inter-Bold.ufo \
	$(UFODIR)/Inter-ExtraBold.ufo \
	\
	$(UFODIR)/Inter-BlackItalic.ufo \
	$(UFODIR)/Inter-Italic.ufo \
	$(UFODIR)/Inter-ThinItalic.ufo \
	$(UFODIR)/Inter-LightItalic.ufo \
	$(UFODIR)/Inter-ExtraLightItalic.ufo \
	$(UFODIR)/Inter-MediumItalic.ufo \
	$(UFODIR)/Inter-SemiBoldItalic.ufo \
	$(UFODIR)/Inter-BoldItalic.ufo \
	$(UFODIR)/Inter-ExtraBoldItalic.ufo \
	\
	$(UFODIR)/InterDisplay-Black.ufo \
	$(UFODIR)/InterDisplay-Regular.ufo \
	$(UFODIR)/InterDisplay-Thin.ufo \
	$(UFODIR)/InterDisplay-Light.ufo \
	$(UFODIR)/InterDisplay-ExtraLight.ufo \
	$(UFODIR)/InterDisplay-Medium.ufo \
	$(UFODIR)/InterDisplay-SemiBold.ufo \
	$(UFODIR)/InterDisplay-Bold.ufo \
	$(UFODIR)/InterDisplay-ExtraBold.ufo \
	\
	$(UFODIR)/InterDisplay-BlackItalic.ufo \
	$(UFODIR)/InterDisplay-Italic.ufo \
	$(UFODIR)/InterDisplay-ThinItalic.ufo \
	$(UFODIR)/InterDisplay-LightItalic.ufo \
	$(UFODIR)/InterDisplay-ExtraLightItalic.ufo \
	$(UFODIR)/InterDisplay-MediumItalic.ufo \
	$(UFODIR)/InterDisplay-SemiBoldItalic.ufo \
	$(UFODIR)/InterDisplay-BoldItalic.ufo \
	$(UFODIR)/InterDisplay-ExtraBoldItalic.ufo \
	\
	$(UFODIR)/Inter-Roman.glyphs \
	$(UFODIR)/Inter-Italic.glyphs \
	$(UFODIR)/Inter-Roman.designspace \
	$(UFODIR)/Inter-Italic.designspace \
	$(UFODIR)/Inter-Roman.var.designspace \
	$(UFODIR)/Inter-Italic.var.designspace

# ---------------------------------------------------------------------------------
# products

# arguments to fontmake
FM_ARGS_2 := $(FM_ARGS) \
	--overlaps-backend pathops \
	--flatten-components \
	--no-autohint
ifndef DEBUG
	FM_ARGS_2 += --production-names
else
	FM_ARGS_2 += --no-production-names
endif


$(FONTDIR)/static/%.otf: $(UFODIR)/%.ufo build/features_data | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o otf --output-path $@.tmp.otf $(FM_ARGS_2)
	. $(VENV) ; psautohint -o $@ $@.tmp.otf
	@rm $@.tmp.otf

$(FONTDIR)/static/%.ttf: $(UFODIR)/%.ufo build/features_data | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o ttf --output-path $@ $(FM_ARGS_2)


AUTOHINT_ARGS := --stem-width-mode=qqq --no-info

$(FONTDIR)/static-hinted/Inter-Regular.ttf: $(FONTDIR)/static/Inter-Regular.ttf | $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/InterDisplay-Regular.ttf: $(FONTDIR)/static/InterDisplay-Regular.ttf | $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/Inter-Italic.ttf: $(FONTDIR)/static/Inter-Italic.ttf | $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/InterDisplay-Italic.ttf: $(FONTDIR)/static/InterDisplay-Italic.ttf | $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/InterDisplay-%Italic.ttf: $(FONTDIR)/static/InterDisplay-%Italic.ttf | $(FONTDIR)/static-hinted/InterDisplay-Italic.ttf $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/InterDisplay-Italic.ttf "$<" "$@"

$(FONTDIR)/static-hinted/InterDisplay-%.ttf: $(FONTDIR)/static/InterDisplay-%.ttf | $(FONTDIR)/static-hinted/InterDisplay-Regular.ttf $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/InterDisplay-Regular.ttf "$<" "$@"

$(FONTDIR)/static-hinted/Inter-%Italic.ttf: $(FONTDIR)/static/Inter-%Italic.ttf | $(FONTDIR)/static-hinted/Inter-Italic.ttf $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/Inter-Italic.ttf "$<" "$@"

$(FONTDIR)/static-hinted/Inter-%.ttf: $(FONTDIR)/static/Inter-%.ttf | $(FONTDIR)/static-hinted/Inter-Regular.ttf $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/Inter-Regular.ttf "$<" "$@"


$(FONTDIR)/var/.%.var.ttf: $(UFODIR)/%.var.designspace build/features_data | $(FONTDIR)/var venv
	. $(VENV) ; fontmake -o variable -m $< --output-path $@ $(FM_ARGS_2)

$(FONTDIR)/var/.%.var.otf: $(UFODIR)/%.var.designspace build/features_data | $(FONTDIR)/var venv
	. $(VENV) ; fontmake -o variable-cff2 -m $< --output-path $@ $(FM_ARGS_2)


%.woff2: %.ttf | venv
	. $(VENV) ; misc/tools/woff2 compress -o "$@" "$<"


$(FONTDIR)/var/InterVariable.ttf: $(FONTDIR)/var/.Inter-Roman.var.ttf misc/tools/bake-vf.py
	. $(VENV) ; python misc/tools/bake-vf.py $< -o $@

$(FONTDIR)/var/InterVariable-Italic.ttf: $(FONTDIR)/var/.Inter-Italic.var.ttf misc/tools/bake-vf.py
	. $(VENV) ; python misc/tools/bake-vf.py $< -o $@


$(FONTDIR)/static:
	mkdir -p $@
$(FONTDIR)/static-hinted:
	mkdir -p $@
$(FONTDIR)/var:
	mkdir -p $@
$(UFODIR):
	mkdir -p $@


var: \
	$(FONTDIR)/var/InterVariable.ttf \
	$(FONTDIR)/var/InterVariable-Italic.ttf

var_web: \
	$(FONTDIR)/var/InterVariable.woff2 \
	$(FONTDIR)/var/InterVariable-Italic.woff2

web: var_web static_web static_web_hinted

static: \
	$(FONTDIR)/static-hinted/Inter.ttc

STATIC_TEXT_FONTS := \
	Inter-Regular \
	Inter-Black \
	Inter-BlackItalic \
	Inter-Italic \
	Inter-Thin \
	Inter-ThinItalic \
	Inter-Light \
	Inter-LightItalic \
	Inter-ExtraLight \
	Inter-ExtraLightItalic \
	Inter-Medium \
	Inter-MediumItalic \
	Inter-SemiBold \
	Inter-SemiBoldItalic \
	Inter-Bold \
	Inter-BoldItalic \
	Inter-ExtraBold \
	Inter-ExtraBoldItalic

STATIC_DISPLAY_FONTS := \
	InterDisplay-Black \
	InterDisplay-BlackItalic \
	InterDisplay-Regular \
	InterDisplay-Italic \
	InterDisplay-Thin \
	InterDisplay-ThinItalic \
	InterDisplay-Light \
	InterDisplay-LightItalic \
	InterDisplay-ExtraLight \
	InterDisplay-ExtraLightItalic \
	InterDisplay-Medium \
	InterDisplay-MediumItalic \
	InterDisplay-SemiBold \
	InterDisplay-SemiBoldItalic \
	InterDisplay-Bold \
	InterDisplay-BoldItalic \
	InterDisplay-ExtraBold \
	InterDisplay-ExtraBoldItalic

STATIC_FONTS := $(STATIC_TEXT_FONTS) $(STATIC_DISPLAY_FONTS)
STATIC_FONTS_OTF := $(patsubst %,$(FONTDIR)/static/%.otf,$(STATIC_FONTS))
STATIC_FONTS_TTF := $(patsubst %,$(FONTDIR)/static-hinted/%.ttf,$(STATIC_FONTS))
STATIC_FONTS_WEB := $(patsubst %,$(FONTDIR)/static/%.woff2,$(STATIC_FONTS))
STATIC_FONTS_WEB_HINTED := $(patsubst %,$(FONTDIR)/static-hinted/%.woff2,$(STATIC_FONTS))

$(FONTDIR)/static/Inter.otc: $(STATIC_FONTS_OTF)
	. $(VENV) ; python -m fontTools.ttLib.__main__ -o $@ $^

$(FONTDIR)/static-hinted/Inter.ttc: $(STATIC_FONTS_TTF)
	. $(VENV) ; python -m fontTools.ttLib.__main__ -o $@ $^

static_otf: $(STATIC_FONTS_OTF)
static_ttf: $(STATIC_FONTS_TTF)
static_web: $(STATIC_FONTS_WEB)
static_web_hinted: $(STATIC_FONTS_WEB_HINTED)

all: var static web static_otf

.PHONY: \
	all var var_web web \
	static static_otf static_ttf static_web static_web_hinted

# ---------------------------------------------------------------------------------
# testing

test: test_var test_static
test_var: \
	build/fontbakery-report-var.txt
test_static: \
	build/fontbakery-report-text.txt \
  build/fontbakery-report-display.txt

# disabled fontbakery tests:
FBAKE_DISABLED =
FBAKE_DISABLED_STATIC =

FBAKE_DISABLED += com.google.fonts/check/fontbakery_version
# Calls a server to see if there's a newer version of fontbakery and
# FAILs if there is. This breaks reproducible builds.

FBAKE_DISABLED += com.google.fonts/check/family/win_ascent_and_descent
# "FAIL OS/2.usWinAscent value should be equal or greater than 2269,
#  but got 1984 instead"
# "FAIL OS/2.usWinDescent value should be equal or greater than 660,
#  but got 494 instead"


FBAKE_DISABLED_STATIC += com.google.fonts/check/family/underline_thickness
# "Fonts have consistent underline thickness"
# Inter explicitly have varying underline thickness, matching wght

FBAKE_DISABLED_STATIC += com.google.fonts/check/contour_count
# This test is pedantic; generates warnings when the number of contours are different
# than what is usually seen in other fonts. No real world impact.

# The following test are minor issues, left enabled for the var tests
# but disabled for the static tests to reduce noise

FBAKE_DISABLED_STATIC += com.google.fonts/check/legacy_accents
# "Glyph <NAME> has a legacy accent component (hungarumlaut)"
# TODO: improve the design of Hungar* composite glyphs to use marks

FBAKE_DISABLED_STATIC += com.google.fonts/check/gdef_mark_chars
# "Check mark characters are in GDEF mark glyph class"
# "WARN The following mark characters could be in the GDEF mark glyph
#  class: uni0488 (U+0488), uni0489 (U+0489), uni20DD (U+20DD), uni20DE (U+20DE)"

FBAKE_DISABLED_STATIC += com.google.fonts/check/gdef_spacing_marks
# "Check glyphs in mark glyph class are non-spacing"
# "WARN The following spacing glyphs may be in the GDEF mark glyph class by mistake:
#  dotbelow (U+0323)

# FBAKE_ARGS are common args for all fontbakery targets
FBAKE_ARGS = \
	check-universal \
	--no-colors \
	--no-progress \
	--loglevel WARN \
	--succinct \
	--full-lists \
	-j \
	$(patsubst %,-x %,$(FBAKE_DISABLED))

FBAKE_ARGS_STATIC = $(FBAKE_ARGS) $(patsubst %,-x %,$(FBAKE_DISABLED_STATIC))

STATIC_TEXT_FONTS_TTF = $(patsubst %,$(FONTDIR)/static-hinted/%.ttf,$(STATIC_TEXT_FONTS))
STATIC_DISPLAY_FONTS_TTF = $(patsubst %,$(FONTDIR)/static-hinted/%.ttf,$(STATIC_DISPLAY_FONTS))

build/fontbakery-report-var.txt: $(FONTDIR)/var/InterVariable.ttf $(FONTDIR)/var/InterVariable-Italic.ttf | venv
	@echo "fontbakery InterVariable -> $(@) ..."
	@. $(VENV) ; fontbakery $(FBAKE_ARGS) $^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)
	@echo "fontbakery InterVariable: PASS"
	@grep -E -A7 '^Total:' $@ | tail -6 | sed -E 's/^ +/  /g'

build/fontbakery-report-text.txt: $(STATIC_TEXT_FONTS_TTF) | venv
	@echo "fontbakery Inter -> $@ ..."
	@. $(VENV) ; fontbakery $(FBAKE_ARGS_STATIC) $^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)
	@echo "fontbakery Inter: PASS"
	@grep -E -A7 '^Total:' $@ | tail -6 | sed -E 's/^ +/  /g'

build/fontbakery-report-display.txt: $(STATIC_DISPLAY_FONTS_TTF) | venv
	@echo "fontbakery InterDisplay -> $@ ..."
	@. $(VENV) ; fontbakery $(FBAKE_ARGS_STATIC) $^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)
	@echo "fontbakery InterDisplay: PASS"
	@grep -E -A7 '^Total:' $@ | tail -6 | sed -E 's/^ +/  /g'

.PHONY: test test_var

# ---------------------------------------------------------------------------------
# zip

zip: all
	bash misc/makezip2.sh -reveal-in-finder \
		"build/release/Inter-$(VERSION)-$(shell git rev-parse --short=10 HEAD).zip"

zip_beta: \
		$(FONTDIR)/var/InterVariable.ttf \
		$(FONTDIR)/var/InterVariable.woff2 \
		$(FONTDIR)/var/InterVariable-Italic.ttf \
		$(FONTDIR)/var/InterVariable-Italic.woff2
	mkdir -p build/release
	zip -j -q -X "build/release/Inter_beta-$(VERSION)-$(shell date '+%Y%m%d_%H%M')-$(shell git rev-parse --short=10 HEAD).zip" $^

.PHONY: zip zip_beta

# ---------------------------------------------------------------------------------
# distribution
# - preflight checks for existing version archive and dirty git state.
# - step1 rebuilds from scratch, since font version & ID is based on git hash.
# - step2 runs tests, then makes a zip archive and updates the website (docs/ dir.)

DIST_ZIP = build/release/Inter-${VERSION}.zip

dist:
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
	$(MAKE) -f $(MAKEFILE) -j$(nproc) clean
	$(MAKE) -f $(MAKEFILE) -j$(nproc) all
	$(MAKE) -f $(MAKEFILE) -j$(nproc) test
	$(MAKE) -f $(MAKEFILE) -j$(nproc) dist_zip dist_docs
	$(MAKE) -f $(MAKEFILE) dist_postflight

dist_zip: | venv
	@#. $(VENV) ; python misc/tools/patch-version.py misc/dist/inter.css
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

install: install_var install_ttf

install_var: \
	$(INSTALLDIR)/InterVariable.ttf \
	$(INSTALLDIR)/InterVariable-Italic.ttf

install_ttf: $(INSTALLDIR)/Inter.ttc
install_otf: $(INSTALLDIR)/Inter.otc

$(INSTALLDIR)/%.ttc: $(FONTDIR)/static-hinted/%.ttc | $(INSTALLDIR)
	@# remove conflicting OTF fonts
	rm -f $(INSTALLDIR)/Inter*.otf $(INSTALLDIR)/Inter*.otc
	cp -a $^ $@

$(INSTALLDIR)/%.otc: $(FONTDIR)/static/%.otc | $(INSTALLDIR)
	@# remove conflicting TTF fonts
	@rm -fv $(INSTALLDIR)/Inter*.ttc
	cp -a $^ $@

$(INSTALLDIR)/InterVariable.ttf: $(FONTDIR)/var/InterVariable.ttf | $(INSTALLDIR)
	@# remove font with legacy name
	@rm -fv $(INSTALLDIR)/InterVariable.ttf
	cp -a $^ $@

$(INSTALLDIR)/InterVariable-Italic.ttf: $(FONTDIR)/var/InterVariable-Italic.ttf | $(INSTALLDIR)
	@# remove font with legacy name
	@rm -fv $(INSTALLDIR)/InterVariable-Italic.ttf
	cp -a $^ $@

$(INSTALLDIR)/%.otf: $(FONTDIR)/static/%.otf | $(INSTALLDIR)
	@# remove conflicting TTF fonts
	rm -f $(INSTALLDIR)/{Inter,InterDisplay}-*.ttf
	cp -a $^ $@

$(INSTALLDIR):
	mkdir -p $@

.PHONY: install install_var install_ttf install_otf

# ---------------------------------------------------------------------------------
# debug

build/ttx/Inter-Var%: $(FONTDIR)/var/Inter-Var%.ttf
	rm -rf "build/ttx/$(basename $(notdir $^))"
	mkdir -p "build/ttx/$(basename $(notdir $^))"
	cp $^ "build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	ttx -x glyf -x GPOS -x GSUB -x gvar -i -f -s \
		"build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	@echo "Dumped $(notdir $^) to build/ttx/$(basename $(notdir $^))/"

build/ttx/%: $(FONTDIR)/static/%.ttf
	rm -rf "build/ttx/$(basename $(notdir $^))"
	mkdir -p "build/ttx/$(basename $(notdir $^))"
	cp $^ "build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	ttx -x glyf -x GPOS -x GSUB -i -f -s "build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	@echo "Dumped $(notdir $^) to build/ttx/$(basename $(notdir $^))/"

ttx_var_roman: build/ttx/InterVariable
ttx_var_italic: build/ttx/InterVariable-Italic
ttx_var: ttx_var_roman ttx_var_italic
ttx_static: $(patsubst %,build/ttx/%,$(STATIC_FONTS))

.PHONY: ttx_var ttx_var_roman ttx_var_italic ttx_static

# ---------------------------------------------------------------------------------
# misc

clean:
	@for f in build/tmp build/fonts build/ufo build/googlefonts build/ttx; do \
		[ ! -e $$f ] || echo "rm -rf $$f"; (rm -rf $$f; rm -rf $$f) & \
	done; wait

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

venv: build/venv/config2.stamp

build/venv/config2.stamp: Pipfile.lock Pipfile
	@mkdir -p build
	[ ! -f build/venv/config.stamp ] || rm -rf build/venv
	[ -d build/venv ] || python3 -m venv build/venv
	. $(VENV) ; pip install pipenv==2023.8.28
	. $(VENV) ; pipenv install
	touch $@

venv-update:
	. $(VENV) ; pipenv update

reset: clean
	rm -rf build/venv

.PHONY: venv venv-update reset
