#!/bin/bash
set -e
cd "$(dirname "$0")/.."

OPT_HELP=
OPT_REVEAL_IN_FINDER=false
OUTFILE=

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
  -h|-help|--help)   OPT_HELP=0; shift;;
  -reveal-in-finder) OPT_REVEAL_IN_FINDER=true; shift;;
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

# convert relative path to absolute if needed
OUTFILE_ABS=$OUTFILE
if [[ "$OUTFILE_ABS" != /* ]]; then
  OUTFILE_ABS="$PWD/$OUTFILE_ABS"
fi

rm -rf "$ZIPDIR"
mkdir -p "$(dirname "$OUTFILE_ABS")" "$ZIPDIR"

cp LICENSE.txt "$ZIPDIR/LICENSE.txt"


mkdir -p "$ZIPDIR/web"

cp misc/dist/help.txt                         "$ZIPDIR/help.txt"
cp build/fonts/static-hinted/Inter.ttc        "$ZIPDIR/Inter.ttc"
cp build/fonts/var/InterVariable.ttf          "$ZIPDIR/InterVariable.ttf"
cp build/fonts/var/InterVariable-Italic.ttf   "$ZIPDIR/InterVariable-Italic.ttf"
cp build/fonts/static/Inter*.woff2            "$ZIPDIR/web/" &
cp build/fonts/var/InterVariable.woff2        "$ZIPDIR/web/InterVariable.woff2"
cp build/fonts/var/InterVariable-Italic.woff2 "$ZIPDIR/web/InterVariable-Italic.woff2"
cp misc/dist/inter.css                         "$ZIPDIR/web/"

. build/venv/bin/activate
python misc/tools/patch-version.py "$ZIPDIR/web/inter.css"

mkdir -p "$ZIPDIR/extras/otf" \
         "$ZIPDIR/extras/ttf" \
         "$ZIPDIR/extras/woff-hinted"

cp build/fonts/static/Inter*.otf          "$ZIPDIR/extras/otf/" &
cp build/fonts/static-hinted/Inter*.ttf   "$ZIPDIR/extras/ttf/" &
cp build/fonts/static-hinted/Inter*.woff2 "$ZIPDIR/extras/woff-hinted/" &



mkdir -p "$(dirname "$OUTFILE_ABS")"
wait

rm -rf "$OUTFILE_ABS"
pushd "$ZIPDIR" >/dev/null
zip -q -X -r "$OUTFILE_ABS" *
popd >/dev/null
rm -rf "$ZIPDIR"

echo "Created $OUTFILE"
if $OPT_REVEAL_IN_FINDER && [ "$(uname -s)" = Darwin ] && [ -f /usr/bin/open ]; then
  /usr/bin/open --reveal "$OUTFILE"
fi
