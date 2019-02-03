#!/bin/sh
set -e
cd "$(dirname "$0")/.."

if ! (which svgo >/dev/null); then
  echo 'svgo not found in $PATH (try `brew install svgo` on mac)' >&2
  exit 1
fi

if ! (which pngcrush >/dev/null); then
  echo 'pngcrush not found in $PATH (try `brew install pngcrush` on mac)' >&2
  exit 1
fi

if ! (which convert >/dev/null); then
  echo 'convert not found in $PATH (try `brew install imagemagick` on mac)' >&2
  exit 1
fi

pushd res >/dev/null

# crunch /docs/res/*.svg
for f in *.svg; do
  svgo --multipass -q "$f" &
done

# crunch /docs/res/*.png
for f in *.png; do
  TMPNAME=.$f.tmp
  (pngcrush -q "$f" "$TMPNAME" && mv -f "$TMPNAME" "$f") &
done

popd >/dev/null


pushd samples/img >/dev/null

# crunch /docs/samples/img/*.png
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

# crunch /docs/samples/icons/*.svg
for f in *.svg; do
  svgo --multipass -q "$f" &
done

popd >/dev/null

# wait for all background processes to exit
wait
