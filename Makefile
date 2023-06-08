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
$(UFODIR)/%.var.designspace: $(UFODIR)/%.designspace | venv
	. $(VENV) ; python misc/tools/gen-var-designspace.py $< $@

$(UFODIR)/%.designspace: $(UFODIR)/%.glyphs $(UFODIR)/features | venv
	. $(VENV) ; fontmake $(FM_ARGS) -o ufo -g $< --designspace-path $@ \
		  --master-dir $(UFODIR) --instance-dir $(UFODIR)
	. $(VENV) ; python misc/tools/postprocess-designspace.py $@

# instance UFOs from designspace
$(UFODIR)/Inter%Italic.ufo: $(UFODIR)/Inter-Italic.designspace | venv
	. $(VENV) ; bash misc/tools/gen-instance-ufo.sh $< $@
$(UFODIR)/Inter%.ufo: $(UFODIR)/Inter-Roman.designspace | venv
	. $(VENV) ; bash misc/tools/gen-instance-ufo.sh $< $@

# designspace & master UFOs (for editing)
build/ufo-editable/%.designspace: $(UFODIR)/%.glyphs $(UFODIR)/features | venv
	@mkdir -p $(dir $@)
	. $(VENV) ; fontmake $(FM_ARGS) -o ufo -g $< --designspace-path $@ \
		  --master-dir $(dir $@) --instance-dir $(dir $@)
	. $(VENV) ; python misc/tools/postprocess-designspace.py --editable $@

# instance UFOs from designspace (for editing)
build/ufo-editable/Inter%Italic.ufo: build/ufo-editable/Inter-Italic.designspace | venv
	. $(VENV) ; bash misc/tools/gen-instance-ufo.sh $< $@
build/ufo-editable/Inter%.ufo: build/ufo-editable/Inter-Roman.designspace | venv
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

$(FONTDIR)/static/InterDisplay-%.otf: $(UFODIR)/InterDisplay-%.ufo build/features_data | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o otf --output-path $@ $(FM_ARGS_2)
	. $(VENV) ; python misc/tools/fix-static-display-names.py $@

$(FONTDIR)/static/%.otf: $(UFODIR)/%.ufo build/features_data | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o otf --output-path $@ $(FM_ARGS_2)


$(FONTDIR)/static/InterDisplay-%.ttf: $(UFODIR)/InterDisplay-%.ufo build/features_data | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o ttf --output-path $@ $(FM_ARGS_2)

$(FONTDIR)/static/%.ttf: $(UFODIR)/%.ufo build/features_data | $(FONTDIR)/static venv
	. $(VENV) ; fontmake -u $< -o ttf --output-path $@ $(FM_ARGS_2)


$(FONTDIR)/static-hinted/%.ttf: $(FONTDIR)/static/%.ttf | $(FONTDIR)/static/Inter-Regular.ttf $(FONTDIR)/static-hinted venv
	. $(VENV) ; python -m ttfautohint \
	  --windows-compatibility \
	  --reference $(FONTDIR)/static/Inter-Regular.ttf \
	  --no-info \
	  "$<" "$@"

$(FONTDIR)/var/.%.var.ttf: $(UFODIR)/%.var.designspace build/features_data | $(FONTDIR)/var venv
	. $(VENV) ; fontmake -o variable -m $< --output-path $@ $(FM_ARGS_2)

$(FONTDIR)/var/.%.var.otf: $(UFODIR)/%.var.designspace build/features_data | $(FONTDIR)/var venv
	. $(VENV) ; fontmake -o variable-cff2 -m $< --output-path $@ $(FM_ARGS_2)


%.woff2: %.ttf | venv
	. $(VENV) ; misc/tools/woff2 compress -o "$@" "$<"


$(FONTDIR)/var/Inter-Variable.ttf: $(FONTDIR)/var/.Inter-Roman.var.ttf
	. $(VENV) ; python misc/tools/bake-vf.py $^ -o $@

$(FONTDIR)/var/Inter-Variable-Italic.ttf: $(FONTDIR)/var/.Inter-Italic.var.ttf
	. $(VENV) ; python misc/tools/bake-vf.py $^ -o $@


$(FONTDIR)/static:
	mkdir -p $@
$(FONTDIR)/static-hinted:
	mkdir -p $@
$(FONTDIR)/var:
	mkdir -p $@
