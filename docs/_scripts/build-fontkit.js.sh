#!/bin/sh
#
# Usage:
#   sh build-fontkit.js.sh [<outfile>]
# <outfile> defaults to ./fontkit-VERSION.js
#
# This script builds fontkit.js for a web browser as an ES module script.
# Use the result like this:
#   <script type="module">
#   import fontkit from "./fontkit-2.0.2.js"
#   let data = await fetch("InterVariable.ttf").then(r => r.arrayBuffer())
#   let font = fontkit.create(new Uint8Array(data))
#   let instance = font.getVariation({wght: 600, opsz: 32})
#   console.log({font, instance})
#   </script>
#
# We can't use esbuild but have to use parcel since fontkit relies on
# parcel-specific features like executing nodejs fs.readFileSync at build time.
# So first we build with parcel then use esbuild to minify the results.
# There might be ways to streamline the parcel build process, but after 30 minutes
# of reading their documentation I couldn't figure it out, thus the sed hacks.
#
set -e

rm -rf /tmp/fontkit-build
mkdir /tmp/fontkit-build
pushd /tmp/fontkit-build >/dev/null

cat <<EOF > package.json
{ "name": "fontkit-build",
  "version": "1.0.0",
  "dependencies": {
    "buffer": "^6.0.3",
    "fontkit": "^2.0.2",
    "parcel": "^2.9.3",
    "esbuild": "^0.19.2"
  }
}
EOF

npm install

FONTKIT_VERSION=$(node -p 'require("./node_modules/fontkit/package.json").version')

cat <<EOF > index.html
<html lang="en"><script type="module">
window.fontkit = require("fontkit")
</script></html>
EOF

./node_modules/.bin/parcel build --no-optimize --no-cache index.html

# strip away HTML
sed -E 's/^\s*(:?<html lang="en"><script type="module">|<\/script><\/html>\s*\n*\s*)//' dist/index.html > dist/1.js
sed -E 's/window.fontkit =/const fontkit =/' dist/1.js > dist/2.js
echo 'export default fontkit' >> dist/2.js

popd >/dev/null

OUTPUT_FILE=${1:-$(cd "$(dirname "$0")/.." && pwd)/res/fontkit-$FONTKIT_VERSION.js}
/tmp/fontkit-build/node_modules/.bin/esbuild /tmp/fontkit-build/dist/2.js \
  --minify \
  --outfile="$OUTPUT_FILE" \
  --format=esm \
  --platform=browser \
  --target=chrome100

rm -rf /tmp/fontkit-build
