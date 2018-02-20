#!/bin/sh
set -e
cd "$(dirname "$0")/.."

pushd res >/dev/null

for f in *.svg; do
  svgo --multipass -q "$f" &
done

for f in *.png; do
  TMPNAME=.$f.tmp
  (pngcrush -q "$f" "$TMPNAME" && mv -f "$TMPNAME" "$f") &
done

popd >/dev/null


pushd samples/img >/dev/null

for f in *.png; do
  TMPNAME=.$f.tmp
  if (echo "$f" | grep -q 'thumb'); then
    (convert "$f" -flatten -background white -colors 16 "$TMPNAME" && pngcrush -q "$TMPNAME" "$f") &
  else
    (pngcrush -q "$f" "$TMPNAME" && mv -f "$TMPNAME" "$f") &
  fi
done

popd >/dev/null



pushd samples/icons >/dev/null

for f in *.svg; do
  svgo --multipass -q "$f" &
done

popd >/dev/null


wait