$(UFODIR):
	mkdir -p $@


var: \
	$(FONTDIR)/var/Inter-Variable.ttf \
	$(FONTDIR)/var/Inter-Variable-Italic.ttf

var_web: \
	$(FONTDIR)/var/Inter-Variable.woff2 \
	$(FONTDIR)/var/Inter-Variable-Italic.woff2

web: var_web static_web

static: \
	$(FONTDIR)/static-hinted/Inter.ttc

$(FONTDIR)/static/Inter.otc: \
	$(FONTDIR)/static/Inter-Regular.otf \
	$(FONTDIR)/static/Inter-Black.otf \
	$(FONTDIR)/static/Inter-BlackItalic.otf \
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
	$(FONTDIR)/static/Inter-ExtraBoldItalic.otf \
	$(FONTDIR)/static/InterDisplay-Black.otf \
	$(FONTDIR)/static/InterDisplay-BlackItalic.otf \
	$(FONTDIR)/static/InterDisplay-Regular.otf \
	$(FONTDIR)/static/InterDisplay-Italic.otf \
	$(FONTDIR)/static/InterDisplay-Thin.otf \
	$(FONTDIR)/static/InterDisplay-ThinItalic.otf \
	$(FONTDIR)/static/InterDisplay-Light.otf \
	$(FONTDIR)/static/InterDisplay-LightItalic.otf \
	$(FONTDIR)/static/InterDisplay-ExtraLight.otf \
	$(FONTDIR)/static/InterDisplay-ExtraLightItalic.otf \
	$(FONTDIR)/static/InterDisplay-Medium.otf \
	$(FONTDIR)/static/InterDisplay-MediumItalic.otf \
	$(FONTDIR)/static/InterDisplay-SemiBold.otf \
	$(FONTDIR)/static/InterDisplay-SemiBoldItalic.otf \
	$(FONTDIR)/static/InterDisplay-Bold.otf \
	$(FONTDIR)/static/InterDisplay-BoldItalic.otf \
	$(FONTDIR)/static/InterDisplay-ExtraBold.otf \
	$(FONTDIR)/static/InterDisplay-ExtraBoldItalic.otf
	. $(VENV) ; python -m fontTools.ttLib.__init__ -o $@ $^

