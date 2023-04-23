#!/bin/bash
set -e
cd "$(dirname "$0")/.."

OPT_HELP=
OPT_REVEAL_IN_FINDER=false
OPT_EXTRAS=false
OUTFILE=

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
  -h|-help|--help)   OPT_HELP=0; shift;;
  -reveal-in-finder) OPT_REVEAL_IN_FINDER=true; shift;;
  -extras|--extras)  OPT_EXTRAS=true; shift;;
  -*)
    echo "$0: Unknown option $1" >&2
    OPT_HELP=1
    shift
    ;;
  *)
    if [[ "$OUTFILE" != "" ]] && ! $OPT_HELP; then
      echo "$0: Extra unexpected argument(s) after <outfile>" >&2
      OPT_HELP=1
    fi
    OUTFILE=$1
    shift
    ;;
  esac
done
if [ -n "$OPT_HELP" ]; then
  echo "Usage: $0 [options] <outfile>"
  echo "Options:"
  echo "  -h, -help          Show help."
  echo "  -reveal-in-finder  After creating the zip file, show it in Finder"
  exit $OPT_HELP
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
rm -rf "$ZIPDIR" build/tmp/a.zip

# create directories
mkdir -p "$(dirname "$OUTFILE_ABS")" "$ZIPDIR"

cp LICENSE.txt "$ZIPDIR/LICENSE.txt"

if $OPT_EXTRAS; then
  mkdir -p "$ZIPDIR/OTF" "$ZIPDIR/TTF"

  cp misc/dist/extras-readme.txt           "$ZIPDIR/README.txt"
  cp build/fonts/static/Inter-*.otf        "$ZIPDIR/OTF/" &
  cp build/fonts/static-hinted/Inter-*.ttf "$ZIPDIR/TTF/" &
else
  mkdir -p "$ZIPDIR/Web"

  cp misc/dist/help.txt                           "$ZIPDIR/help.txt"
  cp build/fonts/static/Inter.ttc                 "$ZIPDIR/Inter.ttc"
  cp build/fonts/static-hinted/Inter-truetype.ttc "$ZIPDIR/Inter TrueType.ttc"
  cp build/fonts/var/InterV.var.ttf               "$ZIPDIR/Inter Variable.ttf"
  cp build/fonts/var/InterV-Italic.var.ttf        "$ZIPDIR/Inter Variable Italic.ttf"

  cp build/fonts/static/Inter-*.woff2 \
     build/fonts/var/Inter.var.woff2 \
     build/fonts/var/Inter-Italic.var.woff2 \
     misc/dist/inter.css                       "$ZIPDIR/Web/" &
fi

mkdir -p "$(dirname "$OUTFILE_ABS")"
wait

pushd "$ZIPDIR" >/dev/null
zip -q -X -r "$OUTFILE_ABS" *
popd >/dev/null
rm -rf "$ZIPDIR"

echo "Created $OUTFILE"
if $OPT_REVEAL_IN_FINDER && [ "$(uname -s)" = Darwin ] && [ -f /usr/bin/open ]; then
  /usr/bin/open --reveal "$OUTFILE"
fi
