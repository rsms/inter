#!/bin/sh
set -e
cd "$(dirname "$0")/.."

if [ "$1" == "-h" ]; then
  echo "usage: $0 [<bindaddr>]" >&2
  exit 1
fi

if [ ! -s lab/fonts ]; then
  rm -f lab/fonts
  ln -fs ../../build/fonts lab/fonts
fi

# need to delete generated content so that jekyll, being a little dumb,
# can manage to copy the font files into there again.
# Why not a symlink you ask? Jekyll traverses it and copies the content.
# In the past we tried to work around this by periodically removing the
# copied font files and re-creating the symlink, but it was a frail process.
# For live testing with fonts, you'll instead want to use docs/lab/serve.py
rm -rf _site

BINDADDR=127.0.0.1
if [ "$1" != "" ]; then
  BINDADDR=$1
fi

# --incremental

jekyll serve \
  --watch \
  --host "$BINDADDR" \
  --port 3002 \
  --livereload \
  --livereload-port 30002
