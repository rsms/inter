#!/bin/sh
set -e
cd "$(dirname "$0")/.."

if [ ! -s lab/fonts ]; then
  rm -rf lab/fonts
  ln -fs ../../build/fonts lab/fonts
fi

rm -rf _site

# jekyll is a little dumb and resolves the lab/fonts symlink and copies
# all font files to _site when started. Bad jekyll.
# Let's work around that.
sh <<_EOF_ &
N=3
while [ \$N -gt 0 ]; do
  sleep 1
  mkdir -p _site/lab
  ln -fs ../../../build/fonts _site/lab/fonts
  sleep 5
  if [ -d _site/lab/fonts ]; then
    rm -rf _site/lab/fonts
  else
    rm -f _site/lab/fonts
  fi
  mkdir -p _site/lab
  ln -fs ../../../build/fonts _site/lab/fonts
  let N=N-1
done
_EOF_

jekyll serve --limit_posts 20 --watch --host 127.0.0.1 --port 3002 --open-url
