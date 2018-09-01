#!/bin/bash -e

function usage() {
  cat 1>&2 <<__END
usage: $0 [options] <font1> <font2>
options:
  -h, --help  Show usage and exit
  Rest of options are forwarded to the "diff" program
__END
}

diffargs=()
file1=
file2=

while [ "$1" != "" ]; do
  PARAM=`echo $1 | awk -F= '{print $1}'`
  VALUE=`echo $1 | awk -F= '{print $2}'`
  case $PARAM in
    -h | -help | --help)
      usage
      exit
      ;;
    -*)
      diffargs[${#diffargs[*]}]=$1
      ;;
    *)
      if [[ "$file1" == "" ]]; then
        file1=$PARAM
      elif [[ "$file2" == "" ]]; then
        file2=$PARAM
      else
        echo "Too many files" 1>&2
        exit 1
      fi
      ;;
  esac
  shift
done

if [[ "$file1" == "" ]] && [[ "$file2" == "" ]]; then
  usage
  exit 1
elif [[ "$file1" == "" ]] || [[ "$file2" == "" ]]; then
  echo "Not enough files" 1>&2
  exit 1
fi

tmpdir=$TMPDIR
if [[ "$tmpdir" == "" ]]; then
  tmpdir=/tmp
fi
tmpdir=$tmpdir/kerndiff-tmp
mkdir -p "$tmpdir"

file1x="$(basename "$file1")"
file2x="$(basename "$file2")"

pushd "$(dirname "$0")" >/dev/null
KERNDIFF_DIR=$PWD
popd >/dev/null

case $file1 in
  *.otf)
    python "$KERNDIFF_DIR/getKerningPairsFromOTF.py" "$file1" \
      > "$tmpdir/$file1x"
    ;;
  *.ufo)
    python "$KERNDIFF_DIR/getKerningPairsFromUFO.py" "$file1" \
      > "$tmpdir/$file1x"
    ;;
  *)
    echo "unsupported file format: $file1"
    exit 1
    ;;
esac

case $file2 in
  *.otf)
    python "$KERNDIFF_DIR/getKerningPairsFromOTF.py" "$file2" \
      > "$tmpdir/$file2x"
    ;;
  *.ufo)
    python "$KERNDIFF_DIR/getKerningPairsFromUFO.py" "$file2" \
      > "$tmpdir/$file2x"
    ;;
  *)
    echo "unsupported file format: $file2"
    exit 1
    ;;
esac

pushd $tmpdir >/dev/null
diff -u "${diffargs[@]}" "$file1x" "$file2x"
popd >/dev/null
rm -rf "$tmpdir"
