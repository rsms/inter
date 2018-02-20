#!/bin/sh
set -e
cd "$(dirname "$0")/.."

if [ ! -s lab/fonts ]; then
  ln -s ../../build/dist lab/fonts
fi

jekyll serve --limit_posts 20 --watch --host 127.0.0.1 --port 3002 --open-url
