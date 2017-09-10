#!/usr/bin/env python
# encoding: utf8
from __future__ import print_function
import os, sys, json, urllib2

f = urllib2.urlopen('https://api.github.com/repos/rsms/interface/releases')
releases = json.load(f)

countTotal = 0

for release in releases:
  count = release['assets'][0]['download_count']
  countTotal += count
  print('%s: %d' % (release['tag_name'], count))

print('Total: %d' % countTotal)
