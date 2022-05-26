#!/bin/bash -e
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
  "$ZIPDIR/Inter Desktop" \
  "$ZIPDIR/Inter Hinted for Windows/Desktop" \
  "$ZIPDIR/Inter Hinted for Windows/Web" \
  "$ZIPDIR/Inter Variable" \
  "$ZIPDIR/Inter Variable/Single axis" \
  "$ZIPDIR/Inter Web"

# copy font files
# ----------------------------------------------------------------------------

# Inter Desktop
cp $FONTDIR/static/Inter-*.otf  "$ZIPDIR/Inter Desktop/" &
cp $FONTDIR/var/Inter-V.var.ttf "$ZIPDIR/Inter Desktop/Inter-V.ttf" &

# Inter Hinted for Windows
cp "misc/dist/about hinted fonts.txt"   "$ZIPDIR/Inter Hinted for Windows/" &
cp $FONTDIR/static-hinted/Inter-*.ttf   "$ZIPDIR/Inter Hinted for Windows/Desktop/" &
cp $FONTDIR/static-hinted/Inter-*.woff* "$ZIPDIR/Inter Hinted for Windows/Web/" &
cp misc/dist/inter.css                  "$ZIPDIR/Inter Hinted for Windows/Web/" &

# Inter Variable
cp $FONTDIR/var/Inter.var.ttf \
  "$ZIPDIR/Inter Variable/Inter.ttf" &
cp $FONTDIR/var/Inter-roman.var.ttf \
  "$ZIPDIR/Inter Variable/Single axis/Inter-roman.ttf" &
cp $FONTDIR/var/Inter-italic.var.ttf \
  "$ZIPDIR/Inter Variable/Single axis/Inter-italic.ttf" &

# Inter Web
cp $FONTDIR/static/Inter-*.woff*       "$ZIPDIR/Inter Web/" &
cp $FONTDIR/var/Inter.var.woff2        "$ZIPDIR/Inter Web/" &
cp $FONTDIR/var/Inter-roman.var.woff2  "$ZIPDIR/Inter Web/" &
cp $FONTDIR/var/Inter-italic.var.woff2 "$ZIPDIR/Inter Web/" &
cp misc/dist/inter.css                 "$ZIPDIR/Inter Web/" &
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
