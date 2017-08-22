#!/bin/bash
set -e
cd "$(dirname "$0")/.."

# Create if needed
if [[ ! -f build/tmp.sparseimage ]]; then
  echo "Creating sparse disk image with case-sensitive file system build/tmp.sparseimage"
  mkdir -p build
  hdiutil create build/tmp.sparseimage \
    -size 1g \
    -type SPARSE \
    -fs JHFS+X \
    -volname tmp
fi

# Mount if needed
if ! (diskutil info build/tmp >/dev/null); then
  echo "Mounting sparse disk image with case-sensitive file system at build/tmp"
  hdiutil attach build/tmp.sparseimage \
    -readwrite \
    -mountpoint "$(pwd)/build/tmp" \
    -nobrowse \
    -noautoopen \
    -noidmereveal
fi