$(FONTDIR)/static-hinted/Inter.ttc: \
	$(FONTDIR)/static-hinted/Inter-Regular.ttf \
	$(FONTDIR)/static-hinted/Inter-Black.ttf \
	$(FONTDIR)/static-hinted/Inter-BlackItalic.ttf \
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
	$(FONTDIR)/static-hinted/Inter-ExtraBoldItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Black.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-BlackItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Regular.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Italic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Thin.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ThinItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Light.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-LightItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraLight.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraLightItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Medium.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-MediumItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-SemiBold.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-SemiBoldItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Bold.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-BoldItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraBold.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraBoldItalic.ttf
	. $(VENV) ; python -m fontTools.ttLib.__init__ -o $@ $^

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
	$(FONTDIR)/static/Inter-ExtraBoldItalic.otf \
	$(FONTDIR)/static/InterDisplay-Black.otf \
	$(FONTDIR)/static/InterDisplay-BlackItalic.otf \
	$(FONTDIR)/static/InterDisplay-Regular.otf \
	$(FONTDIR)/static/InterDisplay-Italic.otf \
	$(FONTDIR)/static/InterDisplay-Thin.otf \
	$(FONTDIR)/static/InterDisplay-ThinItalic.otf \
	$(FONTDIR)/static/InterDisplay-Light.otf \
	$(FONTDIR)/static/InterDisplay-LightItalic.otf \
	$(FONTDIR)/static/InterDisplay-ExtraLight.otf \
	$(FONTDIR)/static/InterDisplay-ExtraLightItalic.otf \
	$(FONTDIR)/static/InterDisplay-Medium.otf \
	$(FONTDIR)/static/InterDisplay-MediumItalic.otf \
	$(FONTDIR)/static/InterDisplay-SemiBold.otf \
	$(FONTDIR)/static/InterDisplay-SemiBoldItalic.otf \
	$(FONTDIR)/static/InterDisplay-Bold.otf \
	$(FONTDIR)/static/InterDisplay-BoldItalic.otf \
	$(FONTDIR)/static/InterDisplay-ExtraBold.otf \
	$(FONTDIR)/static/InterDisplay-ExtraBoldItalic.otf

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
	$(FONTDIR)/static/Inter-ExtraBoldItalic.ttf \
	$(FONTDIR)/static/InterDisplay-Black.ttf \
	$(FONTDIR)/static/InterDisplay-BlackItalic.ttf \
	$(FONTDIR)/static/InterDisplay-Regular.ttf \
	$(FONTDIR)/static/InterDisplay-Italic.ttf \
	$(FONTDIR)/static/InterDisplay-Thin.ttf \
	$(FONTDIR)/static/InterDisplay-ThinItalic.ttf \
	$(FONTDIR)/static/InterDisplay-Light.ttf \
	$(FONTDIR)/static/InterDisplay-LightItalic.ttf \
	$(FONTDIR)/static/InterDisplay-ExtraLight.ttf \
	$(FONTDIR)/static/InterDisplay-ExtraLightItalic.ttf \
	$(FONTDIR)/static/InterDisplay-Medium.ttf \
	$(FONTDIR)/static/InterDisplay-MediumItalic.ttf \
	$(FONTDIR)/static/InterDisplay-SemiBold.ttf \
	$(FONTDIR)/static/InterDisplay-SemiBoldItalic.ttf \
	$(FONTDIR)/static/InterDisplay-Bold.ttf \
	$(FONTDIR)/static/InterDisplay-BoldItalic.ttf \
	$(FONTDIR)/static/InterDisplay-ExtraBold.ttf \
	$(FONTDIR)/static/InterDisplay-ExtraBoldItalic.ttf

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
	$(FONTDIR)/static-hinted/Inter-ExtraBoldItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Black.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-BlackItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Regular.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Italic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Thin.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ThinItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Light.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-LightItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraLight.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraLightItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Medium.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-MediumItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-SemiBold.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-SemiBoldItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-Bold.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-BoldItalic.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraBold.ttf \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraBoldItalic.ttf

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
	$(FONTDIR)/static/Inter-ExtraBoldItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Black.woff2 \
	$(FONTDIR)/static/InterDisplay-BlackItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Regular.woff2 \
	$(FONTDIR)/static/InterDisplay-Italic.woff2 \
	$(FONTDIR)/static/InterDisplay-Thin.woff2 \
	$(FONTDIR)/static/InterDisplay-ThinItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Light.woff2 \
	$(FONTDIR)/static/InterDisplay-LightItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraLight.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraLightItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Medium.woff2 \
	$(FONTDIR)/static/InterDisplay-MediumItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-SemiBold.woff2 \
	$(FONTDIR)/static/InterDisplay-SemiBoldItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-Bold.woff2 \
	$(FONTDIR)/static/InterDisplay-BoldItalic.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraBold.woff2 \
	$(FONTDIR)/static/InterDisplay-ExtraBoldItalic.woff2

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
	$(FONTDIR)/static-hinted/Inter-ExtraBoldItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-Black.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-BlackItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-Regular.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-Italic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-Thin.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-ThinItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-Light.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-LightItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraLight.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraLightItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-Medium.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-MediumItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-SemiBold.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-SemiBoldItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-Bold.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-BoldItalic.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraBold.woff2 \
	$(FONTDIR)/static-hinted/InterDisplay-ExtraBoldItalic.woff2


all: var static web static_otf static_ttf_hinted static_web_hinted

.PHONY: \
	all var var_web web \
	static static_otf static_ttf static_ttf_hinted static_web static_web_hinted

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

build/fontbakery-report-var.txt: \
		$(FONTDIR)/var/Inter-Variable.ttf \
		$(FONTDIR)/var/Inter-Variable-Italic.ttf \
		| venv
	@echo "fontbakery {Inter-Variable,Inter-Variable-Italic}.ttf > $(@) ..."
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

zip_beta: \
		$(FONTDIR)/var/Inter-Variable.ttf \
		$(FONTDIR)/var/Inter-Variable.woff2 \
		$(FONTDIR)/var/Inter-Variable-Italic.ttf \
		$(FONTDIR)/var/Inter-Variable-Italic.woff2
	mkdir -p build/release
	zip -j -q -X "build/release/Inter_beta-$(VERSION)-$(shell date '+%Y%m%d_%H%M')-$(shell git rev-parse --short=10 HEAD).zip" $^

