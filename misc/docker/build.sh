#!/bin/bash -e
#
# Builds the docker image
#

cd "$(dirname "$0")"
DOCKER_DIR=$(pwd)
cd ../..
ROOT_DIR=$(pwd)

IMAGE_NAME=rsms/inter-build
BUILD_DIR=$ROOT_DIR/build/docker

# setup build dir
mkdir -p "$BUILD_DIR/misc/tools" "$BUILD_DIR/misc/fontbuildlib"

# copy files to build dir
echo "Syncing build dir"
cp -a \
  init.sh \
  requirements.txt \
  "$DOCKER_DIR/Dockerfile" \
  "$BUILD_DIR/"
# rsync -v -acC --delete --filter="- *.pyc" --filter="- /*/" \
#   "misc/tools/" \
#   "$BUILD_DIR/misc/tools/" &
# rsync -v -acC --delete --filter="- *.pyc" --filter="- /*/" \
#   "misc/fontbuildlib/" \
#   "$BUILD_DIR/misc/fontbuildlib/" &
# rsync -v -acC --delete \
#   misc/fontbuild \
#   misc/ttf2woff \
#   "$BUILD_DIR/misc/"
wait

# update githash.txt
git rev-parse --short HEAD > githash.txt

pushd "$BUILD_DIR" >/dev/null

# build the image
echo "Building image. This might take a while..."
# docker build -f Dockerfile -t $IMAGE_NAME --squash .
docker build -f Dockerfile -t $IMAGE_NAME .

echo "You can push the image to Docker hub:"
echo "  docker push $IMAGE_NAME:latest"
echo ""
echo "Run interactively:"
echo "  docker run --rm -it -v \"$ROOT_DIR:/host\" $IMAGE_NAME:latest"
