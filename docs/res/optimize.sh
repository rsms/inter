#!/bin/sh
set -e
cd "$(dirname "$0")"

for f in *.svg; do
  svgo --multipass -q "$f" &
done

for f in *.png; do
  TMPNAME=.$f.tmp
  (pngcrush -q "$f" "$TMPNAME" && mv -f "$TMPNAME" "$f") &
done

wait
