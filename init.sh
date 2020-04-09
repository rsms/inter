#!/bin/bash

SRCDIR=$(dirname "${BASH_SOURCE[0]}")
BUILD_DIR=$SRCDIR/build

if [[ "${BUILD_DIR:0:2}" == "./" ]]; then
  BUILD_DIR=${BUILD_DIR:2}
fi

# DIST_DIR=$BUILD_DIR/fonts/
DIST_DIR_TOK='$(FONTDIR)/'
BUILD_TMP_DIR=$BUILD_DIR/tmp
VENV_DIR=$BUILD_DIR/venv

if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  # sourced
  if [[ -z $VIRTUAL_ENV ]] && [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    echo "Project not configured." >&2
    echo "Execute this script instead of sourcing it to perform setup." >&2
  else
    source "$VENV_DIR/bin/activate"
    pushd "$SRCDIR" >/dev/null
    SRCDIR_ABS=$(pwd)
    popd >/dev/null
    export PYTHONPATH=$SRCDIR_ABS/misc/tools
  fi
else
  # Subshell
  set -e
  cd "$SRCDIR"

  if [[ "$1" == "-h" ]] || [[ "$1" == "-help" ]] || [[ "$1" == "--help" ]]; then
    echo "usage: $0 [options]" >&2
    echo "options:" >&2
    echo "  -clean     Start from scratch" >&2
    echo "  -h, -help  Show help and exit" >&2
    exit 1
  fi

  clean=false
  if [[ "$1" == "-clean" ]]; then
    clean=true
    shift
  fi

  platform=osx
  UNAME=$(uname)
  if [[ "$UNAME" == *"inux"* ]]; then
    platform=linux
  elif [[ "$UNAME" != *"arwin"* ]]; then
    echo "Unsupported platform $UNAME (only macOS and Linux are supported)" >&2
    exit 1
  fi


  # ——————————————————————————————————————————————————————————————————
  # git hooks
  if [ -d .git ] && [ -d misc/git-hooks ]; then
    mkdir -p .git/hooks
    pushd .git/hooks >/dev/null
    for f in ../../misc/git-hooks/*.sh; do
      HOOKFILE=$(basename "$f" .sh)
      if ! [ -f "$HOOKFILE" ]; then
        ln -vfs "$f" "$HOOKFILE"
      fi
    done
    popd >/dev/null
  fi


  # ——————————————————————————————————————————————————————————————————
  # virtualenv

  mkdir -p "$VENV_DIR"

  pushd "$(dirname "$VENV_DIR")" >/dev/null
  VENV_DIR_ABS=$(pwd)/$(basename "$VENV_DIR")
  popd >/dev/null

  # must check and set VENV_ACTIVE before polluting local env
  VENV_ACTIVE=false
  if [[ "$VIRTUAL_ENV" == "$VENV_DIR_ABS" ]] && [[ "$1" != "-force" ]]; then
    VENV_ACTIVE=true
  fi

  require_virtualenv() {
    # find pip3 (Python 3)
    export pip=$(which pip3)
    if [ "$pip" = "" ]; then
      export pip=$(which pip)
      if [ "$pip" = "" ]; then
        echo "pip not found in PATH -- please install Python 3" >&2
        exit 1
      fi
    fi
    echo "using $("$pip" --version)"
    if [ "$pip" = "" ]; then
      echo "Pip for Python 3 not found (tried pip and pip3 in PATH)" >&2
      exit 1
    elif ! ($pip --version 2>&1 | grep -q 'ython 3'); then
      echo "Pip for Python 3 not found (found pip for different python version)" >&2
      exit 1
    fi
    # find virtualenv
    if ! ($pip show virtualenv >/dev/null); then
      echo "$0: Can't find virtualenv -- install through '$pip install --user virtualenv'" >&2
      exit 1
    fi
    virtualenv_pkgdir=$($pip show virtualenv | grep Location | cut -d ' ' -f 2)
    export virtualenv="$(dirname "$(dirname "$(dirname "$virtualenv_pkgdir")")")/bin/virtualenv"
    echo "using virtualenv: $virtualenv"
  }

  # TODO: allow setting a flag to recreate venv
  if $clean; then
    rm -rf "$VENV_DIR"
  fi

  if [[ ! -d "$VENV_DIR/bin" ]]; then
    require_virtualenv
    echo "Setting up virtualenv in '$VENV_DIR'"
    rm -f "$VENV_DIR/lib/python"
    $virtualenv "$VENV_DIR"
  elif [[ ! -z $VIRTUAL_ENV ]] && [[ "$VIRTUAL_ENV" != "$VENV_DIR_ABS" ]]; then
    echo "Looks like the repository has moved location -- updating virtualenv"
    rm -f "$VENV_DIR/lib/python"
    require_virtualenv
    $virtualenv "$VENV_DIR"
  fi

  # symlink lib/python -> lib/python<version>
  if [[ ! -d "$VENV_DIR/lib/python" ]]; then
    for f in "$VENV_DIR/lib/"python*; do
      if [[ -d "$f" ]]; then
        ln -svf $(basename "$f") "$VENV_DIR/lib/python"
        break
      fi
    done
  fi


  # ——————————————————————————————————————————————————————————————————
  # python dependencies

  # install if deps changed
  REQUIREMENTS_FILE=$SRCDIR/requirements.txt
  UPDATE_TIMESTAMP_FILE="$VENV_DIR/last-pip-run.mark"
  if [ "$REQUIREMENTS_FILE" -nt "$UPDATE_TIMESTAMP_FILE" ]; then
    echo "$VENV_DIR/bin/pip install -r $REQUIREMENTS_FILE"
    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"
    date '+%s' > "$UPDATE_TIMESTAMP_FILE"
  fi


  # ——————————————————————————————————————————————————————————————————
  # activate env (for rest of this script)
  source "$VENV_DIR/bin/activate"


  # ——————————————————————————————————————————————————————————————————
  # other toolchain dependencies

  DEPS_DIR=$BUILD_DIR/deps
  PATCH_DIR=$(pwd)/misc/patches
  mkdir -p "$DEPS_DIR"


  function fetch() {
    URL=$1
    DSTFILE=$2
    echo "Fetching $URL"
    curl '-#' -o "$DSTFILE" -L "$URL"
  }

  function check_dep() {
    NAME=$1
    REPO_URL=$2
    BRANCH=$3
    TREE_REF=$4
    set -e
    REPODIR=$DEPS_DIR/$NAME
    CHANGED=false
    if [[ ! -d "$REPODIR/.git" ]]; then
      rm -rf "$REPODIR"
      echo "Fetching $NAME from $REPO_URL"
      if ! (git clone --recursive --single-branch -b $BRANCH -- "$REPO_URL" "$REPODIR"); then
        exit 1
      fi
      CHANGED=true
    elif [[ "$(git -C "$REPODIR" rev-parse HEAD)" != "$TREE_REF" ]]; then
      CHANGED=true
      git -C "$REPODIR" fetch origin
    fi
    if $CHANGED; then
      if [[ ! -z $TREE_REF ]]; then
        git -C "$REPODIR" checkout "$TREE_REF"
        git -C "$REPODIR" submodule update
      fi
      return 1
    fi
    return 0
  }


  # woff2
  LINK=false
  if ! (check_dep woff2 \
    https://github.com/google/woff2.git master \
    a0d0ed7da27b708c0a4e96ad7a998bddc933c06e )
  then
    echo "Building woff2"
    make -C "$DEPS_DIR/woff2" -j8 clean
    if !(make -C "$DEPS_DIR/woff2" -j8 all); then
      rm -rf "$DEPS_DIR/woff2"
      exit 1
    fi
    LINK=true
  elif [[ ! -f "$VENV_DIR/bin/woff2_compress" ]]; then
    LINK=true
  fi
  if $LINK; then
    ln -vfs ../../deps/woff2/woff2_compress "$VENV_DIR/bin/woff2_compress"
  fi


  # # EOT (disabled)
  # if ! (check_dep \
  #   ttf2eot https://github.com/rsms/ttf2eot.git master )
  # then
  #   echo "Building ttf2eot"
  #   make -C "$DEPS_DIR/ttf2eot" clean all
  # fi
  # if [[ ! -f "$VENV_DIR/bin/ttf2eot" ]]; then
  #   ln -vfs ../../deps/ttf2eot/ttf2eot "$VENV_DIR/bin"
  # fi


  # # meson (internal requirement of ots)
  # MESON_VERSION=0.47.2
  # pushd "$DEPS_DIR" >/dev/null
  # MESON_BIN=$PWD/meson-${MESON_VERSION}/meson.py
  # popd >/dev/null
  # if [[ ! -f "$MESON_BIN" ]]; then
  #   fetch \
  #     https://github.com/mesonbuild/meson/releases/download/${MESON_VERSION}/meson-${MESON_VERSION}.tar.gz \
  #     "$DEPS_DIR/meson.tar.gz"
  #   tar -C "$DEPS_DIR" -xzf "$DEPS_DIR/meson.tar.gz"
  #   rm "$DEPS_DIR/meson.tar.gz"
  # fi


  # # ninja
  # NINJA_VERSION=1.8.2
  # pushd "$DEPS_DIR" >/dev/null
  # NINJA_BIN=$PWD/ninja-${NINJA_VERSION}
  # if [[ ! -f "$NINJA_BIN" ]]; then
  #   fetch \
  #     https://github.com/ninja-build/ninja/releases/download/v${NINJA_VERSION}/ninja-mac.zip \
  #     ninja.zip
  #   rm -f ninja
  #   unzip -q -o ninja.zip
  #   rm ninja.zip
  #   mv ninja "$NINJA_BIN"
  # fi
  # popd >/dev/null


  # # ots (from source)
  # LINK=false
  # if ! (check_dep ots \
  #   https://github.com/khaledhosny/ots.git master \
  #   cad0b4f9405d03ddf801f977f2f65892192ad047 )
  # then
  #   echo "Building ots"
  #   pushd "$DEPS_DIR/ots" >/dev/null
  #   "$MESON_BIN" build
  #   "$NINJA_BIN" -C build
  #   popd >/dev/null
  # fi


  # ots (from dist)
  OTS_VERSION=7.1.7
  OTS_DIR=$DEPS_DIR/ots-${OTS_VERSION}
  LINK=false
  if [[ ! -f "$OTS_DIR/ots-sanitize" ]]; then
    mkdir -p "$OTS_DIR"
    fetch \
      https://github.com/khaledhosny/ots/releases/download/v${OTS_VERSION}/ots-${OTS_VERSION}-${platform}.zip \
      "$OTS_DIR/ots.zip"
    pushd "$OTS_DIR" >/dev/null
    unzip ots.zip
    rm ots.zip
    mv ots-* xx-ots
    mv xx-ots/* .
    rm -rf xx-ots
    popd >/dev/null
    LINK=true
  fi
  if $LINK || [[ ! -f "$VENV_DIR/bin/ots-sanitize" ]]; then
    pushd "$OTS_DIR" >/dev/null
    for f in ots-*; do
      popd >/dev/null
      ln -vfs ../../deps/ots-${OTS_VERSION}/$f "$VENV_DIR/bin/$f"
      pushd "$OTS_DIR" >/dev/null
    done
    popd >/dev/null
  fi


  AUTOHINT_VERSION=1.8.2
  AUTOHINT_SRC_VERSION=1.8.2.8
  LINK=false
  if [[ ! -f "$DEPS_DIR/ttfautohint-${AUTOHINT_VERSION}" ]]; then
    if [[ "$platform" == "osx" ]]; then
      fetch \
        https://download.savannah.gnu.org/releases/freetype/ttfautohint-${AUTOHINT_VERSION}-tty-osx.tar.gz \
        "$DEPS_DIR/ttfautohint.tar.gz"
      tar -C "$DEPS_DIR" -xzf "$DEPS_DIR/ttfautohint.tar.gz"
      rm "$DEPS_DIR/ttfautohint.tar.gz"
      mv -f "$DEPS_DIR/ttfautohint" "$DEPS_DIR/ttfautohint-${AUTOHINT_VERSION}"
    else
      fetch \
        https://github.com/source-foundry/ttfautohint-build/archive/v${AUTOHINT_SRC_VERSION}.tar.gz \
        "$DEPS_DIR/ttfautohint-build.tar.gz"
      pushd "$DEPS_DIR" >/dev/null
        tar -xzf ttfautohint-build.tar.gz
        rm ttfautohint-build.tar.gz
        rm -rf ttfautohint-build
        mv -f ttfautohint*/ ./ttfautohint-build
        pushd ttfautohint-build >/dev/null
          ./ttfautohint-build.sh
        popd >/dev/null
        mv -f \
          /root/ttfautohint-build/ttfautohint*/frontend/ttfautohint \
          "ttfautohint-${AUTOHINT_VERSION}"
        rm -rf /root/ttfautohint-build ttfautohint-build
      popd >/dev/null
    fi
    LINK=true
  elif [[ ! -f "$VENV_DIR/bin/ttfautohint" ]]; then
    LINK=true
  fi
  if $LINK; then
    ln -vfs ../../deps/ttfautohint-${AUTOHINT_VERSION} "$VENV_DIR/bin/ttfautohint"
  fi

  if [[ ! -f "$VENV_DIR/bin/ttf2woff" ]] || [[ ! -f "$SRCDIR/misc/ttf2woff/ttf2woff" ]]; then
    echo "Building ttf2woff"
    make -C "$SRCDIR/misc/ttf2woff" -j8
  fi
  if [[ ! -f "$VENV_DIR/bin/ttf2woff" ]]; then
    ln -vfs ../../../misc/ttf2woff/ttf2woff "$VENV_DIR/bin"
  fi

  has_newer() {
    DIR=$1
    REF_FILE=$2
    for f in $(find "$DIR" -type f -newer "$REF_FILE" -print -quit); do
      return 0
    done
    return 1
  }

  # ————————————————————————————————————————————————————————————————————————————————————————————————
  # $BUILD_DIR/etc/generated.make

  GEN_MAKE_FILE=$BUILD_DIR/etc/generated.make
  INIT_FILE_HASH= ; if [ -d .git ]; then INIT_FILE_HASH=$(git hash-object -w init.sh); fi
  GENERATE_MAKE_FILE=false
  if $clean || [[ ! -f "$GEN_MAKE_FILE" ]]; then
    GENERATE_MAKE_FILE=true
  else
    # check to see if stored hash of init.sh is the same as the current init.sh
    GEN_MAKE_FILE_LINE1=$(head -n 1 "$GEN_MAKE_FILE")
    if [[ "$GEN_MAKE_FILE_LINE1" != "#$INIT_FILE_HASH" ]]; then
      # the makefile was generated by a different version of init.sh
      GENERATE_MAKE_FILE=true
    fi
  fi

  # Generate BUILD_DIR/etc/generated.make
  if $GENERATE_MAKE_FILE; then

    # Warning about UFOs moving from src to build/ufo
    for f in src/Inter-*.ufo; do
      if [ -f "$f" ]; then
        echo "" >&2
        echo "--------------------------- WARNING ----------------------------" >&2
        echo "" >&2
        echo "     UFO files have moved from ./src to ./build/ufo" >&2
        echo "" >&2
        echo "If you are working with a UFO workflow, please manually move" >&2
        echo "your UFO source files from ./src to ./build/ufo." >&2
        echo "" >&2
        echo "If you are working in a Glyphps workflow, then simply remove" >&2
        echo "the UFO files in ./src to silence this warning." >&2
        echo "" >&2
        echo "----------------------------------------------------------------" >&2
        echo "" >&2
      fi
      break
    done

    echo "Generating '$GEN_MAKE_FILE'"
    echo "#$INIT_FILE_HASH" > "$GEN_MAKE_FILE"
    echo "# Generated by init.sh -- do not modify manually" >> "$GEN_MAKE_FILE"
    echo "" >> "$GEN_MAKE_FILE"

    master_styles=( \
      Thin \
      ThinItalic \
      Regular \
      Italic \
      Black \
      BlackItalic \
    )
    derived_styles=( \
      "Light            : Thin Regular" \
      "LightItalic      : ThinItalic Italic" \
      "ExtraLight       : Thin Regular" \
      "ExtraLightItalic : ThinItalic Italic" \
      "Medium           : Regular Black" \
      "MediumItalic     : Italic BlackItalic" \
      "SemiBold         : Regular Black" \
      "SemiBoldItalic   : Italic BlackItalic" \
      "Bold             : Regular Black" \
      "BoldItalic       : Italic BlackItalic" \
      "ExtraBold        : Regular Black" \
      "ExtraBoldItalic  : Italic BlackItalic" \
    )
    web_formats=( woff woff2 )

    mkdir -p "$BUILD_DIR/etc"

    all_styles=()
    instance_styles=()

    # add master styles to style array
    for style in "${master_styles[@]}"; do
      all_styles+=( $style )
    done

    # master UFO targets
    echo "# master UFOs" >> "$GEN_MAKE_FILE"
    echo "# Note: build/ufo/Inter.designspace depends on src/Inter.glyphs" >> "$GEN_MAKE_FILE"
    echo "# Note: build/ufo/InterDisplay.designspace depends on src/InterDisplay.glyphs" >> "$GEN_MAKE_FILE"
    for style in "${master_styles[@]}"; do
      echo -n "build/ufo/Inter-${style}.ufo:" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/Inter.designspace" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/features" >> "$GEN_MAKE_FILE"
      echo -n " \$(wildcard" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/Inter-${style}.ufo/*.plist" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/Inter-${style}.ufo/*.fea" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/Inter-${style}.ufo/glyphs/*.plist" >> "$GEN_MAKE_FILE"
      echo ")" >> "$GEN_MAKE_FILE"
      echo -e "\t@touch \"\$@\"" >> "$GEN_MAKE_FILE"

      echo -n "build/ufo/InterDisplay-${style}.ufo:" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/InterDisplay.designspace" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/features" >> "$GEN_MAKE_FILE"
      echo -n " \$(wildcard" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/InterDisplay-${style}.ufo/*.plist" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/InterDisplay-${style}.ufo/*.fea" >> "$GEN_MAKE_FILE"
      echo -n " build/ufo/InterDisplay-${style}.ufo/glyphs/*.plist" >> "$GEN_MAKE_FILE"
      echo ")" >> "$GEN_MAKE_FILE"
      echo -e "\t@touch \"\$@\"" >> "$GEN_MAKE_FILE"
    done
    echo -n "all_ufo_masters_text :=" >> "$GEN_MAKE_FILE"
    for style in "${master_styles[@]}"; do
      echo -n " build/ufo/Inter-${style}.ufo" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo -n "all_ufo_masters_display :=" >> "$GEN_MAKE_FILE"
    for style in "${master_styles[@]}"; do
      echo -n " build/ufo/InterDisplay-${style}.ufo" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo "" >> "$GEN_MAKE_FILE"


    # add derived styles to `style` array
    echo "# instance UFOs" >> "$GEN_MAKE_FILE"
    for e in "${derived_styles[@]}"; do
      style=$(echo "${e%%:*}" | xargs)
      dependent_styles=$(echo "${e#*:}" | xargs)
      all_styles+=( $style )
      instance_styles+=( $style )

      echo -n "build/ufo/Inter-${style}.ufo:" >> "$GEN_MAKE_FILE"
      for depstyle in $dependent_styles; do
        echo -n " build/ufo/Inter-${depstyle}.ufo" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"
      echo -e "\tmisc/fontbuild instancegen build/ufo/Inter.designspace ${style}" >> "$GEN_MAKE_FILE"

      echo -n "build/ufo/InterDisplay-${style}.ufo:" >> "$GEN_MAKE_FILE"
      for depstyle in $dependent_styles; do
        echo -n " build/ufo/InterDisplay-${depstyle}.ufo" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"
      echo -e "\tmisc/fontbuild instancegen build/ufo/InterDisplay.designspace ${style}" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"


    # STYLE and STYLE_ttf targets
    for style in "${all_styles[@]}"; do
      echo "${style}: ${style}_otf ${style}_ttf ${style}_ttf_hinted ${style}_web ${style}_web_hinted" >> "$GEN_MAKE_FILE"

      echo "${style}_ttf_hinted: ${DIST_DIR_TOK}const-hinted/Inter-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo "${style}_ttf: ${DIST_DIR_TOK}const/Inter-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo "${style}_otf: ${DIST_DIR_TOK}const/Inter-${style}.otf" >> "$GEN_MAKE_FILE"

      echo -n "${style}_web:" >> "$GEN_MAKE_FILE"
      for format in "${web_formats[@]}"; do
        echo -n " ${DIST_DIR_TOK}const/Inter-${style}.${format}" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"

      echo -n "${style}_web_hinted:" >> "$GEN_MAKE_FILE"
      for format in "${web_formats[@]}"; do
        echo -n " ${DIST_DIR_TOK}const-hinted/Inter-${style}.${format}" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"

      echo "${style}_check: ${DIST_DIR_TOK}const/Inter-${style}.otf ${DIST_DIR_TOK}const/Inter-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo -e "\tmisc/fontbuild checkfont $^" >> "$GEN_MAKE_FILE"


      echo "display_${style}: display_${style}_otf display_${style}_ttf display_${style}_ttf_hinted display_${style}_web display_${style}_web_hinted" >> "$GEN_MAKE_FILE"

      echo "display_${style}_ttf_hinted: ${DIST_DIR_TOK}const-hinted/InterDisplay-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo "display_${style}_ttf: ${DIST_DIR_TOK}const/InterDisplay-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo "display_${style}_otf: ${DIST_DIR_TOK}const/InterDisplay-${style}.otf" >> "$GEN_MAKE_FILE"

      echo -n "display_${style}_web:" >> "$GEN_MAKE_FILE"
      for format in "${web_formats[@]}"; do
        echo -n " ${DIST_DIR_TOK}const/InterDisplay-${style}.${format}" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"

      echo -n "display_${style}_web_hinted:" >> "$GEN_MAKE_FILE"
      for format in "${web_formats[@]}"; do
        echo -n " ${DIST_DIR_TOK}const-hinted/InterDisplay-${style}.${format}" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"

      echo "display_${style}_check: ${DIST_DIR_TOK}const/InterDisplay-${style}.otf ${DIST_DIR_TOK}const/InterDisplay-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo -e "\tmisc/fontbuild checkfont $^" >> "$GEN_MAKE_FILE"


      echo "" >> "$GEN_MAKE_FILE"
    done

    # all_otf_* target
    echo -n "all_otf_text:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_otf" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo -n "all_otf_display:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " display_${style}_otf" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_ttf_* target
    echo -n "all_ttf_text:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_ttf" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo -n "all_ttf_display:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " display_${style}_ttf" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_ttf_*_hinted target
    echo -n "all_ttf_text_hinted:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_ttf_hinted" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo -n "all_ttf_display_hinted:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " display_${style}_ttf_hinted" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_web_* target
    echo -n "all_web_text:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_web" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo -n "all_web_display:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " display_${style}_web" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_web_*_hinted target
    echo -n "all_web_hinted_text:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_web_hinted" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo -n "all_web_hinted_display:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " display_${style}_web_hinted" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # check_all_* target
    echo -n "check_all_text:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_check" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
    echo -n "check_all_display:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " display_${style}_check" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_samples_pdf target
    echo -n "all_samples_pdf:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " \$(FONTDIR)/samples/Inter-${style}.pdf" >> "$GEN_MAKE_FILE"
      echo -n " \$(FONTDIR)/samples/InterDisplay-${style}.pdf" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_samples_png target
    echo -n "all_samples_png:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " \$(FONTDIR)/samples/Inter-${style}.png" >> "$GEN_MAKE_FILE"
      echo -n " \$(FONTDIR)/samples/InterDisplay-${style}.png" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"


    echo -n ".PHONY:" >> "$GEN_MAKE_FILE"
    echo -n " all_otf_text all_otf_display" >> "$GEN_MAKE_FILE"
    echo -n " all_ttf_text all_ttf_display all_ttf_hinted_text all_ttf_hinted_display" >> "$GEN_MAKE_FILE"
    echo -n " all_web_text all_web_display all_web_hinted_text all_web_hinted_display" >> "$GEN_MAKE_FILE"
    echo -n " check_all_text check_all_display" >> "$GEN_MAKE_FILE"
    echo -n " all_samples_pdf all_samples_png" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style} ${style}_ttf ${style}_ttf_hinted ${style}_otf ${style}_check" >> "$GEN_MAKE_FILE"
      echo -n " display_${style} display_${style}_ttf display_${style}_ttf_hinted display_${style}_otf display_${style}_check" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
  fi

  # # ————————————————————————————————————————————————————————————————
  # # summary
  # if ! $VENV_ACTIVE; then
  #   echo -n "You can activate virtualenv by running "
  #   if [ "$0" == "./init.sh" ]; then
  #     # pretty format for common case
  #     echo '`source init.sh`'
  #   else
  #     echo "\`source \"$0\"\`"
  #   fi
  # fi
fi