.PHONY: zip zip_beta

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

install: install_var $(INSTALLDIR)/Inter.ttc | install_clean_otf

install_clean_otf:
	@# Remove any old pre-ttc fonts
	rm -rf $(INSTALLDIR)/Inter*.otf

install_var: \
	$(INSTALLDIR)/Inter-Variable.ttf \
	$(INSTALLDIR)/Inter-Variable-Italic.ttf

$(INSTALLDIR)/%.ttc: $(FONTDIR)/static-hinted/%.ttc | $(INSTALLDIR)
	cp -a $^ $@

$(INSTALLDIR)/%.otc: $(FONTDIR)/static/%.otc | $(INSTALLDIR)
	cp -a $^ $@

$(INSTALLDIR)/Inter-Variable.ttf: $(FONTDIR)/var/Inter-Variable.ttf | $(INSTALLDIR)
	cp -a $^ $@

$(INSTALLDIR)/Inter-Variable-Italic.ttf: $(FONTDIR)/var/Inter-Variable-Italic.ttf | $(INSTALLDIR)
	cp -a $^ $@

$(INSTALLDIR)/%.otf: $(FONTDIR)/static/%.otf | $(INSTALLDIR)
	cp -a $^ $@

$(INSTALLDIR):
	mkdir -p $@

.PHONY: install install_var install_clean_otf

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

ttx_var_roman: build/ttx/Inter-Variable
ttx_var_italic: build/ttx/Inter-Variable-Italic
ttx_var: ttx_var_roman ttx_var_italic
ttx_static: \
	build/ttx/Inter-Black.ttx \
	build/ttx/Inter-BlackItalic.ttx \
	build/ttx/Inter-Regular.ttx \
	build/ttx/Inter-Italic.ttx \
	build/ttx/Inter-Thin.ttx \
	build/ttx/Inter-ThinItalic.ttx \
	build/ttx/Inter-Light.ttx \
	build/ttx/Inter-LightItalic.ttx \
	build/ttx/Inter-ExtraLight.ttx \
	build/ttx/Inter-ExtraLightItalic.ttx \
	build/ttx/Inter-Medium.ttx \
	build/ttx/Inter-MediumItalic.ttx \
	build/ttx/Inter-SemiBold.ttx \
	build/ttx/Inter-SemiBoldItalic.ttx \
	build/ttx/Inter-Bold.ttx \
	build/ttx/Inter-BoldItalic.ttx \
	build/ttx/Inter-ExtraBold.ttx \
	build/ttx/Inter-ExtraBoldItalic.ttx \
	build/ttx/InterDisplay-Black.ttx \
	build/ttx/InterDisplay-BlackItalic.ttx \
	build/ttx/InterDisplay-Regular.ttx \
	build/ttx/InterDisplay-Italic.ttx \
	build/ttx/InterDisplay-Thin.ttx \
	build/ttx/InterDisplay-ThinItalic.ttx \
	build/ttx/InterDisplay-Light.ttx \
	build/ttx/InterDisplay-LightItalic.ttx \
	build/ttx/InterDisplay-ExtraLight.ttx \
	build/ttx/InterDisplay-ExtraLightItalic.ttx \
	build/ttx/InterDisplay-Medium.ttx \
	build/ttx/InterDisplay-MediumItalic.ttx \
	build/ttx/InterDisplay-SemiBold.ttx \
	build/ttx/InterDisplay-SemiBoldItalic.ttx \
	build/ttx/InterDisplay-Bold.ttx \
	build/ttx/InterDisplay-BoldItalic.ttx \
	build/ttx/InterDisplay-ExtraBold.ttx \
	build/ttx/InterDisplay-ExtraBoldItalic.ttx

.PHONY: ttx_var ttx_var_roman ttx_var_italic ttx_static

# ---------------------------------------------------------------------------------
# misc

clean:
	rm -rf build/tmp build/fonts build/ufo build/googlefonts build/ttx || true
	rm -rf build/tmp build/fonts build/ufo build/googlefonts build/ttx

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
	. $(VENV) ; pip install pipenv
	. $(VENV) ; pipenv install
	touch $@

venv-update:
	. $(VENV) ; pipenv update

reset: clean
	rm -rf build/venv

.PHONY: venv venv-update reset
