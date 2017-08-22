#!/bin/bash
set -e
cd "$(dirname "$0")/.."

diskutil unmount build/tmp
