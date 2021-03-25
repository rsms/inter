#!/usr/bin/env python
# encoding: utf8
#
# Formats a Python profile dump from for example `fontbuild --profile=file ...`
#
import argparse, pstats
from pstats import SortKey

def main():
  argparser = argparse.ArgumentParser(description='Formats a Python profile dump')
  argparser.add_argument('infile', metavar='<file>', type=str, help='Python pstats file')
  argparser.add_argument('-n', '--limit', metavar='N', default=None, type=int,
                         help='Only print the top N entries')
  argparser.add_argument('--sort', metavar='<key>', default=['time'], nargs='+', type=str,
                         help='Sort by keys (default is time.) Available keys: ' + ', '.join(SortKey))
  args = argparser.parse_args()
  p = pstats.Stats(args.infile)
  p.strip_dirs()
  p.sort_stats(SortKey(*args.sort))
  p.print_stats(args.limit)


if __name__ == '__main__':
  main()
