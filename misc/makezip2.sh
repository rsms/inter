#!/bin/bash
set -e
cd "$(dirname "$0")/.."

OPT_HELP=false
OPT_REVEAL_IN_FINDER=false
OUTFILE=

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
  -h*|--h*)
    OPT_HELP=true
    shift
    ;;
  -reveal-in-finder)
    OPT_REVEAL_IN_FINDER=true
    shift
    ;;
  -*)
    echo "$0: Unknown option $1" >&2
    OPT_HELP=true
    shift
    ;;
  *)
    if [[ "$OUTFILE" != "" ]] && ! $OPT_HELP; then
      echo "$0: Extra unexpected argument(s) after <outfile>" >&2
      OPT_HELP=true
    fi
    OUTFILE=$1
    shift
    ;;
  esac
done
if $OPT_HELP; then
  echo "Usage: $0 [options] <outfile>"
  echo "Options:"
  echo "  -h, -help          Show help."
  echo "  -reveal-in-finder  After creating the zip file, show it in Finder"
  exit 1
fi

# tmp dir
ZIPDIR=build/tmp/zip
FONTDIR=build/fonts

# convert relative path to absolute if needed
OUTFILE_ABS=$OUTFILE
if [[ "$OUTFILE_ABS" != /* ]]; then
  OUTFILE_ABS=$PWD/$OUTFILE_ABS
fi

# cleanup any previous build
rm -rf "$ZIPDIR"
rm -f  build/tmp/a.zip

# create directories
mkdir -p \
  "$ZIPDIR/Desktop" \
  "$ZIPDIR/Desktop with TrueType hints" \
  "$ZIPDIR/Variable" \
  "$ZIPDIR/Web"

# copy font files
# ----------------------------------------------------------------------------

# Desktop
cp $FONTDIR/static/Inter-*.otf         "$ZIPDIR/Desktop/" &

# Hinted for Windows
cp "misc/dist/about hinted fonts.txt"  "$ZIPDIR/Desktop with TrueType hints/" &
cp $FONTDIR/static-hinted/Inter-*.ttf  "$ZIPDIR/Desktop with TrueType hints/" &

# Variable ("Inter" and "Inter V")
cp $FONTDIR/var/Inter*.var.ttf         "$ZIPDIR/Variable/" &

# Web
cp $FONTDIR/static/Inter-*.woff*       "$ZIPDIR/Web/" &
cp $FONTDIR/var/Inter.var.woff2        "$ZIPDIR/Web/" &
cp $FONTDIR/var/Inter-Italic.var.woff2 "$ZIPDIR/Web/" &
cp misc/dist/inter.css                 "$ZIPDIR/Web/" &

# ----------------------------------------------------------------------------

# copy misc stuff
cp misc/dist/install*.txt        "$ZIPDIR/"
cp LICENSE.txt                   "$ZIPDIR/"
mkdir -p "$(dirname "$OUTFILE_ABS")"

# wait for processes to finish
wait

# zip
pushd "$ZIPDIR" >/dev/null
zip -q -X -r "$OUTFILE_ABS" *
popd >/dev/null
rm -rf "$ZIPDIR"

echo "Created $OUTFILE"
if $OPT_REVEAL_IN_FINDER && [ -f /usr/bin/open ]; then
  /usr/bin/open --reveal "$OUTFILE"
fi
