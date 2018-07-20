#!/bin/sh
set -e
cd "$(dirname "$0")/.."

if [ ! -s lab/fonts ]; then
  ln -s ../../build/dist-unhinted lab/fonts
fi

# jekyll is a little dumb and resolves the lab/fonts symlink and copies
# all font files to _site when started. Fix that. Bad jekyll!
#
# Step 1/2: remove any previous symlink, or jekyll crashes
rm -rf _site/lab/fonts
#
# Step 2/2: create symlink again after some delay. Ugh.
sh <<_EOF_ &
N=3
while [ \$N -gt 0 ]; do
  sleep 1
  rm -rf _site/lab/fonts
  ln -s ../../../build/dist-unhinted _site/lab/fonts
  let N=N-1
done
_EOF_

jekyll serve --limit_posts 20 --watch --host 127.0.0.1 --port 3002 --open-url
