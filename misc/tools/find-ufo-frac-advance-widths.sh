#!/bin/bash
#
# This script finds UFO glyphs with fractional advance width, which is invalid.
# See https://github.com/rsms/inter/issues/508
#
cd "$(dirname "$0")"/../../build/ufo
ADVANCES=$(rg 'advance width'|awk 'BEGIN {FS="  "} {print $2}')
NOTREALLYFLOATS=$((rg '\.0\b'|wc -l) <<< "$ADVANCES")
FLOATS=$((rg '\.\d+'|wc -l) <<< "$ADVANCES")
INTS=$((rg -v '\.'|wc -l) <<< "$ADVANCES")

printf "Total: $((INTS+FLOATS)) (sanity: $(wc -l <<< "$ADVANCES"))\nFloats: $((FLOATS-NOTREALLYFLOATS))\nInts: $((INTS+NOTREALLYFLOATS))\n"

echo "Occurance Fraction"
(rg -o '\.\d{1,12}'|sort|uniq -c) <<< "$ADVANCES"
