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
    export PYTHONPATH=$SRCDIR_ABS/misc/pylib
  fi
else
  # Subshell
  set -e
  cd "$SRCDIR"

  if [[ "$1" == "-h" ]] || [[ "$1" == "-help" ]] || [[ "$1" == "--help" ]]; then
    echo "usage: $0 [options]" >&2
    echo "options:" >&2
    echo "  -clean  Start from scratch" >&2
    exit 1
  fi

  clean=false
  if [[ "$1" == "-clean" ]]; then
    clean=true
  fi

  # ————————————————————————————————————————————————————————————————————————————————————————————————
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
    # find pip
    export pip=$(which pip2)
    if [ "$pip" = "" ]; then
      export pip=$(which pip)
    fi
    echo "using pip: $pip $(pip --version)"
    if [ "$pip" = "" ]; then
      echo "Pip for Python 2 not found (tried pip and pip2 in PATH)" >&2
      exit 1
    elif ! ($pip --version 2>&1 | grep -q 'ython 2'); then
      echo "Pip for Python 2 not found (found pip for different python version)" >&2
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
    echo "Setting up virtualenv in '$VENV_DIR'"
    rm -f "$VENV_DIR/lib/python"
    require_virtualenv
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

  source "$VENV_DIR/bin/activate"

  UPDATE_TIMESTAMP_FILE="$VENV_DIR/last-pip-run.mark"
  REQUIREMENTS_FILE=$SRCDIR/requirements.txt
  PY_REQUIREMENTS_CHANGED=false

  if [ "$REQUIREMENTS_FILE" -nt "$UPDATE_TIMESTAMP_FILE" ]; then
    echo "pip install -r $REQUIREMENTS_FILE"
    pip install -r "$REQUIREMENTS_FILE"
    date '+%s' > "$UPDATE_TIMESTAMP_FILE"
    PY_REQUIREMENTS_CHANGED=true
  fi

  # ————————————————————————————————————————————————————————————————————————————————————————————————
  # deps
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
      https://github.com/khaledhosny/ots/releases/download/v${OTS_VERSION}/ots-${OTS_VERSION}-osx.zip \
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
  LINK=false
  if [[ ! -f "$DEPS_DIR/ttfautohint-${AUTOHINT_VERSION}" ]]; then
    fetch \
      https://download.savannah.gnu.org/releases/freetype/ttfautohint-${AUTOHINT_VERSION}-tty-osx.tar.gz
      "$DEPS_DIR/ttfautohint.tar.gz"
    tar -C "$DEPS_DIR" -xzf "$DEPS_DIR/ttfautohint.tar.gz"
    rm "$DEPS_DIR/ttfautohint.tar.gz"
    mv -f "$DEPS_DIR/ttfautohint" "$DEPS_DIR/ttfautohint-${AUTOHINT_VERSION}"
    LINK=true
  elif [[ ! -f "$VENV_DIR/bin/ttfautohint" ]]; then
    LINK=true
  fi
  if $LINK; then
    ln -vfs ../../deps/ttfautohint-1.8.2 "$VENV_DIR/bin/ttfautohint"
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
    for f in $(find "$DIR" -type f -name '*.pyx' -newer "$REF_FILE" -print -quit); do
      return 0
    done
    return 1
  }

  # ————————————————————————————————————————————————————————————————————————————————————————————————
  # $BUILD_DIR/etc/generated.make
  master_styles=( \
    Regular \
    Black \
    Italic \
    BlackItalic \
  )
  derived_styles=( \
    "Medium           : Regular Black" \
    "MediumItalic     : Italic BlackItalic" \
    "SemiBold         : Regular Black" \
    "SemiBoldItalic   : Italic BlackItalic" \
    "Bold             : Regular Black" \
    "BoldItalic       : Italic BlackItalic" \
    "ExtraBold        : Regular Black" \
    "ExtraBoldItalic  : Italic BlackItalic" \
  )
  web_formats=( woff woff2 )  # Disabled/unused: eot

  mkdir -p "$BUILD_DIR/etc"
  GEN_MAKE_FILE=$BUILD_DIR/etc/generated.make

  # Only generate if there are changes to the font sources or init.sh
  NEED_GENERATE=false
  if $clean || [[ ! -f "$GEN_MAKE_FILE" ]] || [[ "$0" -nt "$GEN_MAKE_FILE" ]]; then
    NEED_GENERATE=true
  else
    for style in "${master_styles[@]}"; do
      if $NEED_GENERATE; then
        break
      fi
      if has_newer "src/Inter-UI-${style}.ufo" "$GEN_MAKE_FILE"; then
        NEED_GENERATE=true
      fi
    done
  fi

  if $NEED_GENERATE; then
    echo "Generating '$GEN_MAKE_FILE'"
    echo "# Generated by init.sh -- do not modify manually" > "$GEN_MAKE_FILE"

    all_styles=()

    # add master styles to style array
    for style in "${master_styles[@]}"; do
      all_styles+=( $style )
      echo -n "${style}_ufo_d := \$(wildcard" >> "$GEN_MAKE_FILE"
      echo -n " src/Inter-UI-${style}.ufo/*.plist" >> "$GEN_MAKE_FILE"
      echo -n " src/Inter-UI-${style}.ufo/*.fea" >> "$GEN_MAKE_FILE"
      echo -n " src/Inter-UI-${style}.ufo/glyphs/*.plist" >> "$GEN_MAKE_FILE"
      echo -n " src/Inter-UI-${style}.ufo/glyphs/*.glif" >> "$GEN_MAKE_FILE"
      echo ")" >> "$GEN_MAKE_FILE"
    done

    # generate all_ufo: <master_ufos>
    # echo -n "all_ufo:" >> "$GEN_MAKE_FILE"
    # for style in "${master_styles[@]}"; do
    #   echo -n " \$(${style}_ufo_d)" >> "$GEN_MAKE_FILE"
    # done
    # echo "" >> "$GEN_MAKE_FILE"
    
    echo "" >> "$GEN_MAKE_FILE"

    # add derived styles to style array
    for e in "${derived_styles[@]}"; do
      style=$(echo "${e%%:*}" | xargs)
      dependent_styles=$(echo "${e#*:}" | xargs)
      all_styles+=( $style )
    done

    # STYLE and STYLE_ttf targets
    for style in "${all_styles[@]}"; do
      echo "${style}: ${style}_otf ${style}_ttf ${style}_ttf_hinted ${style}_web ${style}_web_hinted" >> "$GEN_MAKE_FILE"

      echo "${style}_ttf_hinted: ${DIST_DIR_TOK}const-hinted/Inter-UI-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo "${style}_ttf: ${DIST_DIR_TOK}const/Inter-UI-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo "${style}_otf: ${DIST_DIR_TOK}const/Inter-UI-${style}.otf" >> "$GEN_MAKE_FILE"

      echo -n "${style}_web:" >> "$GEN_MAKE_FILE"
      for format in "${web_formats[@]}"; do
        echo -n " ${DIST_DIR_TOK}const/Inter-UI-${style}.${format}" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"

      echo -n "${style}_web_hinted:" >> "$GEN_MAKE_FILE"
      for format in "${web_formats[@]}"; do
        echo -n " ${DIST_DIR_TOK}const-hinted/Inter-UI-${style}.${format}" >> "$GEN_MAKE_FILE"
      done
      echo "" >> "$GEN_MAKE_FILE"

      echo "${style}_check: ${DIST_DIR_TOK}const/Inter-UI-${style}.otf ${DIST_DIR_TOK}const/Inter-UI-${style}.ttf" >> "$GEN_MAKE_FILE"
      echo -e "\tmisc/fontbuild checkfont $^" >> "$GEN_MAKE_FILE"

      echo "" >> "$GEN_MAKE_FILE"
    done

    # all_otf target
    echo -n "all_otf:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_otf" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_ttf target
    echo -n "all_ttf:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_ttf" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_ttf_hinted target
    echo -n "all_ttf_hinted:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_ttf_hinted" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_web target
    echo -n "all_web:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_web" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_web_hinted target
    echo -n "all_web_hinted:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_web_hinted" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_check_const target
    echo -n "all_check_const:" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style}_check" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"

    # all_const_fonts target
    # echo -n "all_const_fonts:" >> "$GEN_MAKE_FILE"
    # for style in "${all_styles[@]}"; do
    #   echo -n " ${style}" >> "$GEN_MAKE_FILE"
    # done
    # echo "" >> "$GEN_MAKE_FILE"
    

    echo -n ".PHONY: all_otf all_ttf_hinted all_ttf all_web all_web_hinted all_ufo all_check_const" >> "$GEN_MAKE_FILE"
    for style in "${all_styles[@]}"; do
      echo -n " ${style} ${style}_ttf ${style}_ttf_hinted ${style}_otf ${style}_check" >> "$GEN_MAKE_FILE"
    done
    echo "" >> "$GEN_MAKE_FILE"
  fi

  # ————————————————————————————————————————————————————————————————————————————————————————————————
  # summary
  if ! $VENV_ACTIVE; then
    echo -n "You can activate virtualenv by running "
    if [ "$0" == "./init.sh" ]; then
      # pretty format for common case
      echo '`source init.sh`'
    else
      echo "\`source \"$0\"\`"
    fi
  fi
fi
