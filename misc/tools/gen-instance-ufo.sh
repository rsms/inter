#!/bin/bash
set -e
PROG=${0##*/}
DESIGNSPACE=$1
UFO=$2

INSTANCE_Light="Inter Light"
INSTANCE_ExtraLight="Inter ExtraLight"
INSTANCE_Medium="Inter Medium"
INSTANCE_SemiBold="Inter SemiBold"
INSTANCE_Bold="Inter Bold"
INSTANCE_ExtraBold="Inter ExtraBold"

INSTANCE_LightItalic="Inter Light Italic"
INSTANCE_ExtraLightItalic="Inter ExtraLight Italic"
INSTANCE_MediumItalic="Inter Medium Italic"
INSTANCE_SemiBoldItalic="Inter SemiBold Italic"
INSTANCE_BoldItalic="Inter Bold Italic"
INSTANCE_ExtraBoldItalic="Inter ExtraBold Italic"

INSTANCE_DisplayThin="Inter Display Thin"
INSTANCE_DisplayLight="Inter Display Light"
INSTANCE_DisplayExtraLight="Inter Display ExtraLight"
INSTANCE_DisplayRegular="Inter Display Regular"
INSTANCE_DisplayMedium="Inter Display Medium"
INSTANCE_DisplaySemiBold="Inter Display SemiBold"
INSTANCE_DisplayBold="Inter Display Bold"
INSTANCE_DisplayExtraBold="Inter Display ExtraBold"
INSTANCE_DisplayBlack="Inter Display Black"

INSTANCE_DisplayThinItalic="Inter Display Thin Italic"
INSTANCE_DisplayLightItalic="Inter Display Light Italic"
INSTANCE_DisplayExtraLightItalic="Inter Display ExtraLight Italic"
INSTANCE_DisplayItalic="Inter Display Italic"
INSTANCE_DisplayMediumItalic="Inter Display Medium Italic"
INSTANCE_DisplaySemiBoldItalic="Inter Display SemiBold Italic"
INSTANCE_DisplayBoldItalic="Inter Display Bold Italic"
INSTANCE_DisplayExtraBoldItalic="Inter Display ExtraBold Italic"
INSTANCE_DisplayBlackItalic="Inter Display Black Italic"

MASTER_Thin=1
MASTER_Regular=1
MASTER_Black=1
MASTER_ThinItalic=1
MASTER_Italic=1
MASTER_BlackItalic=1
MASTER_DisplayThin=1
MASTER_Display=1
MASTER_DisplayBlack=1
MASTER_DisplayThinItalic=1
MASTER_DisplayItalic=1
MASTER_DisplayBlackItalic=1

_err() { echo "$PROG: $@" >&2; exit 1; }

# build/ufo/Inter-DisplayExtraBold.ufo -> DisplayExtraBold
UFO_NAME=$(basename "$UFO" .ufo)
case "$UFO_NAME" in
  Inter-*)        UFO_NAME=${UFO_NAME:6} ;;
  InterDisplay-*) UFO_NAME=Display${UFO_NAME:13} ;;
esac

# DisplayExtraBold -> "Inter Display ExtraBold"
INSTANCE=INSTANCE_${UFO_NAME} ; INSTANCE=${!INSTANCE}

# If UFO is not an instance, assume that it's a master (or else error)
# master UFOs are byproducts of building Inter.designspace, so we just update mtime.
if [ -z "$INSTANCE" ]; then
  MASTER=MASTER_${UFO_NAME}
  [ -n "${!MASTER}" ] || _err "Failed to map UFO name \"$UFO_NAME\" to instance"
  [ -d "$UFO" ] || _err "Cannot find master UFO: $UFO"
  echo "touch $UFO"
  touch "$UFO"
  exit
fi

set -x
fontmake -o ufo -m "$DESIGNSPACE" --output-path "$UFO" -i "$INSTANCE"
exec python misc/tools/postprocess_instance_ufo.py "$UFO"
