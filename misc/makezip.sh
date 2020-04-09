#!/bin/bash -e
cd "$(dirname "$0")/.."

OPT_HELP=false
OPT_TEXT=false
OPT_DISPLAY=false
OPT_REVEAL_IN_FINDER=false
OUTFILE=

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
  -h*|--h*)
    OPT_HELP=true
    shift
    ;;
  -text|--text)
    OPT_TEXT=true
    shift
    ;;
  -display|--display)
    OPT_DISPLAY=true
    shift
    ;;
  -a*|--a*)
    OPT_TEXT=true
    OPT_DISPLAY=true
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
if (! $OPT_TEXT && ! $OPT_DISPLAY); then
  OPT_HELP=true
  echo "$0: Need at least one of: -all, -display, -text" >&2
fi
if $OPT_HELP; then
  echo "Usage: $0 [options] <outfile>"
  echo "Options:"
  echo "  -h, -help          Show help."
  echo "  -text              Include Inter Text"
  echo "  -display           Include Inter Display"
  echo "  -a, -all           Include all fonts"
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
if $OPT_TEXT; then
  # Inter Desktop
  cp $FONTDIR/const/Inter-*.otf          "$ZIPDIR/Inter Desktop/" &
  cp $FONTDIR/var/Inter-V.var.otf        "$ZIPDIR/Inter Desktop/Inter-V.otf" &

  # Inter Hinted for Windows
  cp "misc/dist/about hinted fonts.txt"  "$ZIPDIR/Inter Hinted for Windows/" &
  cp $FONTDIR/const-hinted/Inter-*.ttf   "$ZIPDIR/Inter Hinted for Windows/Desktop/" &
  cp $FONTDIR/const-hinted/Inter-*.woff* "$ZIPDIR/Inter Hinted for Windows/Web/" &
  cp misc/dist/inter.css                 "$ZIPDIR/Inter Hinted for Windows/Web/" &

  # Inter Variable
  cp $FONTDIR/var/Inter.var.otf          "$ZIPDIR/Inter Variable/Inter.otf" &
  cp $FONTDIR/var/Inter-roman.var.otf    "$ZIPDIR/Inter Variable/Single axis/Inter-roman.otf" &
  cp $FONTDIR/var/Inter-italic.var.otf   "$ZIPDIR/Inter Variable/Single axis/Inter-italic.otf" &

  # Inter Web
  cp $FONTDIR/const/Inter-*.woff*        "$ZIPDIR/Inter Web/" &
  cp $FONTDIR/var/Inter.var.woff2        "$ZIPDIR/Inter Web/" &
  cp $FONTDIR/var/Inter-roman.var.woff2  "$ZIPDIR/Inter Web/" &
  cp $FONTDIR/var/Inter-italic.var.woff2 "$ZIPDIR/Inter Web/" &
  cp misc/dist/inter.css                 "$ZIPDIR/Inter Web/" &
fi
# ----------------------------------------------------------------------------
if $OPT_DISPLAY; then
  # Inter Desktop
  cp $FONTDIR/const/InterDisplay-*.otf          "$ZIPDIR/Inter Desktop/" &
  cp $FONTDIR/var/InterDisplay-V.var.otf        "$ZIPDIR/Inter Desktop/InterDisplay-V.otf" &

  # Inter Hinted for Windows
  cp "misc/dist/about hinted fonts.txt"         "$ZIPDIR/Inter Hinted for Windows/" &
  cp $FONTDIR/const-hinted/InterDisplay-*.ttf   "$ZIPDIR/Inter Hinted for Windows/Desktop/" &
  cp $FONTDIR/const-hinted/InterDisplay-*.woff* "$ZIPDIR/Inter Hinted for Windows/Web/" &
  cp misc/dist/inter-display.css                "$ZIPDIR/Inter Hinted for Windows/Web/" &

  # Inter Variable
  cp $FONTDIR/var/InterDisplay.var.otf          "$ZIPDIR/Inter Variable/InterDisplay.otf" &
  cp $FONTDIR/var/InterDisplay-roman.var.otf    "$ZIPDIR/Inter Variable/Single axis/InterDisplay-roman.otf" &
  cp $FONTDIR/var/InterDisplay-italic.var.otf   "$ZIPDIR/Inter Variable/Single axis/InterDisplay-italic.otf" &

  # Inter Web
  cp $FONTDIR/const/InterDisplay-*.woff*        "$ZIPDIR/Inter Web/" &
  cp $FONTDIR/var/InterDisplay.var.woff2        "$ZIPDIR/Inter Web/" &
  cp $FONTDIR/var/InterDisplay-roman.var.woff2  "$ZIPDIR/Inter Web/" &
  cp $FONTDIR/var/InterDisplay-italic.var.woff2 "$ZIPDIR/Inter Web/" &
  cp misc/dist/inter-display.css                "$ZIPDIR/Inter Web/" &
fi
# ----------------------------------------------------------------------------

# copy misc stuff
cp misc/dist/install*.txt        "$ZIPDIR/"
cp LICENSE.txt                   "$ZIPDIR/"

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
