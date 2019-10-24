#!/bin/bash -e
cd "$(dirname $0)"
# GFDIR=$PWD  # may be useful to save path to the misc/googlefonts-qa directory.
# move to repository root directory
cd ../..

# parse CLI options
CLEAN=false
if [[ "$1" == "-h"* ]] || [[ "$1" == "--h"* ]]; then
  echo "usage: $0 [--clean | --help]"
  echo "--clean   Clean \"from scratch\" build. Clears any previous build products."
  exit
elif [[ "$1" == "--clean" ]]; then
  CLEAN=true ; shift
fi

# make sure that make and venv is up-to-date
./init.sh
source init.sh

# make sure there are no left-over build products
if $CLEAN; then
  make clean >/dev/null
fi

# compile multi-axis variable font
make build/fonts/var/Inter.var.otf

# change file type to TTF and change style names to Google Fonts standard.
rm -rf build/googlefonts
mkdir -p build/googlefonts
misc/fontbuild rename --google-style \
  build/fonts/var/Inter.var.otf \
  -o build/googlefonts/Inter.var.ttf
